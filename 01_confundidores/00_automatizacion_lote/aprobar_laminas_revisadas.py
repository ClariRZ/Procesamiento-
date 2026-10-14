#!/usr/bin/env python3
"""Registra SOLO la aprobación humana de 71 láminas previamente revisadas.

No inspecciona ni aprueba imágenes por sí mismo; exige confirmación explícita.
No genera máscaras, confusores ni ejecuta FEAT. Usa la acción 'approve'
existente para que cada run tenga su manifiesto individual.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

EXPECTED = 71
CONFIRM = 'REVISE_LAS_71_LAMINAS'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda: file.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-root', type=Path,
                        default=Path.home() / 'TesisDoctoral/confounds_nativos')
    parser.add_argument('--laminas', type=Path,
                        default=Path.home() / 'TesisDoctoral/QC_LAMINAS_CONFUNDS_20261014')
    parser.add_argument('--observer', default='Investigadora principal')
    parser.add_argument('--confirm', default='',
                        help='Requiere confirmación literal de la revisión humana')
    parser.add_argument('--execute', action='store_true',
                        help='Si falta, solo muestra un plan y no escribe')
    args = parser.parse_args()
    script = Path(__file__).resolve().with_name('automatizar_confounds_nativos.py')
    require(script.is_file(), 'FALTA automatizar_confounds_nativos.py junto al aprobador')
    require(args.observer.strip(), 'Debe indicarse observador')
    require(args.laminas.is_dir(), 'FALTA la carpeta de láminas')
    require((args.laminas / 'index.html').is_file(), 'FALTA index.html')
    report = args.laminas / 'resultado_qc_visual.tsv'
    require(report.is_file(), 'FALTA resultado_qc_visual.tsv')

    with report.open(newline='', encoding='utf-8') as file:
        data = list(csv.DictReader(file, delimiter='\t'))
    require(len(data) == EXPECTED,
            f'Se esperaban {EXPECTED} láminas, el índice tiene {len(data)}')
    require(all({'id', 'run', 'estado', 'detalle'} <= row.keys() for row in data),
            'CABECERA_DEL_INDICE_INVALIDA')

    expected_keys = set()
    ready = []
    previously = 0
    for row in data:
        sid, run = row['id'], row['run']
        key = (sid, run)
        require(re.fullmatch(r'\d{4}', sid) and run in ('run1', 'run2'),
                f'ID_O_RUN_INVALIDO: {key}')
        require(key not in expected_keys, f'DUPLICADO_EN_LAMINAS: {key}')
        expected_keys.add(key)
        require(key != ('6037', 'run1') and key != ('6037','run2'),
                f'RUN_PILOTO_NO_DEBE_ESTAREN_LOTE: {key}')
        require(row['estado'] == 'PENDIENTE_INSPECCION_HUMANA',
                f'LÁMINA_NO_GENERADA_SATISFACTORIAMENTE: {key}')
        filename = f'{sid}_{run}_mascaras.png'
        require(row['detalle'] == filename,
                f'NOMBRE_LAMINA_INESPERADO: {key}')
        image = args.laminas / filename
        require(image.is_file() and image.stat().st_size > 0,
                f'FALTA_IMAGEN_VISUAL: {image}')
        folder = args.native_root / sid / run
        prep = folder/'prepare.json'
        require(prep.is_file() and not prep.is_symlink(),
                f'FALTA_PREPARE_O_SYMLINK: {key}')
        manifest = json.loads(prep.read_text(encoding='utf-8'))
        require(manifest.get('sujeto') == sid and manifest.get('run') == run,
                f'PREPARE_CORRESPONDE_A_OTRO_RUN: {key}')
        fingerprints = manifest.get('sha256_mascaras', {})
        for tissue in ('wm','csf'):
            name = f'mask_{tissue}_func.nii.gz'
            path = folder / name
            require(path.is_file() and not path.is_symlink(),
                    f'MASCARA_FALTANTE_O_SYMLINK: {key}, {name}')
            require(fingerprints.get(name) == sha256(path),
                    f'MASCARA_CAMBIADA_TRAS_PREPARE: {key}, {name}')
        approved = folder / 'aprobacion_visual.json'
        if approved.exists() or approved.is_symlink():
            require(approved.is_file() and not approved.is_symlink(),
                    f'APROBACION_EXISTENTE_INVALIDA: {key}')
            record = json.loads(approved.read_text(encoding='utf-8'))
            require(record.get('aprobado') is True and
                    record.get('sha256_mascaras_aprobadas') == fingerprints,
                    f'APROBACION_EXISTENTE_NO_COINCIDE: {key}')
            previously += 1
        else:
            for output in ('todos_confounds_nativo.txt', 'finalize.json'):
                target = folder/output
                require(not target.exists() and not target.is_symlink(),
                        f'SALIDA_FINAL_SIN_APROBACION: {key}')
            ready.append(key)

    all_prepared = set()
    for folder in args.native_root.glob('[0-9][0-9][0-9][0-9]/run[12]/prepare.json'):
        parts = folder.relative_to(args.native_root).parts
        key = (parts[0], parts[1])
        if key not in {('6037','run2')}:
            all_prepared.add(key)
    require(all_prepared == expected_keys,
            'LAS_71_LAMINAS_NO_COINCIDEN_CON_EL_CONJUNTO_PREPARADO '
            f'(faltan={sorted(all_prepared - expected_keys)}, '
            f'extra={sorted(expected_keys - all_prepared)})')

    print(f'PRECHECK_OK laminas={len(data)} ya_aprobadas={previously} por_aprobar={len(ready)}', flush=True)
    print('Alcance: revisión visual humana de las láminas de 5 cortes por run.',flush=True)
    if not args.execute:
        print('SOLO PLAN: NO SE ESCRIBIÓ NINGUNA APROBACIÓN.',flush=True)
        return
    require(args.confirm == CONFIRM,
            f'Confirmación requerida: --confirm {CONFIRM}')
    for sid, run in ready:
        subprocess.run([
            sys.executable, str(script), 'approve', '--id',sid,'--run',run,
            '--observer',args.observer,
            '--confirm','HE_REVISADO_AMBAS_MASCARAS',
        ], check=True)
    print(f'APROBACIONES_OK total={len(data)} nuevas={len(ready)} previas={previously}',flush=True)
    print('NO SE CREARON CONFOUNDS. SIGUIENTE ETAPA: finalize-all --execute.',flush=True)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'DETENIDO: {exc}', file=sys.stderr)
        sys.exit(1)
