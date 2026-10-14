#!/usr/bin/env python3
"""Planifica y genera FSF individuales (SIN copiar FEAT ni ejecutar FILM).

Uso:
  python3 preparar_fsf_nativos.py plan
  python3 preparar_fsf_nativos.py generar --id 6037 --run run2

Plantilla: FSF inputtype=1 del piloto exitoso 6037/run1, solo en equipo local.
Salidas y NIfTI del paciente NUNCA van al repositorio público.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

EVENTS=('AtencionPlena','ExperimNeg','ExperimNeutra','Likert',
        'ObservaNeg','ObservaNeutra','Reinterpreta','Suprime')
REG=('reg/example_func2highres.mat','reg/highres2standard_warp.nii.gz',
     'reg/example_func2standard_warp.nii.gz','reg/standard.nii.gz')
EXACT={'level':'1','analysis':'2','inputtype':'1','filtering_yn':'0',
       'stats_yn':'1','prewhiten_yn':'1','motionevs':'0','confoundevs':'1',
       'reghighres_yn':'0','regstandard_yn':'0','evs_orig':'8',
       'evs_real':'16','ncon_orig':'21','ncon_real':'21'}


def good(path):
    return path.is_file() and path.stat().st_size>0


def hash_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for piece in iter(lambda:f.read(1<<20),b''):
            h.update(piece)
    return h.hexdigest()


def value(image, key):
    p=subprocess.run(['fslval',str(image),key],capture_output=True,text=True,check=True,timeout=30)
    return float(p.stdout.split()[0])


def fsf_entries(text):
    found={}
    for line in text.splitlines():
        match=re.fullmatch(r'set (fmri\([^)]*\)|feat_files\(1\)|confoundev_files\(1\)) (.+)',line.strip())
        if match:
            key=match.group(1)
            if key in found:
                raise ValueError('FSF contiene clave duplicada: '+key)
            found[key]=match.group(2)
    return found


def check_options(text, expected):
    params=fsf_entries(text)
    for k,v in expected.items():
        key='fmri('+k+')'
        if params.get(key)!=v:
            raise ValueError(f'FSF {key} esperado {v}, obtenido {params.get(key)}')
    for k in range(1,9):
        for prefix in ('custom','deriv_yn'):
            field=f'fmri({prefix}{k})'
            if field not in params:
                raise ValueError('FSF sin '+field)
        if params[f'fmri(deriv_yn{k})']!='1':
            raise ValueError('Derivada deshabilitada: '+str(k))
    for k in range(1,22):
        for j in range(1,17):
            field=f'fmri(con_real{k}.{j})'
            if field not in params:
                raise ValueError('FSF sin contraste expandido '+field)
    return params


def replace(text, key, value):
    pattern=r'^(set '+re.escape(key)+r') [^\r\n]+$'
    result,n=re.subn(pattern,lambda m:m.group(1)+' '+value,text,flags=re.M)
    if n!=1:
        raise ValueError('No se pudo reemplazar una sola clave '+key+f': {n}')
    return result


def finite_matrix(path, cols, n):
    with path.open(encoding='utf-8') as f:
        rows=[l.split() for l in f if l.strip()]
    if len(rows)!=n:
        raise ValueError(f'{path}: filas={len(rows)} esperaba={n}')
    matrix=[]
    for row in rows:
        if len(row)!=cols:
            raise ValueError(f'{path}: columnas distintas de {cols}')
        xs=[float(x) for x in row]
        if not all(math.isfinite(v) for v in xs):
            raise ValueError(f'{path}: no finitos')
        matrix.append(xs)
    if any(max(row[j] for row in matrix)-min(row[j] for row in matrix)<1e-12
           for j in range(cols)):
        raise ValueError(f'{path}: regresor constante')
    return matrix


def check_events(root, sid, run, n, tr):
    folder=root/sid/'evs'/('run-'+run[-1])
    result=[]
    for name in EVENTS:
        path=folder/(name+'.txt')
        if not good(path):
            raise ValueError('FALTA_EV_'+name)
        lines=path.read_text(encoding='utf-8').splitlines()
        nonblank=0
        for line in lines:
            if not line.strip():
                continue
            v=[float(x) for x in line.split()]
            if len(v)!=3 or not all(math.isfinite(x) for x in v):
                raise ValueError('EV_INVALIDO_'+name)
            if v[0]<0 or v[1]<=0 or v[0]+v[1]>n*tr+0.0001:
                raise ValueError('EV_FUERA_DEL_RUN_'+name)
            nonblank+=1
        if nonblank==0:
            raise ValueError('EV_VACIO_'+name)
        result.append(path)
    return result


def ready(a,sid,run):
    pre=a.feat_root/sid/(run+'.feat')
    dest=a.out_root/sid/(run+'.feat')
    model=a.out_root/sid/(run+'_stats_only.fsf')
    if (sid,run)==('6037','run1'):
        return 'PILOTO_YA_EJECUTADO','NO_REPETIR'
    if dest.exists() or dest.is_symlink() or model.exists() or model.is_symlink():
        return 'DETENIDO_DESTINO_EXISTENTE','NO_SOBRESCRIBIR'
    if not pre.is_dir():
        return 'NO_APTO','FALTA_FEAT'
    required=[pre/'filtered_func_data.nii.gz',pre/'mask.nii.gz',pre/'example_func.nii.gz',
              pre/'design.fsf',*[pre/p for p in REG]]
    missing=[p.relative_to(pre).as_posix() for p in required if not good(p)]
    if missing:
        return 'NO_APTO','FALTA_'+','.join(missing)
    text=(pre/'design.fsf').read_text(encoding='utf-8',errors='replace')
    for k,v in (('analysis','1'),('filtering_yn','1')):
        if not re.search(r'^set\s+fmri\('+k+r'\)\s+'+v+r'\s*$',text,re.M):
            return 'NO_APTO','PREPROCESAMIENTO_NO_CONFIRMADO_'+k
    try:
        n=int(value(pre/'filtered_func_data.nii.gz','dim4'))
        tr=value(pre/'filtered_func_data.nii.gz','pixdim4')
        if n<=10 or tr<=0 or not math.isfinite(tr):
            raise ValueError('NPTS_TR_INVALIDOS')
        dims=[int(value(pre/'filtered_func_data.nii.gz','dim'+str(i))) for i in (1,2,3)]
        maskdims=[int(value(pre/'mask.nii.gz','dim'+str(i))) for i in (1,2,3)]
        if dims!=maskdims:
            raise ValueError('MASCARA_DE_OTRA_GEOMETRIA')
        conf=a.conf_root/sid/run/'todos_confounds_nativo.txt'
        if not good(conf):
            raise ValueError('FALTAN_CONFOUNDS_NATIVOS')
        mat=finite_matrix(conf,14,n)
        man=a.conf_root/sid/run/'finalize.json'
        if not good(man):
            raise ValueError('FALTA_FINALIZE_VALIDADO')
        data=json.loads(man.read_text(encoding='utf-8'))
        if data.get('estado')!='CONFOUNDS_OK' or data.get('sha256_confounds')!=hash_file(conf):
            raise ValueError('MANIFIESTO_O_HASH_CONFOUNDS_INCORRECTOS')
        if data.get('nvol')!=n or data.get('columnas')!=14:
            raise ValueError('CONFOUNDS_MANIFIESTO_DIMENSIONES')
        qc=a.conf_root/sid/run/'aprobacion_visual.json'
        if not good(qc) or json.loads(qc.read_text(encoding='utf-8')).get('aprobado') is not True:
            raise ValueError('QC_VISUAL_NO_REGISTRADO')
        evs=check_events(a.evs_root,sid,run,n,tr)
        if any(not good(p) for p in evs):
            raise ValueError('EV_FALTANTE')
        return 'APTO_PARA_PREPARAR_FSF',f'N={n};TR={tr:.6g};BOLD={dims};confounds=14'
    except (OSError,ValueError,KeyError,IndexError,subprocess.SubprocessError) as exc:
        return 'NO_APTO',str(exc).replace('\t','_').replace('\n','_')


def make(a,sid,run):
    state,why=ready(a,sid,run)
    if state!='APTO_PARA_PREPARAR_FSF':
        raise ValueError('NO_GENERAR '+sid+'/'+run+' '+state+' '+why)
    source=a.template.read_text(encoding='utf-8')
    check_options(source,EXACT)
    vals=fsf_entries(source)
    # Keep model's eight EVs and all 21 contrasts; change paths and per-run timing only.
    for j,name in enumerate(EVENTS,1):
        prior=Path(vals[f'fmri(custom{j})'].strip('"')).name
        if prior!=name+'.txt':
            raise ValueError('ORDEN_EV_DE_LA_PLANTILLA_NO_ES_EL_ESPERADO: '+str(j))
    pre=a.feat_root/sid/(run+'.feat')
    bold=pre/'filtered_func_data.nii.gz'
    n=int(value(bold,'dim4'))
    tr=value(bold,'pixdim4')
    dimensions=[int(value(bold,'dim'+str(i))) for i in (1,2,3)]
    outdir=a.out_root/sid
    dest=outdir/(run+'.feat')
    fsf=outdir/(run+'_stats_only.fsf')
    # FEAT uses this '.feat' as the actual statistics directory in inputtype=1.
    source=replace(source,'feat_files(1)',json.dumps(str(dest)))
    source=replace(source,'fmri(outputdir)',json.dumps(str(outdir/(run+'_stats_only'))))
    source=replace(source,'confoundev_files(1)',json.dumps(str(a.conf_root/sid/run/'todos_confounds_nativo.txt')))
    source=replace(source,'fmri(tr)',f'{tr:.6f}')
    source=replace(source,'fmri(npts)',str(n))
    source=replace(source,'fmri(totalVoxels)',str(n*math.prod(dimensions)))
    for j,name in enumerate(EVENTS,1):
        event=a.evs_root/sid/'evs'/('run-'+run[-1])/(name+'.txt')
        source=replace(source,f'fmri(custom{j})',json.dumps(str(event)))
    generated=check_options(source,EXACT)
    if generated['feat_files(1)']!=json.dumps(str(dest)):
        raise ValueError('RUTA_DE_ENTRADA_FSF_INCORRECTA')
    for j,name in enumerate(EVENTS,1):
        if generated[f'fmri(custom{j})']!=json.dumps(str(a.evs_root/sid/'evs'/('run-'+run[-1])/(name+'.txt'))):
            raise ValueError('RUTA_EV_GENERADA_INCORRECTA')
    # Preflight before any filesystem modification.
    if outdir.exists() and not outdir.is_dir():
        raise ValueError('OUTPUT_PARENT_NO_ES_DIRECTORIO')
    if outdir.is_symlink() or outdir.resolve().is_relative_to(a.feat_root.resolve()):
        raise ValueError('RUTA_DE_SALIDA_INSEGURA')
    if dest.exists() or dest.is_symlink() or fsf.exists() or fsf.is_symlink():
        raise ValueError('YA_EXISTE_SALIDA_NO_SOBRESCRIBIR')
    outdir.mkdir(parents=True,exist_ok=True)
    with fsf.open('x',encoding='utf-8') as f:
        f.write(source)
    print('FSF_CREADO',sid,run,fsf)
    print('COPIA_FEAT_TODAVIA_NO_CREADA',dest)
    print('FEAT_Y_FILM_NO_EJECUTADOS')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('plan','generar'))
    p.add_argument('--id',dest='sid')
    p.add_argument('--run',choices=('run1','run2'))
    p.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    p.add_argument('--conf-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_nativos')
    p.add_argument('--evs-root',type=Path,default=Path.home()/'NIFTIS_DESCOMPRIMIDOS')
    p.add_argument('--out-root',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO')
    p.add_argument('--template',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/6037_run1_nativo_INPUTTYPE1.fsf')
    a=p.parse_args()
    if not a.feat_root.is_dir():
        p.error('no existe FEAT_ROOT')
    if a.out_root.resolve().is_relative_to(a.feat_root.resolve()):
        p.error('out-root dentro de FEAT original, prohibido')
    if a.action=='generar':
        if not a.sid or not re.fullmatch(r'\d{4}',a.sid) or not a.run:
            p.error('generar requiere --id XXXX --run run1|run2')
        if not a.template.is_file():
            p.error('falta la plantilla FSF inputtype=1')
        make(a,a.sid,a.run)
        return
    print('id\trun\testado\tdetalle')
    result={}
    for folder in sorted(a.feat_root.iterdir()):
        if folder.is_dir() and re.fullmatch(r'\d{4}',folder.name):
            for run in ('run1','run2'):
                if (folder/(run+'.feat')).is_dir():
                    state,why=ready(a,folder.name,run)
                    result[state]=result.get(state,0)+1
                    print('\t'.join((folder.name,run,state,why)))
    print('# RESUMEN '+' '.join(f'{k}={v}' for k,v in sorted(result.items())))
    print('# NO SE CREARON FSF, COPIAS, NI ESTADISTICAS.')


if __name__=='__main__':
    try:
        main()
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print('DETENIDO:',exc,file=sys.stderr)
        sys.exit(1)
