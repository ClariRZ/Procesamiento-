#!/usr/bin/env python3
"""Auditoría SOLO LECTURA del preprocesamiento FEAT y GLM 6037.

Examina los FEAT originales en ~/FEAT, los FSF estadísticos ya preparados
(sin escribir ni ejecutar FEAT/feat_model) y el design.mat del piloto.
NO modifica máscaras, confounds, FSF ni archivos de imágenes.

Uso:
    python3 -B auditar_homogeneidad_y_diseno.py
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import math
from pathlib import Path
import re
import subprocess
import sys

PARAMS = (
    'analysis', 'filtering_yn', 'ndelete', 'paradigm_hp', 'smooth', 'tr',
    'npts', 'temphp_yn', 'templp_yn', 'st', 'mc', 'norm_yn',
)
PREPROC_CRITICAL = ('ndelete', 'paradigm_hp', 'smooth', 'temphp_yn', 'templp_yn', 'st')
MODEL_EXPECTED = {'analysis': '2', 'inputtype': '1', 'filtering_yn': '0',
                  'stats_yn': '1', 'confoundevs': '1', 'motionevs': '0'}


def fsf_settings(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f'FSF_NO_EXISTE {path}')
    result = {}
    for i, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        found = re.fullmatch(r'\s*set\s+(fmri\([^)]*\)|feat_files\(1\)|confoundev_files\(1\))\s+(.+?)\s*', line)
        if not found:
            continue
        name, raw = found.groups()
        if name in result:
            raise ValueError(f'FSF_CLAVE_DUPLICADA {path}:{i} {name}')
        result[name] = raw.strip().strip('"')
    return result


def field(params: dict[str, str], name: str) -> str:
    return params.get('fmri(' + name + ')', '<ausente>')


def fslval(nifti: Path, tag: str) -> float:
    p = subprocess.run(['fslval', str(nifti), tag], text=True,
                       capture_output=True, check=True, timeout=30)
    v = float(p.stdout.split()[0])
    if not math.isfinite(v):
        raise ValueError('FSLVAL_NO_FINITO ' + str(nifti) + ' ' + tag)
    return v


def matrix(path: Path, number: int | None = None) -> list[list[float]]:
    if not path.is_file():
        raise ValueError('FALTA_MATRIZ ' + str(path))
    result = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        vals = [float(v) for v in line.split()]
        if number is not None and len(vals) != number:
            raise ValueError(f'COLUMNAS_{len(vals)}_ESPERADAS_{number} {path}')
        if not all(math.isfinite(v) for v in vals):
            raise ValueError('MATRIZ_NO_FINITA ' + str(path))
        result.append(vals)
    return result


def feat_matrix(path: Path) -> tuple[dict[str, int], list[list[float]]]:
    text = path.read_text(encoding='utf-8')
    header = {}
    for key in ('NumWaves', 'NumPoints', 'NumContrasts'):
        m = re.search(r'^/' + key + r'\s+(\d+)\s*$', text, flags=re.M)
        if m:
            header[key] = int(m.group(1))
    split = re.search(r'^/Matrix\s*$', text, flags=re.M)
    if not split:
        raise ValueError('FALTA_/Matrix ' + str(path))
    data = []
    for line in text[split.end():].splitlines():
        if line.strip():
            data.append([float(v) for v in line.split()])
    n = header.get('NumPoints', header.get('NumContrasts'))
    p = header.get('NumWaves')
    if n is None or p is None or len(data) != n or any(len(x) != p for x in data):
        raise ValueError(f'MATRIZ_DIMENSIONES_INCORRECTAS {path}')
    if not all(math.isfinite(z) for row in data for z in row):
        raise ValueError('MATRIZ_NO_FINITA ' + str(path))
    return header, data


def correlation(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b) or not a:
        return None
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    aa = [v - ma for v in a]
    bb = [v - mb for v in b]
    ssx = sum(v * v for v in aa)
    ssy = sum(v * v for v in bb)
    if ssx < 1e-24 or ssy < 1e-24:
        return None
    return sum(x * y for x, y in zip(aa, bb)) / math.sqrt(ssx * ssy)


def assess_pilot(design: Path, nuisance: Path) -> None:
    print('\n=== 6037/run1: inspección del diseño estadístico, SOLO LECTURA ===')
    if not design.is_file():
        print('PILOTO_SIN_DESIGN_MAT', design)
        return
    if not nuisance.is_file():
        print('PILOTO_SIN_CONFOUNDS', nuisance)
        return
    h, x = feat_matrix(design)
    c = matrix(nuisance, 14)
    print('MATRIZ_GLM NumPoints=', h['NumPoints'], 'NumWaves=', h['NumWaves'],
          'CONF_FILAS=', len(c))
    if h['NumWaves'] != 30 or h['NumPoints'] != len(c):
        print('PILOTO_DISENO_DIMENSIONES_INESPERADAS')
        return
    # Correlación insensible a escala/signo, no equivale a prueba de filtrado.
    correlations = [correlation([row[16 + j] for row in x], [row[j] for row in c])
                    for j in range(14)]
    print('CORR_CON_SERIE_CRUDA_14_COLUMNAS:',
          ' '.join('NA' if v is None else f'{v:.4f}' for v in correlations))
    largest = []
    for j in range(14):
        values = []
        for k in range(16):
            r = correlation([row[16 + j] for row in x], [row[k] for row in x])
            if r is not None:
                values.append((abs(r), k + 1, r))
        if values:
            largest.append((j + 17, *max(values)))
    largest.sort(key=lambda z: z[1], reverse=True)
    print('COLINEALIDAD_MAYOR_CONF_VS_TAREA:',
          '; '.join(f'conf_col{j} x tarea_col{k}: r={r:.3f}'
                    for j, magnitude, k, r in largest[:5]))
    print('ADVERTENCIA: correlación/colinealidad NO prueban contaminacion tisular ni'
          ' equivalencia de high-pass; contrastar con procesamiento temporal FSL.')


def main() -> int:
    home = Path.home()
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--feat-root', type=Path, default=home / 'FEAT')
    arg.add_argument('--out-root', type=Path, default=home / 'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO')
    arg.add_argument('--conf-root', type=Path, default=home / 'TesisDoctoral/confounds_nativos')
    arg.add_argument('--pilot-design', type=Path,
                     default=home / 'TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/design.mat')
    arg.add_argument('--pilot-conf', type=Path,
                     default=home / 'TesisDoctoral/confounds_nativos/6037/run1/todos_confounds_nativo.txt')
    args = arg.parse_args()
    if not args.feat_root.is_dir():
        arg.error('FEAT root no encontrado: ' + str(args.feat_root))
    categories = Counter()
    values = defaultdict(lambda: defaultdict(list))
    runinfo: dict[tuple[str, str], dict[str, str]] = {}
    alerts = []
    failures = []
    model_count = 0
    print('SUJETO RUN NPTS TR NDELETE HP SMOOTH SLICE_T ESTADO')
    for folder in sorted(args.feat_root.iterdir()):
        if not folder.is_dir() or not re.fullmatch(r'\d{4}', folder.name):
            continue
        sid = folder.name
        for run in ('run1', 'run2'):
            feat = folder / (run + '.feat')
            if not feat.is_dir():
                continue
            bold = feat / 'filtered_func_data.nii.gz'
            if not bold.is_file():
                categories['INCOMPLETO'] += 1
                print(sid, run, '-', '-', '-', '-', '-', '-', 'INCOMPLETO')
                continue
            try:
                fsf = fsf_settings(feat / 'design.fsf')
                npts = int(fslval(bold, 'dim4'))
                tr = fslval(bold, 'pixdim4')
                data = {key: field(fsf, key) for key in PARAMS}
                data['npts_bold'] = str(npts)
                data['tr_bold'] = str(tr)
                runinfo[(sid, run)] = data
                categories['PREPROC_COMPLETO'] += 1
                for key, v in data.items():
                    values[key][v].append(sid + '/' + run)
                if field(fsf, 'filtering_yn') != '1' or field(fsf, 'analysis') != '1':
                    alerts.append(f'{sid}/{run}: ORIGINAL_NO_ES_PREPROCESADO_SOLO')
                if data['ndelete'] == '<ausente>':
                    alerts.append(f'{sid}/{run}: NDELETE_FALTA_EN_FSF')
                elif data['ndelete'] != '0':
                    alerts.append(f'{sid}/{run}: NDELETE={data["ndelete"]}; revisar EV y momento de corte')
                if field(fsf, 'tr') != '<ausente>':
                    if abs(float(field(fsf, 'tr')) - tr) > 1e-3:
                        alerts.append(f'{sid}/{run}: TR_FSF_DIFIERE_DE_BOLD')
                model = args.out_root / sid / (run + '_stats_only.fsf')
                if model.is_file():
                    model_count += 1
                    f = fsf_settings(model)
                    for key, expected in MODEL_EXPECTED.items():
                        if field(f, key) != expected:
                            failures.append(f'{sid}/{run}: FSF_MODELO_{key}_ES_{field(f,key)}_NO_{expected}')
                    if f.get('feat_files(1)') != str(args.out_root / sid / (run + '.feat')):
                        failures.append(f'{sid}/{run}: FSF_APUNTA_A_OTRA_FEAT')
                    if f.get('confoundev_files(1)') != str(args.conf_root / sid / run / 'todos_confounds_nativo.txt'):
                        failures.append(f'{sid}/{run}: FSF_APUNTA_A_OTROS_CONFOUNDS')
                    for key in ('ndelete', 'paradigm_hp'):
                        modelv = field(f, key)
                        prev = data[key]
                        if prev != '<ausente>' and modelv != '<ausente>' and modelv != prev:
                            alerts.append(f'{sid}/{run}: FSF_MODELO_{key}={modelv}, PREPROC={prev}')
                print(sid, run, npts, f'{tr:g}', data['ndelete'], data['paradigm_hp'],
                      data['smooth'], data['st'], 'OK_PREPROC')
            except Exception as e:
                categories['ERROR'] += 1
                failures.append(f'{sid}/{run}: {str(e)}')
                print(sid, run, '-', '-', '-', '-', '-', '-', 'ERROR')
    print('\n=== Distribución real en 73 FEAT preprocesados ===')
    for key in ('ndelete', 'paradigm_hp', 'smooth', 'temphp_yn', 'templp_yn',
                'tr', 'tr_bold', 'npts_bold', 'st', 'filtering_yn'):
        print(key + ':',
              ' | '.join(f'{val} (n={len(ids)})' for val, ids in sorted(values[key].items())))
    print('\n=== Discrepancias entre runs del mismo sujeto ===')
    mismatches = 0
    for sid in sorted({sid for sid, _ in runinfo}):
        if (sid, 'run1') not in runinfo or (sid, 'run2') not in runinfo:
            continue
        left = runinfo[(sid, 'run1')]
        right = runinfo[(sid, 'run2')]
        different = [k for k in PREPROC_CRITICAL if left[k] != right[k]]
        if different:
            mismatches += 1
            print(sid, ':', ', '.join(f'{k}={left[k]}|{right[k]}' for k in different))
    if mismatches == 0:
        print('NINGUNA_DIFERENCIA_EN_PARAMETROS_COMPARADOS')
    print('\n=== Advertencias ===')
    for v in alerts:
        print('REVISAR', v)
    if not alerts:
        print('NINGUNA_ADVERTENCIA_DE_CONFIGURACION')
    print('\n=== Errores ===')
    for v in failures:
        print('ERROR', v)
    if not failures:
        print('NINGUN_ERROR_DE_CONFIGURACION')
    try:
        assess_pilot(args.pilot_design, args.pilot_conf)
    except (OSError, ValueError) as e:
        print('PILOTO_ERROR_DE_LECTURA:', str(e))
        failures.append('PILOTO_ERROR_DE_LECTURA ' + str(e))
    print('\nRESUMEN', dict(categories), 'fsf_estadisticos=', model_count,
          'diferencias_pareadas=', mismatches,
          'advertencias=', len(alerts), 'errores=', len(failures))
    print('SOLO_LECTURA; NO_APRUEBA_MODELO_NI_EJECUTA_FEAT')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
