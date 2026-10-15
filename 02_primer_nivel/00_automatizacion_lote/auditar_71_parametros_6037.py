#!/usr/bin/env python3
"""Audita los 71 runs frente al 6037, en SOLO LECTURA; no ejecuta FSL.
Compara Registration y Pre-stats del original, FSF estadistico y copias.
"""
from pathlib import Path
import hashlib
import math
import re
import subprocess
import sys
from collections import Counter

HOME=Path.home()
ORIG=HOME/'FEAT'
LOTE=HOME/'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO'
CONF=HOME/'TesisDoctoral/confounds_nativos'
EVROOT=HOME/'NIFTIS_DESCOMPRIMIDOS'
TEMPLATE=HOME/'TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/6037_run1_nativo_INPUTTYPE1.fsf'
REG=('reginitial_highres_yn','reghighres_yn','reghighres_search','reghighres_dof',
     'regstandard_yn','regstandard','regstandard_search','regstandard_dof',
     'regstandard_nonlinear_yn','regstandard_nonlinear_warpres')
PRE=('analysis','ndelete','paradigm_hp','smooth','temphp_yn','templp_yn','tr','npts','st')
STATS={'level':'1','analysis':'2','inputtype':'1','filtering_yn':'0',
       'stats_yn':'1','prewhiten_yn':'1','motionevs':'0','confoundevs':'1',
       'reghighres_yn':'0','regstandard_yn':'0','evs_orig':'8','evs_real':'16',
       'ncon_orig':'21','ncon_real':'21'}
EVS=('AtencionPlena','ExperimNeg','ExperimNeutra','Likert',
     'ObservaNeg','ObservaNeutra','Reinterpreta','Suprime')
FILES=('reg/example_func2highres.mat','reg/highres2example_func.mat',
       'reg/highres2standard_warp.nii.gz','reg/example_func2standard_warp.nii.gz',
       'reg/standard.nii.gz','mask.nii.gz','filtered_func_data.nii.gz')
CHANGEABLE={'feat_files(1)','confoundev_files(1)','fmri(outputdir)',
            'fmri(tr)','fmri(npts)','fmri(totalVoxels)'}
CHANGEABLE.update('fmri(custom%d)'%i for i in range(1,9))

def settings(p):
    if not p.is_file() or p.stat().st_size==0:
        raise ValueError('FSF_FALTANTE: '+str(p))
    data={}
    for line in p.read_text(errors='replace').splitlines():
        m=re.match(r'^set\s+(fmri\([^)]+\)|feat_files\(1\)|confoundev_files\(1\))\s+(.+?)\s*$',line)
        if m:
            key,val=m.groups()
            if key in data: raise ValueError('FSF_CLAVE_DUPLICADA: '+key)
            data[key]=val.strip('"')
    return data

def field(fsf,key):
    return fsf.get('fmri('+key+')','<AUSENTE>')

def comparable(a,b):
    if a==b:return True
    try:return math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-5)
    except (ValueError,TypeError):return False

def hash_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(1<<20),b''):h.update(part)
    return h.digest()

def has(p):
    return p.is_file() and p.stat().st_size>0

def fslval(img,key):
    result=subprocess.run(['fslval',str(img),key],capture_output=True,text=True,check=True,timeout=40)
    return float(result.stdout.strip().split()[0])

def validate_matrix(p,n,w,issues):
    if not has(p):return
    txt=p.read_text(errors='replace')
    for key,expected in (('NumPoints',n),('NumWaves',w)):
        if key=='NumPoints' and p.name=='design.con':key='NumContrasts';expected=21
        match=re.search(r'^/'+key+r'\s+(\d+)\s*$',txt,flags=re.M)
        if not match or int(match.group(1))!=expected:
            issues.append(p.name+':'+key+' INCORRECTO')

