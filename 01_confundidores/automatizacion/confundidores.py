#!/usr/bin/env python3
"""Confusores nativos WM/CSF + 12 movimientos; ejecución por sujeto/run.

No escribe nunca en el FEAT de origen. No aplica normalización al BOLD.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import numpy as np

# Runs previamente identificados como pendientes/incidentes: no iniciar nuevos datos
# sin una decisión explícita registrada. 6037 no figura en esta lista.
PENDIENTES_QC = {'5017/1', '6010/2', '6032/2', '5031/1', '6025/1', '6025/2'}


def fail(msg: str):
    raise ValueError(msg)


def require(test, msg: str):
    if not test:
        fail(msg)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def nifti(path: Path):
    try:
        import nibabel as nib
    except ImportError as e:
        raise RuntimeError('Falta nibabel. Usar Python de FSL o instalar numpy/nibabel.') from e
    require(path.is_file(), f'Falta imagen: {path}')
    return nib.load(str(path))


def same_grid(one, other, label=''):
    require(one.shape[:3] == other.shape[:3], f'Grilla distinta (dimensiones): {label}')
    require(np.allclose(one.affine, other.affine, rtol=0, atol=1e-4),
            f'Grilla distinta (afín): {label}')


def load_table(path: Path, cols: int, rows: int):
    require(path.is_file(), f'Falta tabla: {path}')
    a = np.loadtxt(path, ndmin=2)
    require(a.ndim == 2 and a.shape == (rows, cols),
            f'Tabla {path.name}: {a.shape}, esperado {(rows, cols)}')
    require(np.isfinite(a).all(), f'Tabla no finita: {path}')
    return a


def check_mask_file(path: Path, bold, brain_mask, tissue: str):
    image = nifti(path)
    same_grid(image, bold, str(path))
    values = np.asanyarray(image.dataobj)
    require(np.isfinite(values).all(), f'Máscara {tissue}: contiene NaN/Inf')
    require(np.isin(np.unique(values), [0, 1]).all(),
            f'Máscara {tissue}: no es binaria')
    selected = values == 1
    brain = np.asanyarray(brain_mask.dataobj)
    require(np.isfinite(brain).all(), 'Máscara funcional con NaN/Inf')
    brain_bool = brain > 0.5
    count = int(selected.sum())
    brain_count = int(brain_bool.sum())
    require(brain_count < brain.size * 0.80,
            'La máscara de origen ocupa más del 80% del FOV: DETENER por posible máscara inflada')
    require(brain_count > 0 and count > 0, f'Máscara {tissue}: vacía')
    require(not np.any(selected & ~brain_bool),
            f'Máscara {tissue}: contiene vóxeles fuera de máscara funcional')
    fraction = count / brain_count
    # Barreras de seguridad, no umbrales para aprobación automática de QC anatómico.
    limit = 0.80 if tissue == 'wm' else 0.50
    require(fraction < limit,
            f'Máscara {tissue} sospechosamente grande ({fraction:.1%} del cerebro); DETENER y revisar')
    return {'voxeles': count, 'voxeles_funcionales': brain_count,
            'fraccion_cerebro': round(fraction, 6)}


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def json_new(path: Path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def run_command(*parts):
    env = dict(os.environ, FSLOUTPUTTYPE='NIFTI_GZ')
    print('FSL:', ' '.join(str(x) for x in parts), flush=True)
    subprocess.run([str(p) for p in parts], check=True, env=env)


def ctx(args):
    require(args.sujeto.isdigit() and len(args.sujeto) == 4,
            'Sujeto debe ser código de cuatro dígitos')
    require(args.run in (1, 2), 'run debe ser 1 o 2')
    home = Path.home()
    default_feat = home / 'Escritorio' / args.sujeto / f'run{args.run}.feat'
    pre = (Path(args.feat) if args.feat else default_feat).expanduser().resolve()
    work_base = Path(args.trabajo).expanduser().resolve()
    out = work_base / args.sujeto / f'run{args.run}' / '01_confundidores'
    require(pre.is_dir(), f'FEAT no existe: {pre}')
    if args.accion in ('mascaras', 'aprobar', 'finalizar'):
        require(f'{args.sujeto}/{args.run}' not in PENDIENTES_QC,
                'Run marcado como pendiente en historial: requiere decisión humana antes de procesar')
    require(pre not in out.parents and out != pre,
            'Trabajo NO puede estar dentro de FEAT de origen')
    require(out not in pre.parents, 'Trabajo no puede contener FEAT de origen')
    return pre, out


def source_files(pre):
    return {
        'bold': pre / 'filtered_func_data.nii.gz',
        'func_ref': pre / 'example_func.nii.gz',
        'func_mask': pre / 'mask.nii.gz',
        't1': pre / 'reg/highres.nii.gz',
        't1_to_func': pre / 'reg/highres2example_func.mat',
        'motion': pre / 'mc/prefiltered_func_data_mcf.par',
    }


def input_audit(pre):
    files = source_files(pre)
    for k, path in files.items():
        require(path.is_file() and path.stat().st_size > 0, f'Falta {k}: {path}')
    b = nifti(files['bold'])
    require(len(b.shape) == 4 and b.shape[3] > 2, 'BOLD debe ser 4D')
    fr, mask, t1 = (nifti(files[k]) for k in ('func_ref', 'func_mask', 't1'))
    require(len(fr.shape) == len(mask.shape) == len(t1.shape) == 3,
            'Referencias/máscaras deben ser 3D')
    same_grid(fr, b, 'example_func vs BOLD')
    same_grid(mask, b, 'mask vs BOLD')
    n = b.shape[3]
    zoom = b.header.get_zooms()
    require(len(zoom) > 3 and zoom[3] > 0, 'TR inválido')
    require(b.header.get_xyzt_units()[1] == 'sec',
            'Unidad temporal del BOLD desconocida/no expresada en segundos; revisar cabecera')
    move = load_table(files['motion'], 6, n)
    mat = np.loadtxt(files['t1_to_func'])
    require(mat.shape == (4, 4) and np.isfinite(mat).all(), 'Matriz de registro inválida')
    require(abs(np.linalg.det(mat)) > 1e-9, 'Matriz de registro singular')
    brain = np.asanyarray(mask.dataobj)
    require(np.isfinite(brain).all() and 0 < np.count_nonzero(brain > .5) < brain.size * .80,
            'Máscara funcional vacía o potencialmente inflada (>80% del FOV)')
    return files, b, mask, {'volumenes': int(n), 'tr_cabecera': float(zoom[3]),
                             'voxeles_mascara_funcional': int(np.count_nonzero(brain > .5)),
                             'filas_movimiento': int(move.shape[0])}


def audit(args):
    pre, out = ctx(args)
    files, _, _, info = input_audit(pre)
    print(json.dumps({'accion': 'AUDITORIA_SOLO_LECTURA', 'preprocesado': str(pre),
                      'destino_fuera_de_FEAT': str(out), 'datos': info,
                      'entradas': {k: str(v) for k, v in files.items()},
                      'revision_anatomica': 'NO CERTIFICADA'}, indent=2, ensure_ascii=False))


def require_programs(*names):
    for name in names:
        require(shutil.which(name), f'Falta programa FSL en PATH: {name}')


def create_masks(args):
    pre, out = ctx(args)
    files, bold, mask, info = input_audit(pre)
    require_programs('fast', 'fslmaths', 'flirt')
    dest = out / 'mascaras'
    require(not dest.exists(), f'Ya existen máscaras; no sobrescribir: {dest}')
    out.mkdir(parents=True, exist_ok=True)
    temp = out / ('.mascaras_en_preparacion_' + uuid.uuid4().hex[:12])
    temp.mkdir()
    try:
        fast_prefix = temp / 'fast' / 'fast'
        fast_prefix.parent.mkdir()
        run_command('fast', '-t', '1', '-n', '3', '-o', fast_prefix, files['t1'])
        for tissue, class_ in [('wm', '2'), ('csf', '0')]:
            pve = Path(str(fast_prefix) + f'_pve_{class_}.nii.gz')
            require(pve.is_file(), f'FAST no creó {pve}')
            mask_t1 = temp / f'mask_{tissue}_T1.nii.gz'
            mask_warp = temp / f'mask_{tissue}_func_sin_recorte.nii.gz'
            final = temp / f'mask_{tissue}_func.nii.gz'
            run_command('fslmaths', pve, '-thr', '0.9', '-bin', mask_t1)
            run_command('flirt', '-in', mask_t1, '-ref', files['func_ref'],
                        '-applyxfm', '-init', files['t1_to_func'],
                        '-interp', 'nearestneighbour', '-out', mask_warp)
            run_command('fslmaths', mask_warp, '-bin', '-mas', files['func_mask'], final)
        m_wm = temp / 'mask_wm_func.nii.gz'
        m_csf = temp / 'mask_csf_func.nii.gz'
        qc_wm = check_mask_file(m_wm, bold, mask, 'wm')
        qc_csf = check_mask_file(m_csf, bold, mask, 'csf')
        require(not np.any((np.asanyarray(nifti(m_wm).dataobj) > 0) &
                           (np.asanyarray(nifti(m_csf).dataobj) > 0)),
                'Las máscaras WM/CSF se superponen. Revisar registro.')
        prov = {'metodo': 'Mirta FAST T1 pve_0/2 0.9, adaptación nativa FLIRT T1->EPI NN',
                'normalizacion_bold_mni': False, 'fecha_utc': utc(),
                'datos': info, 'inputs': {k: {'path': str(v), 'sha256': digest(v)}
                                          for k, v in files.items()},
                'qc_numerico': {'wm': qc_wm, 'csf': qc_csf},
                'qc_visual': 'PENDIENTE',
                'mascaras_sha256': {'wm': digest(m_wm), 'csf': digest(m_csf)}}
        json_new(temp / 'procedencia.json', prov)
        temp.rename(dest)
    except Exception:
        print(f'PREPARACION INCOMPLETA: conservar para diagnosticar: {temp}', file=sys.stderr)
        raise
    print('MASCARAS_PREPARADAS, QC VISUAL PENDIENTE')
    print('WM: ', dest / 'mask_wm_func.nii.gz')
    print('CSF:', dest / 'mask_csf_func.nii.gz')
    print('Abrirlas con FSLeyes sobre example_func y revisar T1->funcional.')


def verify_masks(pre, out):
    files, bold, functional_mask, info = input_audit(pre)
    masks = out / 'mascaras'
    prov = json.loads((masks / 'procedencia.json').read_text())
    require(prov['qc_visual'] == 'PENDIENTE', 'Procedencia inesperada')
    for k, entry in prov['inputs'].items():
        require(str(files[k]) == entry['path'] and digest(files[k]) == entry['sha256'],
                f'Cambiaron las entradas: {k}')
    stats = {}
    for tissue in ('wm', 'csf'):
        filename = masks / f'mask_{tissue}_func.nii.gz'
        require(digest(filename) == prov['mascaras_sha256'][tissue],
                f'Cambio máscara {tissue}')
        stats[tissue] = check_mask_file(filename, bold, functional_mask, tissue)
    require(not np.any((np.asanyarray(nifti(masks/'mask_wm_func.nii.gz').dataobj) > 0) &
                       (np.asanyarray(nifti(masks/'mask_csf_func.nii.gz').dataobj) > 0)),
            'WM y CSF se solapan')
    return files, info, stats, prov


def approve(args):
    pre, out = ctx(args)
    require(args.confirmo_registro and args.confirmo_mascaras and args.nota.strip(),
            'Aprobación humana requiere --confirmo-registro --confirmo-mascaras y --nota descriptiva')
    _, _, stats, prov = verify_masks(pre, out)
    file = out / 'APROBACION_VISUAL.json'
    require(not file.exists(), 'Ya hay aprobación; conservar historial y revisar')
    record = {'fecha_utc': utc(), 'sujeto': args.sujeto, 'run': args.run,
              'revision_registro': 'APROBADO_POR_HUMANO',
              'revision_mascaras': 'APROBADO_POR_HUMANO',
              'nota': args.nota, 'mascaras_sha256': prov['mascaras_sha256'],
              'stats': stats}
    json_new(file, record)
    print('QC visual registrado; autorización manual, NO certificación automática.')


def finalize(args):
    pre, out = ctx(args)
    files, info, stats, prov = verify_masks(pre, out)
    approval_file = out / 'APROBACION_VISUAL.json'
    require(approval_file.is_file(), 'Falta revisión humana de registro y máscaras')
    approval = json.loads(approval_file.read_text())
    require(approval['sujeto'] == args.sujeto and approval['run'] == args.run and
            approval['revision_registro'] == 'APROBADO_POR_HUMANO' and
            approval['revision_mascaras'] == 'APROBADO_POR_HUMANO' and
            approval['mascaras_sha256'] == prov['mascaras_sha256'],
            'Aprobación visual no corresponde a estas máscaras')
    require_programs('fslmeants')
    dest = out / 'finales'
    require(not dest.exists(), 'Confusores finales existentes; no sobrescribir')
    temp = out / ('.finales_en_preparacion_' + uuid.uuid4().hex[:12])
    temp.mkdir(parents=True)
    try:
        for tissue in ('wm', 'csf'):
            run_command('fslmeants', '-i', files['bold'],
                        '-m', out / 'mascaras' / f'mask_{tissue}_func.nii.gz',
                        '-o', temp / f'signal_{tissue}.txt')
        n = info['volumenes']
        motion = load_table(files['motion'], 6, n)
        deriv = np.vstack((np.zeros((1, 6)), np.diff(motion, axis=0)))
        wm = load_table(temp / 'signal_wm.txt', 1, n)
        csf = load_table(temp / 'signal_csf.txt', 1, n)
        require(float(np.ptp(wm)) > 1e-12 and float(np.ptp(csf)) > 1e-12,
                'Señal WM o CSF constante; revisar máscaras')
        matrix = np.column_stack((motion, deriv, wm, csf))
        require(matrix.shape == (n, 14) and np.isfinite(matrix).all(),
                'Confusores incompletos/no finitos')
        np.savetxt(temp/'motion_deriv.par', deriv, fmt='%.12g')
        np.savetxt(temp/'todos_confounds_nativo.txt', matrix, fmt='%.12g')
        reread = load_table(temp/'todos_confounds_nativo.txt', 14, n)
        require(np.allclose(reread, matrix, rtol=0, atol=1e-6),
                'Error al escribir la matriz final')
        fin = {'fecha_utc': utc(), 'sujeto': args.sujeto, 'run': args.run,
               'espacio_extraccion': 'funcional_nativo', 'columnas': 14,
               'filas': n, 'orden': ['rotX', 'rotY', 'rotZ', 'transX', 'transY', 'transZ',
                                    'drotX', 'drotY', 'drotZ', 'dtransX', 'dtransY', 'dtransZ',
                                    'WM', 'CSF'],
               'bold_sha256': digest(files['bold']),
               'motion_sha256': digest(files['motion']),
               'aprobacion_visual_sha256': digest(approval_file),
               'mascaras_sha256': prov['mascaras_sha256'],
               'matriz_sha256': digest(temp/'todos_confounds_nativo.txt')}
        json_new(temp / 'FINALIZADO.json', fin)
        temp.rename(dest)
    except Exception:
        print('Confusores INCOMPLETOS, conservar temporal para diagnóstico:', temp, file=sys.stderr)
        raise
    print('CONFUSORES_NATIVOS_LISTOS:', dest/'todos_confounds_nativo.txt')
    print('Dimension:', info['volumenes'], 'x 14')


def status(args):
    pre, out = ctx(args)
    input_audit(pre)
    print('FEAT de origen:', pre)
    for stage in ('mascaras/procedencia.json', 'APROBACION_VISUAL.json', 'finales/FINALIZADO.json'):
        print(stage, 'SI' if (out/stage).is_file() else 'PENDIENTE')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('accion', choices=['auditar', 'mascaras', 'aprobar', 'finalizar', 'estado'])
    p.add_argument('--sujeto', required=True)
    p.add_argument('--run', required=True, type=int)
    p.add_argument('--feat', help='Carpeta FEAT preprocesada; por defecto ~/Escritorio/SUJETO/runN.feat')
    p.add_argument('--trabajo', default='~/TesisDoctoral/fsl_nativo')
    p.add_argument('--confirmo-registro', action='store_true')
    p.add_argument('--confirmo-mascaras', action='store_true')
    p.add_argument('--nota', default='')
    args = p.parse_args(argv)
    try:
        {'auditar': audit, 'mascaras': create_masks, 'aprobar': approve,
         'finalizar': finalize, 'estado': status}[args.accion](args)
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as e:
        print('DETENIDO:', e, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
