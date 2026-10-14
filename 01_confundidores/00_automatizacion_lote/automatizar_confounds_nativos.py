#!/usr/bin/env python3
"""Pipeline conservador de confusores nativos para FEAT ya preprocesados.

Etapas: plan, prepare, prepare-all, approve, finalize, finalize-all, status.
Nunca escribe en --feat-root ni reejecuta FAST/MCFLIRT/BET/preprocesamiento.
No ejecuta FEAT ni aprueba máscaras automáticamente.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def check(test, msg):
    if not test:
        raise RuntimeError(msg)


def valid_file(path):
    return path.is_file() and path.stat().st_size > 0


def call(*args):
    print('FSL:', ' '.join(str(a) for a in args), flush=True)
    subprocess.run([str(a) for a in args], check=True)


def fslval(img, key):
    out = subprocess.run(['fslval', str(img), key], capture_output=True,
                         text=True, check=True).stdout.strip()
    return float(out.split()[0])


def volume(img):
    out = subprocess.run(['fslstats', str(img), '-V'], capture_output=True,
                         text=True, check=True).stdout.strip().split()
    check(len(out) >= 1, f'No se pudo leer volumen: {img}')
    return int(float(out[0]))


def geometry(img):
    return [fslval(img, f'dim{i}') for i in (1, 2, 3)] + [fslval(img, f'pixdim{i}') for i in (1, 2, 3)]


def geom_match(a, b):
    x, y = geometry(a), geometry(b)
    return all(abs(p-q) < 1e-4 for p, q in zip(x, y))


def runner_paths(a, sid, run):
    sid = str(sid)
    check(re.fullmatch(r'\d{4}', sid) is not None, 'ID inválido (4 dígitos)')
    check(run in ('run1','run2'), 'Run inválido')
    pre = a.feat_root / sid / (run+'.feat')
    out = a.native_root / sid / run
    check(not a.native_root.resolve().is_relative_to(a.feat_root.resolve()),
          'Salida confounds dentro del árbol de preprocesamientos: prohibido')
    check(not out.resolve().is_relative_to(a.feat_root.resolve()),
          'Salida dentro de FEAT original: prohibido')
    return pre, out


def assess(a, sid, run):
    pre, out = runner_paths(a, sid, run)
    if not pre.is_dir():
        return dict(status='PREPROC_AUSENTE', issues=['FALTA_FEAT'])
    required = [pre / p for p in ('filtered_func_data.nii.gz','mask.nii.gz',
                'example_func.nii.gz','reg/highres.nii.gz',
                'reg/highres2example_func.mat','mc/prefiltered_func_data_mcf.par')]
    missing = ['FALTA_'+x.relative_to(pre).as_posix() for x in required if not valid_file(x)]
    if missing:
        return dict(status='PREPROC_INCOMPLETO', issues=missing)
    t1hash = sha(pre/'reg/highres.nii.gz')
    tissue = a.mirta_root / sid / f'tissue_{t1hash[:16]}'
    pves = [tissue/f'fast_{sid}_pve_{idx}.nii.gz' for idx in (0,2)]
    derivative = a.mirta_root/sid/run/'motion_deriv.par'
    issues = ['FALTA_'+p.name for p in pves if not valid_file(p)]
    if not valid_file(derivative):
        issues.append('FALTA_motion_deriv.par')
    if out.exists() or out.is_symlink():
        issues.append('SALIDA_EXISTENTE_NO_MODIFICAR')
    if not issues:
        try:
            bold, mask, example, highres = required[0],required[1],required[2],required[3]
            check(geom_match(bold, mask), 'GEOMETRIA_BOLD_MASK')
            check(geom_match(bold, example), 'GEOMETRIA_BOLD_EXAMPLE')
            for p in pves:
                check(geom_match(highres, p), 'GEOMETRIA_FAST_T1')
            n = int(fslval(bold,'dim4'))
            tr = fslval(bold,'pixdim4')
            check(n>10 and 0.2<=tr<=10, 'NPTS_TR_INVALIDOS')
            motion=matrix(pre/'mc/prefiltered_func_data_mcf.par',6,n)
            deriv=matrix(derivative,6,n)
            maximum=max(abs(deriv[t][j]-(0. if t==0 else motion[t][j]-motion[t-1][j]))
                        for t in range(n) for j in range(6))
            check(maximum<1e-7,'DERIVADAS_MOVIMIENTO_INVALIDAS')
        except (RuntimeError,ValueError,subprocess.SubprocessError,IndexError,OSError) as e:
            issues.append('GEOMETRIA_O_NPTS_'+str(e).replace(' ', '_'))
    return dict(status='LISTO_PARA_PREPARE' if not issues else 'REVISAR',
                issues=issues, t1hash=t1hash, pves=pves, derivative=derivative,
                pre=pre, out=out, n=int(fslval(required[0],'dim4')) if not issues else None)


def atomic_json_new(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')


def manifest(out, name):
    path=out/name
    check(valid_file(path), f'FALTA {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def prepare(a, sid, run):
    s=assess(a,sid,run)
    check(s['status']=='LISTO_PARA_PREPARE',
          f'NO PREPARAR {sid}/{run}: {s["status"]} {s["issues"]}')
    pre, out, pves=s['pre'],s['out'],s['pves']
    out.parent.mkdir(parents=True,exist_ok=True)
    out.mkdir(exist_ok=False)
    print('DIRECTORIO NUEVO:',out,flush=True)
    for kind, idx in (('csf',0),('wm',1)):
        src=pves[idx]
        t1=out/f'mask_{kind}_T1.nii.gz'
        prelim=out/f'mask_{kind}_func_prelim.nii.gz'
        final=out/f'mask_{kind}_func.nii.gz'
        call('fslmaths',src,'-thr','0.9','-bin',t1)
        call('flirt','-in',t1,'-ref',pre/'example_func.nii.gz',
             '-applyxfm','-init',pre/'reg/highres2example_func.mat',
             '-interp','nearestneighbour','-out',prelim)
        call('fslmaths',prelim,'-bin','-mas',pre/'mask.nii.gz',final)
        check(valid_file(final),'MASCARA_FINAL_NO_CREADA')
        check(geom_match(final,pre/'filtered_func_data.nii.gz'),
              'MASCARA_NO_COINCIDE_GEOMETRIA')
    wm=out/'mask_wm_func.nii.gz'; csf=out/'mask_csf_func.nii.gz'
    brainvol=volume(pre/'mask.nii.gz'); wmv=volume(wm); csfv=volume(csf)
    check(brainvol>0,'MASCARA_CEREBRAL_VACIA')
    check(20<wmv<brainvol and 20<csfv<brainvol,'MASCARAS_VACIAS_O_INCORRECTAS')
    check(wmv+csfv<brainvol,'MASCARAS_INCOMPATIBLES_CON_CEREBRO')
    overlap=out/'comprobacion_solapamiento_wm_csf.nii.gz'
    call('fslmaths',wm,'-mul',csf,overlap)
    check(volume(overlap)==0,'SOLAPAMIENTO_WM_CSF_NO_CERO')
    fp={name:sha(out/name) for name in ('mask_wm_func.nii.gz','mask_csf_func.nii.gz')}
    atomic_json_new(out/'prepare.json', {
        'estado':'PREPARADO_PENDIENTE_QC_VISUAL','sujeto':str(sid),'run':run,
        'fecha_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'fuente_feat':str(pre), 'sha256_highres':s['t1hash'],
        'archivos_FAST':[str(p) for p in pves],
        'sha256_mascaras':fp,
        'voxeles':{'brain':brainvol,'wm':wmv,'csf':csfv,'solapamiento':0},
        'barrera': 'SIN APROBACION VISUAL NO SE EXTRAEN SENALES'
    })
    print(f'PREPARADO {sid}/{run}: mask={brainvol}, WM={wmv}, CSF={csfv}; QC VISUAL PENDIENTE')


def approve(a, sid, run, observer, confirmation):
    check(confirmation=='HE_REVISADO_AMBAS_MASCARAS',
          'Para aprobar se requiere --confirm HE_REVISADO_AMBAS_MASCARAS')
    check(observer.strip()!='','Falta observador')
    pre,out=runner_paths(a,sid,run)
    data=manifest(out,'prepare.json')
    check(data['sujeto']==str(sid) and data['run']==run,'MANIFIESTO_DE_OTRO_RUN')
    for name, expect in data['sha256_mascaras'].items():
        check(sha(out/name)==expect, f'MASCARA_MODIFICADA: {name}')
    check(not (out/'aprobacion_visual.json').exists(),'APROBACION_YA_EXISTE')
    atomic_json_new(out/'aprobacion_visual.json',{
        'aprobado':True,'observador':observer,'fecha_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'sha256_mascaras_aprobadas':data['sha256_mascaras'],
        'declaracion':'Se inspeccionaron WM y CSF sobre example_func para este run.'
    })
    print(f'APROBACION VISUAL REGISTRADA {sid}/{run}; todavía NO hay confounds')


def matrix(path, cols, n):
    check(valid_file(path), f'FALTA MATRIZ: {path}')
    result=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        v=[float(x) for x in line.split()]
        check(len(v)==cols and all(map(math.isfinite,v)),f'MATRIZ_INVALIDA {path}')
        result.append(v)
    check(len(result)==n,f'FILAS_INVALIDAS {path}: {len(result)} vs {n}')
    return result


def finalize(a,sid,run):
    pre,out=runner_paths(a,sid,run)
    prep=manifest(out,'prepare.json')
    qc=manifest(out,'aprobacion_visual.json')
    check(qc.get('aprobado') is True,'MASCARAS_NO_APROBADAS')
    check(qc.get('sha256_mascaras_aprobadas')==prep['sha256_mascaras'],
          'LAS_MASCARAS_APROBADAS_NO_COINCIDEN')
    for name, expect in prep['sha256_mascaras'].items():
        check(sha(out/name)==expect,f'MASCARA_MODIFICADA: {name}')
    check(prep['sha256_highres']==sha(pre/'reg/highres.nii.gz'),'T1_HA_CAMBIADO')
    for path in (out/'todos_confounds_nativo.txt',out/'finalize.json',
                 out/'signal_wm_nativa.txt',out/'signal_csf_nativa.txt'):
        check(not path.exists() and not path.is_symlink(),f'DESTINO_EXISTE_NO_SOBRESCRIBIR: {path}')
    bold=pre/'filtered_func_data.nii.gz'
    n=int(fslval(bold,'dim4'))
    check(n>10,'NPTS_INVALIDOS')
    motion=matrix(pre/'mc/prefiltered_func_data_mcf.par',6,n)
    deriv=matrix(a.mirta_root/str(sid)/run/'motion_deriv.par',6,n)
    errors=[]
    for t in range(n):
        for j in range(6):
            expected=0. if t==0 else motion[t][j]-motion[t-1][j]
            errors.append(abs(deriv[t][j]-expected))
    max_error=max(errors)
    check(max_error<1e-7,f'DERIVADAS_INCORRECTAS {max_error}')
    for kind in ('wm','csf'):
        mask=out/f'mask_{kind}_func.nii.gz'
        check(geom_match(bold,mask),f'GEOMETRIA_MASCARA_{kind}')
        call('fslmeants','-i',bold,'-m',mask,'-o',out/f'signal_{kind}_nativa.txt')
    wm=matrix(out/'signal_wm_nativa.txt',1,n)
    csf=matrix(out/'signal_csf_nativa.txt',1,n)
    rows=[motion[t]+deriv[t]+wm[t]+csf[t] for t in range(n)]
    for j in range(14):
        vals=[row[j] for row in rows]
        check(max(vals)-min(vals)>1e-12,f'COLUMNA_CONSTANTE_{j+1}')
    final=out/'todos_confounds_nativo.txt'
    with final.open('x',encoding='utf-8') as f:
        for row in rows:
            f.write(' '.join(f'{v:.17g}' for v in row)+'\n')
    check(matrix(final,14,n)==rows,'MATRIZ_ESCRITA_NO_COINCIDE')
    atomic_json_new(out/'finalize.json', {
        'estado':'CONFOUNDS_OK', 'sujeto':str(sid),'run':run,
        'fecha_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'nvol':n,'columnas':14,'error_max_derivadas':max_error,
        'sha256_confounds':sha(final),
        'advertencia':'Validez estadistica final requiere QC visual y auditoria GLM.'})
    print(f'CONFOUNDS_OK {sid}/{run}: {n} filas x 14 columnas. Max error derivadas {max_error:.4g}')


def runs(a):
    for d in sorted(a.feat_root.iterdir()):
        if d.is_dir() and re.fullmatch(r'\d{4}',d.name):
            for run in ('run1','run2'):
                if (d/(run+'.feat')).is_dir():
                    yield d.name,run


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('plan','prepare','prepare-all','approve','finalize','finalize-all','status'))
    p.add_argument('--id',dest='sid')
    p.add_argument('--run',choices=('run1','run2'))
    p.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    p.add_argument('--mirta-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_mirta')
    p.add_argument('--native-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_nativos')
    p.add_argument('--observer',default='')
    p.add_argument('--confirm',default='')
    p.add_argument('--execute',action='store_true',help='Confirmar ejecucion para preparacion/finalizacion de lote')
    args=p.parse_args()
    check(args.feat_root.is_dir(),'NO_EXISTE_FEAT_ROOT')
    if args.action in ('prepare','prepare-all'):
        for cmd in ('fslmaths','flirt','fslval','fslstats'):
            check(shutil.which(cmd) is not None,f'FALTA_COMANDO_{cmd}')
    if args.action in ('finalize','finalize-all'):
        for cmd in ('fslmeants','fslval'):
            check(shutil.which(cmd) is not None,f'FALTA_COMANDO_{cmd}')
    if args.action in ('plan','status'):
        print('id\trun\testado\tdetalle')
        for sid,run in runs(args):
            if args.action=='status':
                _, out=runner_paths(args,sid,run)
                state=('CONFOUNDS_OK' if (out/'finalize.json').exists()
                    else 'QC_APROBADO_PENDIENTE_FINALIZAR' if (out/'aprobacion_visual.json').exists()
                    else 'PREPARADO_PENDIENTE_QC' if (out/'prepare.json').exists()
                    else 'PILOTO_EXISTENTE_NO_MODIFICAR' if sid=='6037' and run=='run1' and
                         (out/'todos_confounds_nativo.txt').exists()
                    else 'CONFOUNDS_SIN_MANIFIESTO_REVISAR' if (out/'todos_confounds_nativo.txt').exists()
                    else 'CARPETA_INCOMPLETA_REVISAR' if out.exists() else 'SIN_PREPARAR')
                notes='NO_MODIFICAR' if out.exists() else 'NINGUNO'
            else:
                x=assess(args,sid,run)
                state=x['status'];notes=','.join(x['issues']) or 'NINGUNO'
            print('\t'.join((sid,run,state,notes)))
        return
    if args.action in ('prepare-all','finalize-all'):
        check(args.execute,'SIN --execute NO SE PERMITE PROCESAR EN LOTE')
        if args.action=='prepare-all':
            print('BATCH PREPARE: LOS RUNS EXISTENTES SE SALTEAN, NUNCA SE SOBRESCRIBEN.')
        else:
            print('BATCH FINALIZE: SOLO RUNS CON QC HUMANO REGISTRADO.')
        successes=0;skips=0;fails=0
        for sid,run in runs(args):
            if args.action=='prepare-all':
                status=assess(args,sid,run)['status']
                if status!='LISTO_PARA_PREPARE':
                    print('SKIP',sid,run,status);skips+=1;continue
            else:
                _,out=runner_paths(args,sid,run)
                if not (out/'aprobacion_visual.json').exists():
                    skips+=1;continue
                if (out/'finalize.json').exists() or (out/'todos_confounds_nativo.txt').exists():
                    print('SKIP EXISTENTE',sid,run);skips+=1;continue
            try:
                if args.action=='prepare-all':prepare(args,sid,run)
                else:finalize(args,sid,run)
                successes+=1
            except Exception as exc:
                print(f'ERROR {sid}/{run}: {exc}',file=sys.stderr)
                fails+=1
        print(f'LOTE TERMINADO exitosos={successes} omitidos={skips} errores={fails}')
        if fails:sys.exit(1)
        return
    check(args.sid is not None and args.run is not None,'FALTAN --id Y --run')
    if args.action=='prepare':prepare(args,args.sid,args.run)
    elif args.action=='approve':approve(args,args.sid,args.run,args.observer,args.confirm)
    else:finalize(args,args.sid,args.run)


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        print('DETENIDO:',error,file=sys.stderr)
        sys.exit(1)