def main():
    ref=settings(ORIG/'6037/run1.feat/design.fsf')
    ref2=settings(ORIG/'6037/run2.feat/design.fsf')
    template=settings(TEMPLATE)
    for key in REG+PRE:
        if not comparable(field(ref,key),field(ref2,key)):
            raise RuntimeError('REFERENCIA_6037_RUNS_DIFIEREN: '+key)
    for key,val in STATS.items():
        if field(template,key)!=val:
            raise RuntimeError('PLANTILLA_6037_INCORRECTA: '+key)

    targets=[]
    for subj in sorted(ORIG.iterdir()):
        if subj.is_dir() and re.fullmatch(r'\d{4}',subj.name) and subj.name!='6037':
            for run in ('run1','run2'):
                folder=subj/(run+'.feat')
                if folder.is_dir() and has(folder/'filtered_func_data.nii.gz'):
                    targets.append((subj.name,run))
    if len(targets)!=71:
        raise RuntimeError('SE_ESPERABAN_71_RUNS; HAY_'+str(len(targets)))

    counters=Counter()
    for sid,run in targets:
        errs=[]; notes=[]
        try:
            original=ORIG/sid/(run+'.feat')
            copy=LOTE/sid/(run+'.feat')
            fsfpath=LOTE/sid/(run+'_stats_only.fsf')
            conf=CONF/sid/run/'todos_confounds_nativo.txt'
            p=settings(original/'design.fsf')
            model=settings(fsfpath)
            for key in REG:
                if not comparable(field(p,key),field(ref,key)):
                    errs.append('REG_'+key+':'+field(p,key)+' (6037:'+field(ref,key)+')')
            for key in PRE:
                if not comparable(field(p,key),field(ref,key)):
                    value=field(p,key)
                    if sid=='5017' and run=='run1' and key=='st' and value=='0':
                        notes.append('SLICE_TIMING_5017_RUN1=0;6037=5')
                    else:
                        errs.append('PRE_'+key+':'+value+' (6037:'+field(ref,key)+')')
            for key,expected in STATS.items():
                if field(model,key)!=expected:errs.append('STATS_'+key+'!='+expected)
            for key,val in template.items():
                if key not in CHANGEABLE and not comparable(model.get(key,'<AUSENTE>'),val):
                    errs.append('FSF_DIFIERE_DE_PLANTILLA: '+key)
            if model.get('feat_files(1)')!=str(copy):
                errs.append('RUTA_COPIA_FSF_INCORRECTA')
            if model.get('confoundev_files(1)')!=str(conf):
                errs.append('RUTA_CONFOUNDS_FSF_INCORRECTA')
            for i,name in enumerate(EVS,1):
                ev=EVROOT/sid/'evs'/('run-'+run[-1])/(name+'.txt')
                if model.get('fmri(custom%d)'%i)!=str(ev) or not has(ev):
                    errs.append('EV_%d_FALTA_O_APUNTA_OTRO_RUN'%i)
            if not has(conf):errs.append('CONFOUNDS_NO_EXISTE')
            else:
                rows=[l.split() for l in conf.read_text().splitlines() if l.strip()]
                if len(rows)!=387 or any(len(row)!=14 for row in rows):
                    errs.append('CONFOUNDS_DIMENSIONES_INVALIDAS')
                else:
                    try:
                        if not all(math.isfinite(float(v)) for row in rows for v in row):
                            errs.append('CONFOUNDS_NO_FINITOS')
                    except ValueError:errs.append('CONFOUNDS_NO_NUMERICOS')
            if not copy.is_dir() or copy.is_symlink():errs.append('COPIA_FEAT_FALTANTE')
            else:
                for rel in FILES:
                    left,right=original/rel,copy/rel
                    if not has(left) or not has(right):errs.append('FALTA_ARCHIVO_REG_O_BOLD: '+rel)
                    elif hash_file(left)!=hash_file(right):
                        errs.append('COPIA_DISTINTA_DEL_ORIGINAL: '+rel)
                validate_matrix(copy/'design.mat',387,30,errs)
                validate_matrix(copy/'design.con',21,30,errs)
            n=fslval(original/'filtered_func_data.nii.gz','dim4')
            tr=fslval(original/'filtered_func_data.nii.gz','pixdim4')
            if n!=387 or abs(tr-2)>1e-5:errs.append('BOLD_NPTS_O_TR_INCORRECTOS')
        except (OSError,ValueError,KeyError,subprocess.SubprocessError) as e:
            errs.append('AUDITOR_NO_PUDO_COMPROBAR: '+str(e))
            copy=LOTE/sid/(run+'.feat')
        counts=tuple(sum(has(copy/'stats'/(prefix+str(k)+'.nii.gz')) for k in range(1,22))
                     for prefix in ('cope','varcope','zstat'))
        if counts==(21,21,21):counters['STATS_COMPLETAS']+=1
        elif any(counts):counters['STATS_PARCIALES']+=1
        else:counters['STATS_AUSENTES']+=1
        status='ERROR' if errs else ('AVISO' if notes else 'OK')
        counters[status]+=1
        print(sid,run,status,'COPE/VARCOPE/ZSTAT='+str(counts),flush=True)
        for error in errs:print('  ERROR:',error)
        for note in notes:print('  AVISO:',note)
    print('RESUMEN runs=71 OK={OK} AVISO={AVISO} ERROR={ERROR} STATS_COMPLETAS={STATS_COMPLETAS} STATS_PARCIALES={STATS_PARCIALES} STATS_AUSENTES={STATS_AUSENTES}'.format(
          **{k:counters[k] for k in ('OK','AVISO','ERROR','STATS_COMPLETAS','STATS_PARCIALES','STATS_AUSENTES')}))
    print('SOLO LECTURA. NO SE EJECUTO NI MODIFICO FEAT.')
    return 1 if counters['ERROR'] else 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print('DETENIDO:',e,file=sys.stderr);sys.exit(2)
