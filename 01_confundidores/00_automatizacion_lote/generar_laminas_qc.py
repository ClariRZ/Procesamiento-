#!/usr/bin/env python3
"""Generar laminas PNG + indice HTML para inspeccion de 71 mascaras pendientes.

Lee solo imagenes ya preparadas; crea un directorio de visualizacion nuevo.
NO modifica NIfTI, NO aprueba QC, NO extrae senales ni ejecuta FEAT.
Requiere numpy, nibabel y matplotlib en el interprete Python utilizado.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys

try:
    import numpy as np
    import nibabel as nib
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
except ImportError as exc:
    raise SystemExit('DEPENDENCIA FALTANTE: usar el Python de FSL, p.ej. "$FSLDIR/bin/python". '+str(exc))


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


def required(path):
    if not path.is_file() or path.stat().st_size==0:
        raise RuntimeError(f'FALTA_ARCHIVO {path}')
    return path


def image3d(path):
    img=nib.as_closest_canonical(nib.load(str(required(path))))
    if len(img.shape)!=3:
        raise RuntimeError(f'NO_ES_3D {path}')
    a=np.asarray(img.dataobj,dtype=np.float32)
    if not np.isfinite(a).all():
        raise RuntimeError(f'VALORES_NO_FINITOS {path}')
    return img,a


def plane(volume, axis, point):
    if axis==2:
        return np.rot90(volume[:,:,point])
    if axis==1:
        return np.rot90(volume[:,point,:])
    return np.rot90(volume[point,:,:])


def render_one(sid,run,feat,native,output):
    man=json.loads(required(native/'prepare.json').read_text(encoding='utf-8'))
    if man.get('sujeto')!=sid or man.get('run')!=run:
        raise RuntimeError('MANIFIESTO_DE_OTRO_RUN')
    prepared=man.get('sha256_mascaras',{})
    masks={}
    for kind in ('wm','csf'):
        name=f'mask_{kind}_func.nii.gz'
        f=required(native/name)
        if prepared.get(name)!=sha(f):
            raise RuntimeError('HASH_MASCARA_CAMBIADO_'+kind)
        masks[kind]=f

    ref,base=image3d(feat/'example_func.nii.gz')
    arrays={}
    for name,p in [('brain',feat/'mask.nii.gz'),('wm',masks['wm']),('csf',masks['csf'])]:
        img,arr=image3d(p)
        if arr.shape!=base.shape or not np.allclose(img.affine,ref.affine,rtol=1e-5,atol=0.001):
            raise RuntimeError('GEOMETRIA_O_AFIN_DIFERENTE_'+name)
        arrays[name]=arr>0.5

    brain,wm,csf=(arrays[x] for x in ('brain','wm','csf'))
    if brain.sum()==0 or wm.sum()==0 or csf.sum()==0:
        raise RuntimeError('MASCARA_VACIA')
    if np.any(wm & ~brain) or np.any(csf & ~brain) or np.any(wm & csf):
        raise RuntimeError('CONTENCION_O_SOLAPAMIENTO_INCORRECTOS')
    if base[brain].size==0:
        raise RuntimeError('SIN_SENAL_CEREBRAL')
    low,high=np.percentile(base[brain],[2,98])
    if not np.isfinite([low,high]).all() or high<=low:
        raise RuntimeError('IMAGEN_FUNCIONAL_SIN_CONTRASTE')

    coords=np.where(brain)
    limits=[(int(arr.min()),int(arr.max())) for arr in coords]
    # Tres niveles axiales y planos coronal y sagital centrales.
    def slice_at(axis,fraction):
        lo,hi=limits[axis]
        return int(round(lo+(hi-lo)*fraction))
    views=[('Axial inferior',2,slice_at(2,.30)),
           ('Axial medio',2,slice_at(2,.50)),
           ('Axial superior',2,slice_at(2,.70)),
           ('Coronal',1,slice_at(1,.50)),
           ('Sagital',0,slice_at(0,.50))]
    figure,axes=plt.subplots(1,5,figsize=(16,4.2),dpi=140)
    wm_cmap=ListedColormap(['#ff982a'])
    csf_cmap=ListedColormap(['#13c8f2'])
    try:
        for ax,(title,axis,idx) in zip(axes,views):
            ax.imshow(plane(base,axis,idx),cmap='gray',vmin=low,vmax=high,
                      origin='lower',interpolation='nearest')
            for data,cmap in ((wm,wm_cmap),(csf,csf_cmap)):
                lay=np.ma.masked_where(~plane(data,axis,idx),plane(data,axis,idx).astype(int))
                ax.imshow(lay,cmap=cmap,alpha=.62,vmin=0,vmax=1,
                          origin='lower',interpolation='nearest')
            brain_slice=plane(brain,axis,idx)
            if brain_slice.any() and not brain_slice.all():
                ax.contour(brain_slice.astype(float),levels=[.5],
                           colors=['#ffffff'],linewidths=[.5])
            ax.set_title(f'{title} (corte {idx})',fontsize=9)
            ax.axis('off')
        figure.suptitle(f'{sid}/{run} · WM naranja · CSF celeste · borde cerebral blanco',fontsize=11)
        figure.tight_layout()
        filename=f'{sid}_{run}_mascaras.png'
        figure.savefig(output/filename,bbox_inches='tight',facecolor='white')
    finally:
        plt.close(figure)
    return filename,int(brain.sum()),int(wm.sum()),int(csf.sum())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feat-root',type=Path,default=Path.home()/'FEAT')
    parser.add_argument('--native-root',type=Path,default=Path.home()/'TesisDoctoral/confounds_nativos')
    parser.add_argument('--out',type=Path,default=Path.home()/'TesisDoctoral/QC_LAMINAS_CONFUNDS_20261014')
    args=parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        parser.error(f'No se sobrescribe la salida existente: {args.out}')
    candidates=[]
    for subject in sorted(args.native_root.iterdir()):
        if not subject.is_dir() or not re.fullmatch(r'\d{4}',subject.name):
            continue
        for run in ('run1','run2'):
            native=subject/run
            if (native/'prepare.json').is_file() and not (native/'aprobacion_visual.json').exists():
                candidates.append((subject.name,run,native))
    if not candidates:
        parser.error('No se encontraron mascaras pendientes de QC; no se creo salida.')
    args.out.mkdir(parents=True,exist_ok=False)
    success=[]
    failures=[]
    for sid,run,native in candidates:
        feat=args.feat_root/sid/(run+'.feat')
        try:
            result=render_one(sid,run,feat,native,args.out)
            success.append((sid,run,*result))
            print('OK',sid,run,flush=True)
        except Exception as exc:
            failures.append((sid,run,str(exc)))
            print('REVISAR',sid,run,exc,file=sys.stderr,flush=True)
    cards=[]
    for sid,run,filename,brain,wm,csf in success:
        label=html.escape(sid+'/'+run)
        cards.append('<figure><img loading="lazy" src="'+html.escape(filename)+'" alt="'+label+
                     '"><figcaption>'+label+f' | cerebro {brain} WM {wm} CSF {csf}</figcaption></figure>')
    failed_html=''.join('<li>'+html.escape(sid+'/'+run+': '+err)+'</li>' for sid,run,err in failures)
    document=(
       '<!doctype html><html lang="es"><meta charset="utf-8"><title>QC de máscaras</title>'
       '<style>body{font:16px sans-serif;margin:2rem;background:#fafafa;color:#222}'
       'figure{background:white;border:1px solid #ddd;padding:12px;margin:20px 0}'
       'img{max-width:100%;height:auto}figcaption{padding:8px}li{margin:.5em}</style>'
       '<h1>QC máscaras nativas: pendientes de aprobación visual</h1>'
       '<p>WM naranja, CSF celeste; línea blanca: contorno cerebral. '
       'La inspección requiere recorrer todos los cortes y confirmar anatomía en FSLeyes; '
       '<strong>estas láminas no aprueban automáticamente ningún run.</strong></p>'
       '<p>Generadas: '+str(len(success))+'; incidencias: '+str(len(failures))+'</p>'
       +''.join(cards)+('<h2>Incidencias</h2><ul>'+failed_html+'</ul>' if failures else '')
       +'</html>'
    )
    (args.out/'index.html').write_text(document,encoding='utf-8')
    (args.out/'resultado_qc_visual.tsv').write_text(
       'id\trun\testado\tdetalle\n'+
       ''.join(f'{sid}\t{run}\tPENDIENTE_INSPECCION_HUMANA\t{file}\n' for sid,run,file,*_ in success)+
       ''.join(f'{sid}\t{run}\tERROR_GENERACION_LAMINA\t{err}\n' for sid,run,err in failures),
       encoding='utf-8')
    print(f'LAMINAS={len(success)} ERRORES={len(failures)} CARPETA={args.out}')
    print('Abrir archivo index.html en navegador; no hay aprobaciones automáticas.')
    if failures:
        raise SystemExit(1)


if __name__=='__main__':
    main()
