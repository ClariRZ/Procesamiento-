#!/usr/bin/env python3
"""Inventario sin escrituras de runs FEAT nativos disponibles.

No crea carpetas ni modifica datos. Requiere fslval (FSL) en PATH.
La elegibilidad técnica NO reemplaza QC visual ni autorización de ejecución.
"""
import argparse
import math
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

EVENTOS = (
    'AtencionPlena', 'ExperimNeg', 'ExperimNeutra', 'Likert',
    'ObservaNeg', 'ObservaNeutra', 'Reinterpreta', 'Suprime',
)
REG = ('reg/example_func2highres.mat', 'reg/highres2standard_warp.nii.gz',
       'reg/example_func2standard_warp.nii.gz', 'reg/standard.nii.gz')


def nonempty(path):
    return path.is_file() and path.stat().st_size > 0


def fslval(path, key):
    p = subprocess.run(('fslval', str(path), key), capture_output=True,
                       text=True, check=True, timeout=30)
    return float(p.stdout.split()[0])


def rows(path, cols, n):
    result = []
    with path.open(encoding='utf-8') as file:
        for line in file:
            fields = line.split()
            if len(fields) != cols:
                raise ValueError(f'{path.name}: columnas distintas de {cols}')
            row = [float(t) for t in fields]
            if not all(math.isfinite(t) for t in row):
                raise ValueError(f'{path.name}: valores no finitos')
            result.append(row)
    if len(result) != n:
        raise ValueError(f'{path.name}: {len(result)} filas, esperadas {n}')
    return result


def preflight(feat, data_root, conf_root, output_root):
    sid, run = feat.parent.name, feat.name[:-5]
    errs, extras = [], []
    bold, mask = feat/'filtered_func_data.nii.gz', feat/'mask.nii.gz'
    for path in (bold, mask, feat/'example_func.nii.gz', feat/'design.fsf', *[feat/p for p in REG]):
        if not nonempty(path):
            errs.append('FALTA_'+path.relative_to(feat).as_posix())
    design = feat/'design.fsf'
    if nonempty(design):
        txt = design.read_text(encoding='utf-8', errors='replace')
        for key, val in [('analysis','1'), ('filtering_yn','1')]:
            if not re.search(r'^set\s+fmri\('+key+r'\)\s+'+val+r'\s*$', txt, re.M):
                errs.append('PREPROCESAMIENTO_NO_CONFIRMADO_'+key)
    n, tr = 0, 0.0
    if nonempty(bold) and nonempty(mask):
        try:
            n = int(fslval(bold, 'dim4'))
            tr = fslval(bold, 'pixdim4')
            if n <= 10 or not 0.2 <= tr <= 10:
                errs.append('NPTS_TR_INVALIDOS')
            for k in ('dim1','dim2','dim3'):
                if fslval(bold, k) != fslval(mask, k):
                    errs.append('MASCARA_NO_COINCIDE_'+k)
        except (ValueError, IndexError, subprocess.SubprocessError, OSError) as exc:
            errs.append('FSLVAL_ERROR_'+type(exc).__name__)
    if n and tr:
        evdir = data_root/sid/'evs'/f'run-{run[3:]}'
        for ev in EVENTOS:
            file = evdir/(ev+'.txt')
            if not nonempty(file):
                errs.append('FALTA_EV_'+ev)
                continue
            try:
                count = 0
                for line in file.read_text(encoding='utf-8').splitlines():
                    if not line.strip():
                        continue
                    a = [float(v) for v in line.split()]
                    if len(a) != 3 or not all(map(math.isfinite, a)) or a[0] < 0 or a[1] <= 0 or a[0]+a[1] > n*tr+1e-5:
                        raise ValueError('evento fuera de rango o formato inválido')
                    count += 1
                if not count:
                    raise ValueError('sin eventos')
            except ValueError:
                errs.append('EV_INVALIDO_'+ev)
        native = conf_root/sid/run
        for tissue in ('wm','csf'):
            if not nonempty(native/f'mask_{tissue}_func.nii.gz'):
                errs.append('FALTA_MASCARA_'+tissue.upper())
        conf = native/'todos_confounds_nativo.txt'
        movement = feat/'mc/prefiltered_func_data_mcf.par'
        if not nonempty(conf):
            errs.append('FALTAN_CONFOUNDS_NATIVOS')
        if not nonempty(movement):
            errs.append('FALTA_MCFLIRT_PAR')
        if nonempty(conf) and nonempty(movement):
            try:
                c, m = rows(conf, 14, n), rows(movement, 6, n)
                for t in range(n):
                    for j in range(6):
                        d = 0. if t == 0 else m[t][j]-m[t-1][j]
                        if abs(c[t][j]-m[t][j]) > 1e-6 or abs(c[t][j+6]-d) > 1e-6:
                            raise ValueError('confounds no coinciden con movimiento')
                for j in range(14):
                    if max(row[j] for row in c)-min(row[j] for row in c) < 1e-12:
                        raise ValueError('regresor constante')
            except (OSError, ValueError, OverflowError):
                errs.append('CONFOUNDS_INVALIDOS')
    dest = output_root/sid/(run+'.feat')
    if dest.exists() or dest.is_symlink():
        errs.append('DESTINO_YA_EXISTE_NO_SOBRESCRIBIR')
    # El piloto 6037/run1 ya fue realizado por separado. No duplicar.
    if sid == '6037' and run == 'run1':
        pilot = Path.home()/'TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/entrada_run1.feat/stats'
        if all(nonempty(pilot/f'{kind}{i}.nii.gz') for kind in ('cope','varcope','zstat') for i in range(1,22)):
            extras.append('PILOTO_EXISTENTE_6037_RUN1')
    status = ('REVISAR' if errs else 'APTO_TECNICO_PENDIENTE_QC_VISUAL')
    if extras:
        status = 'YA_ANALIZADO_PILOTO'
    return (sid,run,str(n or ''),format(tr,'.6g') if tr else '',status,','.join(errs+extras) or 'NINGUNO')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    p.add_argument('--data-root',type=Path,default=Path.home()/'NIFTIS_DESCOMPRIMIDOS')
    p.add_argument('--conf-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_nativos')
    p.add_argument('--out-root',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO')
    args = p.parse_args()
    if not shutil.which('fslval'):
        p.error('fslval no está disponible en PATH (cargar FSL antes)')
    if not args.feat_root.is_dir():
        p.error('no existe --feat-root')
    feats = sorted(f for sub in args.feat_root.iterdir() if sub.is_dir() and re.fullmatch(r'\d{4}',sub.name)
                   for f in sub.iterdir() if f.is_dir() and re.fullmatch(r'run[12]\.feat', f.name))
    print('id\trun\tnvol\ttr_s\testado\tdetalle')
    results = []
    for feat in feats:
        try:
            row = preflight(feat,args.data_root,args.conf_root,args.out_root)
        except (OSError,ValueError) as exc:
            row = (feat.parent.name,feat.name[:-5],'','','REVISAR','ERROR_LECTURA_'+type(exc).__name__)
        print('\t'.join(row))
        results.append(row)
    count = Counter(x[4] for x in results)
    print(f'# RESUMEN sujetos={len({r[0] for r in results})} runs_detectados={len(results)} '+
          ' '.join(f'{k}={v}' for k,v in sorted(count.items())))
    print('# SIN CAMBIOS: ninguna imagen, FSF, confound o carpeta fue modificada')


if __name__=='__main__':
    main()
