#!/usr/bin/env python3
"""Auditoría estrictamente de solo lectura de confounds nativos y rutas FEAT.

Valida 73 runs con matrices; reproduce las 14 columnas a partir de fuentes.
Si existe FSF, comprueba rutas de confounds, BOLD y los ocho EVs.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys

from preparar_fsf_nativos import EVENTS, fsf_entries

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()

def rows(p,cols,n):
    if not p.is_file():raise ValueError('FALTA_'+str(p))
    output=[]
    for idx,line in enumerate(p.read_text().splitlines(),1):
        if not line.strip():continue
        vs=[float(x) for x in line.split()]
        if len(vs)!=cols or not all(math.isfinite(v) for v in vs):
            raise ValueError(f'MATRIZ_INVALIDA_{p}_LINEA_{idx}')
        output.append(vs)
    if len(output)!=n:raise ValueError(f'FILAS_{p}_{len(output)}_ESPERADAS_{n}')
    return output

def fslval(p,key):
    result=subprocess.run(['fslval',str(p),key],capture_output=True,
                          text=True,check=True)
    return float(result.stdout.split()[0])

def audit(root,croot,mroot,out,sid,run):
    issues=[]
    feat=root/sid/(run+'.feat')
    bold=feat/'filtered_func_data.nii.gz'
    confdir=croot/sid/run
    conf=confdir/'todos_confounds_nativo.txt'
    if not bold.is_file():return ['FALTA_BOLD'],False
    n=int(fslval(bold,'dim4'))
    if n<=0:return ['N_INVALIDO'],False
    try:
        mat=rows(conf,14,n)
        man=json.loads((confdir/'finalize.json').read_text())
        if (man.get('estado')!='CONFOUNDS_OK' or man.get('sujeto')!=sid or
            man.get('run')!=run or man.get('nvol')!=n or
            man.get('columnas')!=14 or man.get('sha256_confounds')!=digest(conf)):
            issues.append('MANIFIESTO_O_SHA_INVALIDO')
        qc=json.loads((confdir/'aprobacion_visual.json').read_text())
        if qc.get('aprobado') is not True:issues.append('SIN_APROBACION_VISUAL')
        if any(max(row[j] for row in mat)-min(row[j] for row in mat)<1e-12
               for j in range(14)):issues.append('COLUMNA_CONSTANTE')
        motion=rows(feat/'mc/prefiltered_func_data_mcf.par',6,n)
        deriv=rows(mroot/sid/run/'motion_deriv.par',6,n)
        wm=rows(confdir/'signal_wm_nativa.txt',1,n)
        csf=rows(confdir/'signal_csf_nativa.txt',1,n)
        delta=max(abs(deriv[t][j]-(0 if t==0 else motion[t][j]-motion[t-1][j]))
                  for t in range(n) for j in range(6))
        if delta>1e-7:issues.append(f'DERIVADAS_INVALIDAS_{delta:.3g}')
        err=max(abs(mat[t][j]-([*motion[t],*deriv[t],wm[t][0],csf[t][0]][j]))
                for t in range(n) for j in range(14))
        if err>1e-7:issues.append(f'COLUMNAS_NO_COINCIDEN_CON_FUENTES_{err:.3g}')
        # Comprobar coherencia documental de máscaras aprobadas
        prep=json.loads((confdir/'prepare.json').read_text())
        masks=prep.get('sha256_mascaras',{})
        for fn,expected in masks.items():
            file=confdir/fn
            if not file.is_file() or digest(file)!=expected:
                issues.append('MASCARA_CAMBIADA_'+fn)
        if qc.get('sha256_mascaras_aprobadas')!=masks:
            issues.append('APROBACION_MASCARAS_NO_COINCIDE')
    except (OSError,ValueError,KeyError,IndexError,json.JSONDecodeError) as e:
        issues.append(str(e))
    fsf=out/sid/(run+'_stats_only.fsf')
    if fsf.exists():
        try:
            opts=fsf_entries(fsf.read_text())
            def path(key):
                value=opts.get(key)
                if value is None:raise ValueError('FALTA_EN_FSF_'+key)
                return Path(value.strip('"'))
            if path('confoundev_files(1)')!=conf:issues.append('FSF_RUTA_CONFOUNDS_ERRONEA')
            if not path('confoundev_files(1)').is_file():issues.append('FSF_CONFOUNDS_NO_EXISTE')
            expected_copy=out/sid/(run+'.feat')
            if path('feat_files(1)')!=expected_copy:issues.append('FSF_RUTA_ENTRADA_ERRONEA')
            if (expected_copy/'filtered_func_data.nii.gz').is_file():
                if digest(expected_copy/'filtered_func_data.nii.gz')!=digest(bold):
                    issues.append('BOLD_COPIA_DIFIERE')
            for i,name in enumerate(EVENTS,1):
                ev=Path.home()/'NIFTIS_DESCOMPRIMIDOS'/sid/'evs'/('run-'+run[-1])/(name+'.txt')
                if path(f'fmri(custom{i})')!=ev:
                    issues.append('FSF_RUTA_EV_ERRONEA_'+name)
                if not ev.is_file():
                    issues.append('FSF_EV_NO_EXISTE_'+name)
            if opts.get('fmri(confoundevs)')!='1':issues.append('FSF_CONFOUNDS_DESHABILITADOS')
            if opts.get('fmri(motionevs)')!='0':issues.append('FSF_MOVIMIENTO_DUPLICADO')
        except (OSError,ValueError) as e:issues.append('FSF_'+str(e))
    return issues,fsf.is_file()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    p.add_argument('--conf-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_nativos')
    p.add_argument('--mirta-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_mirta')
    p.add_argument('--out-root',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO')
    a=p.parse_args()
    totals={'OK':0,'ERROR':0,'SIN_CONFOUNDS':0,'FSF_PRESENTE':0}
    print('SUJETO RUN ESTADO FSF DETALLE')
    for subject in sorted(a.feat_root.iterdir()):
        if not (subject.is_dir() and re.fullmatch(r'\d{4}',subject.name)):continue
        for run in ('run1','run2'):
            feat=subject/(run+'.feat')
            if not feat.is_dir():continue
            if not (a.conf_root/subject.name/run/'todos_confounds_nativo.txt').is_file():
                totals['SIN_CONFOUNDS']+=1
                print(subject.name,run,'SIN_CONFOUNDS','-', 'FEAT_INCOMPLETO_O_PENDIENTE')
                continue
            try:issues,has_fsf=audit(a.feat_root,a.conf_root,a.mirta_root,a.out_root,subject.name,run)
            except Exception as e:issues=['EXCEPCION_'+repr(e)];has_fsf=False
            if has_fsf:totals['FSF_PRESENTE']+=1
            status='ERROR' if issues else 'OK'
            totals[status]+=1
            print(subject.name,run,status,'SI' if has_fsf else 'NO', ';'.join(issues) if issues else '14_COLUMNAS_Y_FUENTES_COINCIDEN')
    print('RESUMEN',' '.join(f'{k}={v}' for k,v in totals.items()))
    print('AUDITORIA_SOLO_LECTURA')
    if totals['ERROR']:sys.exit(1)

if __name__=='__main__':main()
