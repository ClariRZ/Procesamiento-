#!/usr/bin/env python3
"""Integra reportes de preprocesamiento y GLM sin tocar report.html de FEAT.

Solo copia HTML y recursos visuales (no NIfTI) de la FEAT original a una
subcarpeta nueva de la FEAT preparada. Crea un indice unico.
Por defecto: simulacion. Usar --execute para crear archivos nuevos.
"""
from pathlib import Path
from html import escape
import argparse
import json
import re
import shutil
import sys

VISUAL_EXT={'.html','.htm','.png','.gif','.jpg','.jpeg','.svg','.css','.js'}
EXCLUDE_PARTS={'stats','logs','.files'}
DESTNAME='reporte_preprocesamiento_original'
INDEXNAME='reporte_integrado.html'

def existing_sources(original):
    for p in original.rglob('*'):
        if not p.is_file() or p.is_symlink():continue
        if p.suffix.lower() not in VISUAL_EXT:continue
        rel=p.relative_to(original)
        if any(part in EXCLUDE_PARTS for part in rel.parts):continue
        yield p,rel

def run(args):
    if args.solo not in ('all','5015'):raise ValueError('solo acepta all o 5015')
    if not args.out_root.is_dir():raise ValueError('No existe carpeta de salida')
    candidates=ok=errors=0
    for marker in sorted(args.out_root.glob('*/run*.feat/ORQUESTADOR_PREPARADO.json')):
        dest=marker.parent
        meta=json.loads(marker.read_text())
        sid,run=meta.get('subject'),meta.get('run')
        if args.solo=='5015' and sid!='5015':continue
        if not re.fullmatch(r'\d{4}',str(sid)) or run not in ('run1','run2'):continue
        if sid=='6037':continue
        original=(args.feat_root/sid/(run+'.feat'))
        if original.resolve()==dest.resolve() or not original.is_dir():
            raise RuntimeError(f'Original ausente o ruta insegura: {sid}/{run}')
        if dest.is_symlink() or dest.resolve().is_relative_to(args.feat_root.resolve()):
            raise RuntimeError(f'Salida insegura: {dest}')
        if meta.get('original')!=str(original):
            raise RuntimeError(f'Marcador de otro origen: {dest}')
        if not (original/'report.html').is_file():
            print('SIN_REPORT_ORIGINAL',sid,run);errors+=1;continue
        sub=dest/DESTNAME
        index=dest/INDEXNAME
        if sub.exists() or sub.is_symlink() or index.exists() or index.is_symlink():
            print('YA_EXISTE_SIN_SOBRESCRIBIR',sid,run);continue
        sources=list(existing_sources(original))
        if not sources:
            print('SIN_ARCHIVOS_VISUALES',sid,run);errors+=1;continue
        candidates+=1
        if not args.execute:
            print('PLAN',sid,run,'archivos_visuales',len(sources))
            continue
        try:
            sub.mkdir(exist_ok=False)
            for src,rel in sources:
                tgt=sub/rel
                tgt.parent.mkdir(parents=True,exist_ok=True)
                with src.open('rb') as fin, tgt.open('xb') as fout:
                    shutil.copyfileobj(fin,fout)
            # Mantener los reportes originales intactos; indice independiente.
            page='''<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Reporte integrado FEAT - SUBJECT RUN</title></head><body>
<h1>Reporte FEAT: SUBJECT RUN</h1>
<p>El preprocesamiento se efectuó previamente; el nuevo FEAT ejecuta estadísticas únicamente.</p>
<h2>Preprocesamiento y registración originales</h2>
<p><a href="reporte_preprocesamiento_original/report.html">Abrir reporte de preprocesamiento completo</a>
 · <a href="reporte_preprocesamiento_original/report_prestats.html">Pre-stats</a>
 · <a href="reporte_preprocesamiento_original/report_reg.html">Registration</a></p>
<h2>Estadísticas de primer nivel</h2>
<p><a href="report.html">Abrir reporte estadístico FEAT</a>
 · <a href="report_stats.html">Stats</a>
 · <a href="report_poststats.html">Post-stats</a></p>
<p>Estos reportes corresponden a etapas distintas. Los archivos originales no se han modificado.</p>
</body></html>'''.replace('SUBJECT',escape(sid)).replace('RUN',escape(run))
            with index.open('x',encoding='utf-8') as f:f.write(page)
            ok+=1
            print('INTEGRADO',sid,run,index)
        except Exception as exc:
            # Nunca borrar evidencias parciales, ni sobrescribir.
            print('ERROR',sid,run,repr(exc),file=sys.stderr)
            errors+=1
    print(f'RESUMEN candidatos={candidates} integrados={ok} errores={errors} modo={"EJECUCION" if args.execute else "PLAN"}')
    if errors:sys.exit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true')
    p.add_argument('--solo',default='all',choices=('all','5015'))
    p.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    p.add_argument('--out-root',type=Path,default=Path.home()/'TesisDoctoral/PRIMER_NIVEL_LOTE_NATIVO')
    run(p.parse_args())
