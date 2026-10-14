#!/usr/bin/env python3
"""Read-only readiness report for native WM/CSF confound generation.

Never creates folders, modifies NIfTI files, or reruns FSL.
This is a prerequisite audit, not a mask generation or QC approval.
"""
from __future__ import annotations
import argparse
import hashlib
import re
from collections import Counter
from pathlib import Path


def nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def inspect(feat: Path, tissue_root: Path, native_root: Path):
    ident, run = feat.parent.name, feat.name.removesuffix('.feat')
    original = [feat/x for x in (
        'filtered_func_data.nii.gz', 'mask.nii.gz', 'example_func.nii.gz',
        'reg/highres.nii.gz', 'reg/highres2example_func.mat',
        'mc/prefiltered_func_data_mcf.par',
    )]
    missing = ['FALTA_' + f.relative_to(feat).as_posix() for f in original if not nonempty(f)]
    if missing:
        return (ident, run, 'PREPROC_INCOMPLETO', '-', '-', ','.join(missing))

    try:
        finger = sha256(feat/'reg/highres.nii.gz')[:16]
    except OSError:
        return (ident, run, 'REVISAR_T1', '-', '-', 'NO_SE_PUEDE_LEER_REG_HIGHRES')

    subject = tissue_root/ident
    tissue = subject/f'tissue_{finger}'
    tissue_candidates = sorted(p for p in subject.glob('tissue_*') if p.is_dir())
    notes = []
    if not tissue.is_dir():
        notes.append('NO_EXISTE_TISSUE_COINCIDENTE_CON_HASH_T1')
        if tissue_candidates:
            notes.append('OTROS_TISSUE='+str(len(tissue_candidates)))
    else:
        for idx in (0, 2):
            f = tissue/f'fast_{ident}_pve_{idx}.nii.gz'
            if not nonempty(f):
                notes.append('FALTA_FAST_PVE_'+str(idx))

    deriv = subject/run/'motion_deriv.par'
    if not nonempty(deriv):
        notes.append('FALTA_MOTION_DERIV')
    if (native_root/ident/run/'todos_confounds_nativo.txt').exists():
        notes.append('CONFOUNDS_NATIVOS_EXISTENTES_NO_SOBRESCRIBIR')

    status = 'INSUMOS_PRESENTES_PENDIENTE_QC' if not notes else 'REVISAR_INSUMOS'
    if ident == '6037' and run == 'run1':
        status = 'PILOTO_6037_RUN1_EXISTENTE'
    return (ident, run, status, finger, tissue.as_posix() if tissue.is_dir() else '-', ','.join(notes) if notes else 'NINGUNO')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--feat-root', type=Path, default=Path.home()/'FEAT')
    p.add_argument('--mirta-root', type=Path, default=Path.home()/'TesisDoctoral/confounds_mirta')
    p.add_argument('--native-root', type=Path, default=Path.home()/'TesisDoctoral/confounds_nativos')
    args = p.parse_args()
    if not args.feat_root.is_dir():
        p.error(f'No existe FEAT root: {args.feat_root}')
    rows = []
    for subject in sorted(args.feat_root.iterdir()):
        if not subject.is_dir() or not re.fullmatch(r'\d{4}', subject.name):
            continue
        for run in ('run1', 'run2'):
            d = subject/(run+'.feat')
            if not d.is_dir():
                continue
            try:
                rows.append(inspect(d, args.mirta_root, args.native_root))
            except OSError as exc:
                rows.append((subject.name, run, 'ERROR_LECTURA', '-', '-', type(exc).__name__))
    print('id\trun\testado\thash_T1_16\tcarpeta_FAST\tdetalle')
    for row in rows:
        print('\t'.join(row))
    counts = Counter(row[2] for row in rows)
    print('# RESUMEN', f'runs={len(rows)}', ' '.join(f'{key}={counts[key]}' for key in sorted(counts)))
    print('# SOLO LECTURA. NO SE CREARON MASCARAS, CONFOUNDS O PROCESAMIENTOS.')


if __name__ == '__main__':
    main()
