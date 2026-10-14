#!/usr/bin/env python3
"""Orquestador conservador de FEAT nativo. Datos siempre locales.

Acciones: plan, prepare-all, run-all, status.
Ejecutar acciones mutables sólo con --execute. No relanzar pilotos ni pisar resultados.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from preparar_fsf_nativos import ready, make, check_options, EXACT, fsf_entries, good, hash_file

ESSENTIAL = ('filtered_func_data.nii.gz', 'mask.nii.gz', 'example_func.nii.gz',
             'reg/example_func2highres.mat', 'reg/highres2standard_warp.nii.gz',
             'reg/example_func2standard_warp.nii.gz', 'reg/standard.nii.gz')
EXCLUDE = {'stats', 'logs', '.files', 'reg_standard',\n           'design.mat', 'design.con', 'design.fts', 'design.frf',\n           'design.min', 'design.trg', 'design.png', 'design.ppm',\n           'design_cov.png', 'design_cov.ppm', 'design.gif'}
REPORTS = ('report.html', 'report_log.html', 'report_stats.html',
           'report_poststats.html', 'report_prestats.html', 'report_reg.html')
GUARD = 'ORQUESTADOR_PREPARADO.json'


def sha(path):
    return hash_file(path)


def pairs(args):
    for subject in sorted(args.feat_root.iterdir()):
        if subject.is_dir() and re.fullmatch(r'\d{4}', subject.name):
            for run in ('run1','run2'):
                if (subject / (run + '.feat')).is_dir():
                    yield subject.name, run


def paths(args, sid, run):
    root = args.out_root / sid
    return (args.feat_root / sid / (run+'.feat'),
            root / (run+'.feat'), root / (run+'_stats_only.fsf'))


def preflight(args):
    if not args.feat_root.is_dir():
        raise RuntimeError('FALTA_FEAT_ROOT')
    if args.out_root.resolve().is_relative_to(args.feat_root.resolve()):
        raise RuntimeError('SALIDA_DENTRO_DE_FEAT')
    if args.template.resolve().is_relative_to(args.feat_root.resolve()):
        raise RuntimeError('PLANTILLA_DENTRO_DE_FEAT')


def marker(args,sid,run):
    _,dest,_ = paths(args,sid,run)
    p=dest/GUARD
    if not p.is_file():
        raise RuntimeError('FALTA_MARCADOR_ORQUESTADOR')
    obj=json.loads(p.read_text())
    if obj.get('subject')!=sid or obj.get('run')!=run:
        raise RuntimeError('MARCADOR_DE_OTRO_RUN')
    return obj


def prepare(args,sid,run):
    state,why=ready(args,sid,run)
    if state!='APTO_PARA_PREPARAR_FSF':
        raise RuntimeError(state+':'+why)
    original,dest,fsf=paths(args,sid,run)
    # El generador del repositorio valida eventos, hashes de confounds y geometría.
    make(args,sid,run)
    if dest.exists() or dest.is_symlink():
        raise RuntimeError('DESTINO_YA_EXISTE')
    # Copiar íntegro el preprocesamiento, pero nunca las estadísticas existentes.
    # Copiamos en directorio temporal y lo movemos sólo después de cotejar.
    temp=dest.with_name(dest.name+'.copia_parcial')
    if temp.exists() or temp.is_symlink():
        raise RuntimeError('COPIA_PARCIAL_EXISTE_REVISAR')
    def ignore(folder,names):
        if Path(folder)==original:
            return set(names)&(EXCLUDE|set(REPORTS))
        return set()
    try:
        shutil.copytree(original,temp,symlinks=False,ignore=ignore)
        for rel in ESSENTIAL:
            a=original/rel
            b=temp/rel
            if not good(a) or not good(b) or sha(a)!=sha(b):
                raise RuntimeError('COPIA_NO_COINCIDE:'+rel)
        if (temp/'stats').exists():
            raise RuntimeError('ESTADISTICAS_ANTIGUAS_EN_COPIA')
        payload={'subject':sid,'run':run,'original':str(original),
                 'fsf':str(fsf),'source_hashes':{p:sha(original/p) for p in ESSENTIAL},
                 'template_hash':sha(args.template),
                 'confounds_hash':sha(args.conf_root/sid/run/'todos_confounds_nativo.txt'),
                 'qc_visual':'registrado previamente, no comprobado por este orquestador'}
        (temp/GUARD).write_text(json.dumps(payload,indent=2)+'\n')
        temp.rename(dest)
    except Exception:
        # Se conserva una copia parcial para permitir auditoría; NUNCA borrar automáticamente.
        raise
    print('PREPARADO',sid,run,fsf,dest)


def validate_prepared(args,sid,run):
    original,dest,fsf=paths(args,sid,run)
    obj=marker(args,sid,run)
    if not fsf.is_file() or not dest.is_dir():
        raise RuntimeError('FALTA_FSF_O_COPIA')
    text=fsf.read_text()
    check_options(text,EXACT)
    fields=fsf_entries(text)
    if fields.get('feat_files(1)')!=json.dumps(str(dest)):
        raise RuntimeError('FSF_NO_APUNTA_A_COPIA')
    if fields.get('confoundev_files(1)')!=json.dumps(str(args.conf_root/sid/run/'todos_confounds_nativo.txt')):
        raise RuntimeError('FSF_CONFOUNDS_INCORRECTOS')
    if obj['template_hash']!=sha(args.template):
        raise RuntimeError('PLANTILLA_CAMBIADA')
    if obj['confounds_hash']!=sha(args.conf_root/sid/run/'todos_confounds_nativo.txt'):
        raise RuntimeError('CONFOUNDS_CAMBIADOS')
    for rel,h in obj['source_hashes'].items():
        if not good(original/rel) or not good(dest/rel):
            raise RuntimeError('FALTA_ESSENTIAL:'+rel)
        if sha(original/rel)!=h or sha(dest/rel)!=h:
            raise RuntimeError('ORIGINAL_O_COPIA_CAMBIADOS:'+rel)
    return fsf,dest


def result_status(dest):
    stats=dest/'stats'
    cope=sum((stats/f'cope{i}.nii.gz').is_file() for i in range(1,22))
    varcope=sum((stats/f'varcope{i}.nii.gz').is_file() for i in range(1,22))
    zstat=sum((stats/f'zstat{i}.nii.gz').is_file() for i in range(1,22))
    return cope,varcope,zstat


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('plan','prepare-all','run-all','status'))
    p.add_argument('--execute',action='store_true')
    p.add_argument('--confirm',default='')
    p.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    p.add_argument('--conf-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_nativos')
    p.add_argument('--evs-root',type=Path,default=Path.home()/'NIFTIS_DESCOMPRIMIDOS')
    p.add_argument('--out-root',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO')
    p.add_argument('--template',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_NATIVO_6037/6037_run1_nativo_INPUTTYPE1.fsf')
    p.add_argument('--limit',type=int,default=0,help='Máximo de runs mutables (0=sin límite)')
    args=p.parse_args()
    preflight(args)
    if args.limit<0:raise RuntimeError('LIMIT_INVALIDO')
    mut=args.action in ('prepare-all','run-all')
    expected='PREPARAR_LOTE' if args.action=='prepare-all' else 'EJECUTAR_FEAT_LOTE'
    if mut and (not args.execute or args.confirm!=expected):
        raise RuntimeError('SIN_CONFIRMACION: usar --execute --confirm '+expected)
    if args.action=='run-all' and shutil.which('feat') is None:
        raise RuntimeError('FALTA_COMANDO_FEAT')
    ok=blocked=done=0
    for sid,run in pairs(args):
        original,dest,fsf=paths(args,sid,run)
        if args.action in ('plan','prepare-all'):
            state,detail=ready(args,sid,run)
            if state!='APTO_PARA_PREPARAR_FSF':
                print(sid,run,state,detail)
                blocked+=1
                continue
            if args.action=='plan':
                print(sid,run,'APTO',detail)
                ok+=1;continue
            if args.limit and done>=args.limit:break
            try:
                prepare(args,sid,run);done+=1
            except Exception as e:
                print('ERROR_PREPARAR',sid,run,str(e),file=sys.stderr);blocked+=1
        else:
            if (sid,run) in (('6037','run1'),('6037','run2')):
                print(sid,run,'PILOTO_NO_RELANZAR')
                continue
            if not (dest/GUARD).exists():
                if args.action=='status':print(sid,run,'SIN_COPIA_ORQUESTADA')
                continue
            try:
                fsf,dest=validate_prepared(args,sid,run)
                counts=result_status(dest)
                if counts==(21,21,21):
                    print(sid,run,'RESULTADOS_PRESENTES','COPE/VARCOPE/ZSTAT=21/21/21');ok+=1;continue
                if args.action=='status':
                    print(sid,run,'PREPARADO_O_INCOMPLETO',counts);continue
                if any(counts) or (dest/'design.mat').exists() or (dest/'logs').exists():
                    raise RuntimeError('INDICIOS_EJECUCION_PREVIA_NO_RELANZAR')
                if args.limit and done>=args.limit:break
                # Stats-only se ejecuta únicamente sobre la copia de este orquestador.
                print('LANZANDO_FEAT',sid,run,flush=True)
                subprocess.run(['feat',str(fsf)],check=True)
                counts=result_status(dest)
                if counts!=(21,21,21):
                    raise RuntimeError('SALIDA_INCOMPLETA:'+str(counts))
                if sha(dest/'mask.nii.gz')!=marker(args,sid,run)['source_hashes']['mask.nii.gz']:
                    raise RuntimeError('MASCARA_CAMBIADA_REVISAR')
                print('FEAT_OK',sid,run,counts);done+=1
            except Exception as e:
                print('ERROR',sid,run,str(e),file=sys.stderr);blocked+=1
    print(f'RESUMEN aptos_o_completos={ok} procesados={done} incidencias={blocked}')
    if blocked and args.action!='plan':
        sys.exit(1)


if __name__=='__main__':
    try:main()
    except Exception as e:
        print('DETENIDO:',e,file=sys.stderr);sys.exit(1)
