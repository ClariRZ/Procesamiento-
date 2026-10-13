#!/usr/bin/env python3
"""Primer nivel FEAT nativo: reutiliza exactamente los EV/contrastes del FSF histórico.

FASES: auditar -> preparar -> diseno -> ejecutar -> verificar.
No modifica el FEAT de entrada. No transforma el BOLD a MNI. No permite lotes.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

import numpy as np

HERE = Path(__file__).resolve().parent
CONFOUND_SCRIPT = HERE.parents[1] / '01_confundidores' / 'automatizacion'
sys.path.insert(0, str(CONFOUND_SCRIPT))
import confundidores as cf  # script probado de la etapa anterior

EVS = ('AtencionPlena', 'ExperimNeg', 'ExperimNeutra', 'Likert',
       'ObservaNeg', 'ObservaNeutra', 'Reinterpreta', 'Suprime')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_fsf(path):
    require(path.is_file(), f'Falta FSF histórico: {path}')
    values = {}
    occurrence = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        match = re.match(r'^\s*set\s+(\S+)\s+(.+?)\s*$', line)
        if match:
            key = match.group(1)
            val = match.group(2)
            values[key] = val[1:-1] if val.startswith('"') and val.endswith('"') else val
            occurrence[key] = occurrence.get(key, 0) + 1
    require(bool(values), f'FSF vacío: {path}')
    return values, occurrence


def update_fsf(text, changes):
    """Reemplaza claves, conservando los demás ajustes originales sin reinterpretarlos."""
    seen = set()
    new = []
    for line in text.splitlines():
        m = re.match(r'^\s*set\s+(\S+)\s+(.+?)\s*$', line)
        if not m or m.group(1) not in changes:
            new.append(line)
            continue
        key = m.group(1)
        require(key not in seen, f'Clave FSF duplicada: {key}')
        new.append(f'set {key} {changes[key]}')
        seen.add(key)
    require(set(changes) == seen, 'FSF incompleto, faltan: ' + str(sorted(set(changes) - seen)))
    return '\n'.join(new) + '\n'


def quote_tcl(path):
    value = str(path)
    require(not any(c in value for c in '\n\r{}[]$;"\\'),
            'Ruta incompatible con sintaxis Tcl segura: ' + value)
    return '"' + value + '"'


def keyfloat(values, name):
    require(name in values, f'Falta configuración FSF: {name}')
    return float(values[name])


def expected_paths(args):
    require(len(args.sujeto) == 4 and args.sujeto.isdigit(), 'Sujeto debe tener 4 dígitos')
    require(args.run in (1, 2), 'Solo run1 o run2')
    home = Path.home()
    feat = Path(args.feat or (home / 'Escritorio' / args.sujeto / f'run{args.run}.feat')).expanduser().resolve()
    fsf = args.fsf
    if not fsf:
        require(args.sujeto == '6037' and args.run == 1,
                'Para otros runs indicar --fsf con el diseño real de ESE run; nunca asumir el de run1.')
        fsf = home / 'Escritorio' / '6037' / 'run1_firstlevel.feat' / 'design.fsf'
    fsf = Path(fsf).expanduser().resolve()
    evdir = Path(args.evdir or (home / 'NIFTIS_DESCOMPRIMIDOS' / args.sujeto / 'evs' / f'run-{args.run}')).expanduser().resolve()
    root = Path(args.trabajo).expanduser().resolve()
    out = root / args.sujeto / f'run{args.run}'
    pre_copy = out / '02_primer_nivel' / 'entrada_nativa.feat'
    design = out / '02_primer_nivel' / 'diseno_run_nativo.fsf'
    provenance = out / '02_primer_nivel' / 'diseno_run_nativo.procedencia.json'
    outputbase = out / '02_primer_nivel' / 'run_firstlevel_nativo'
    actual_output = Path(str(outputbase) + '.feat')
    confdir = out / '01_confundidores' / 'finales'
    confound = confdir / 'todos_confounds_nativo.txt'
    for path in (out, pre_copy, design, actual_output):
        require(feat != path and feat not in path.parents and path not in feat.parents,
                'El área de trabajo debe estar fuera del FEAT original')
    return dict(feat=feat, fsf=fsf, evdir=evdir, root=out, pre_copy=pre_copy,
                design=design, provenance=provenance, outputbase=outputbase,
                output=actual_output, confound=confound, confdir=confdir)


def validate_model(fsf_path, npts, tr, evdir):
    original, occurrences = read_fsf(fsf_path)
    relevant = ('fmri(level)', 'fmri(analysis)', 'fmri(evs_orig)', 'fmri(evs_real)',
                'fmri(ncon_orig)', 'fmri(ncon_real)', 'fmri(npts)', 'fmri(tr)',
                'fmri(ndelete)', 'fmri(prewhiten_yn)')
    for key in relevant:
        require(occurrences.get(key) == 1, f'{key} falta o está repetida')
    expect = {'fmri(level)': 1, 'fmri(analysis)': 2, 'fmri(evs_orig)': 8,
              'fmri(evs_real)': 16, 'fmri(ncon_orig)': 21,
              'fmri(ncon_real)': 21, 'fmri(ndelete)': 0,
              'fmri(prewhiten_yn)': 1}
    for key, val in expect.items():
        require(keyfloat(original, key) == val, f'FSF histórico no coincide: {key} (esperado {val})')
    require(keyfloat(original, 'fmri(npts)') == npts, 'FSF histórico y volúmenes nativos no coinciden')
    require(abs(keyfloat(original, 'fmri(tr)') - tr) < 1e-4, 'TR histórico y nativo no coinciden')
    require(original.get('fmri(motionevs)') == '0', 'No duplicar parámetros de movimiento')
    require(original.get('fmri(confoundevs)') == '1', 'FSF histórico no usaba confounds explícitos')
    files, hashes = [], {}
    for index, name in enumerate(EVS, 1):
        require(original.get(f'fmri(evtitle{index})') == name,
                f'Orden de EV incompatible: {index}')
        for setting, expected in [('shape', 3), ('convolve', 3), ('deriv_yn', 1)]:
            require(keyfloat(original, f'fmri({setting}{index})') == expected,
                    f'EV{index}: {setting} distinto del modelo histórico')
        ev = evdir / (name + '.txt')
        require(ev.is_file(), f'Falta evento: {ev}')
        table = np.loadtxt(ev, ndmin=2)
        require(table.ndim == 2 and table.shape[1] == 3 and len(table) > 0,
                f'EV debe tener formato onset/duración/valor: {ev}')
        require(np.isfinite(table).all() and np.all(table[:, 0] >= 0) and
                np.all(table[:, 1] >= 0) and np.all(table[:, 0] + table[:, 1] <= npts * tr + .05),
                f'EV fuera de los {npts * tr:.3f} segundos del BOLD: {ev}')
        require(np.any(table[:, 2] != 0), f'EV sin amplitud: {ev}')
        hashes[str(ev)] = cf.digest(ev)
        files.append(ev)
    for i in range(1, 22):
        require(bool(original.get(f'fmri(conname_orig.{i})')),
                f'Falta nombre del contraste {i}')
        for ev in range(1, 9):
            weight = keyfloat(original, f'fmri(con_orig{i}.{ev})')
            real = keyfloat(original, f'fmri(con_real{i}.{ev*2-1})')
            derivative = keyfloat(original, f'fmri(con_real{i}.{ev*2})')
            require(np.isfinite([weight, real, derivative]).all() and
                    abs(real-weight) < 1e-8 and abs(derivative) < 1e-8,
                    f'COPE{i} EV{ev}: pesos no coinciden con derivadas temporales')
    return original, files, hashes


def verify_inputs(args):
    loc = expected_paths(args)
    if args.accion in ('preparar', 'diseno', 'ejecutar'):
        require(f'{args.sujeto}/{args.run}' not in cf.PENDIENTES_QC,
                'Run pendiente de revisión humana según historial: no generar nuevos análisis')
    pre = loc['feat']
    cfgfile = pre / 'design.fsf'
    require(pre.is_dir() and cfgfile.is_file(), f'No hay FEAT preprocesado: {pre}')
    cfg, _ = read_fsf(cfgfile)
    require(cfg.get('fmri(analysis)') == '1', 'Se requiere FEAT sólo preprocesamiento')
    require(not (pre / 'stats').exists(), 'FEAT ya tiene stats: no reutilizarlo como preproc')
    require(cfg.get('fmri(ndelete)') == '0', 'Volúmenes eliminados; revisar origen EV')
    fp = cf.source_files(pre)
    for key, file in fp.items():
        require(file.is_file() and file.stat().st_size > 0, 'Falta archivo de FEAT: ' + str(file))
    bold = cf.nifti(fp['bold'])
    example = cf.nifti(fp['func_ref'])
    brainmask = cf.nifti(fp['func_mask'])
    require(len(bold.shape) == 4, 'BOLD nativo debe ser 4D')
    cf.same_grid(bold, example, 'example_func vs BOLD')
    cf.same_grid(bold, brainmask, 'mask vs BOLD')
    n = bold.shape[3]
    tr = float(bold.header.get_zooms()[3])
    require(cfg.get('fmri(npts)') is not None and int(cfg['fmri(npts)']) == n,
            'Dim4 incompatible con preprocesamiento')
    require(abs(float(cfg['fmri(tr)']) - tr) < 1e-4,
            'TR del preprocesamiento incompatible con cabecera')
    require(float(cfg.get('fmri(smooth)', '-1')) == 8.0 and
            float(cfg.get('fmri(paradigm_hp)', '-1')) == 100.,
            'El piloto 6037 debe documentar previamente cualquier cambio en suavizado/HP')
    original, evfiles, evhashes = validate_model(loc['fsf'], n, tr, loc['evdir'])
    final = loc['confdir'] / 'FINALIZADO.json'
    approval = loc['root'] / '01_confundidores' / 'APROBACION_VISUAL.json'
    require(final.is_file() and approval.is_file(),
            'Falta completar y aprobar confusores nativos del MISMO sujeto/run')
    info = json.loads(final.read_text(encoding='utf-8'))
    appr = json.loads(approval.read_text(encoding='utf-8'))
    require(info['sujeto'] == args.sujeto and info['run'] == args.run and
            info['espacio_extraccion'] == 'funcional_nativo', 'Confusores de otro run o espacio')
    require(appr['sujeto'] == args.sujeto and appr['run'] == args.run and
            appr['revision_registro'] == 'APROBADO_POR_HUMANO' and
            appr['revision_mascaras'] == 'APROBADO_POR_HUMANO',
            'QC humano de confusores no confirmado')
    require(info['aprobacion_visual_sha256'] == cf.digest(approval),
            'Cambió el archivo de aprobación visual')
    require(info['bold_sha256'] == cf.digest(fp['bold']) and
            info['motion_sha256'] == cf.digest(fp['motion']),
            'La entrada BOLD o el movimiento cambió desde confusores')
    require(info['matriz_sha256'] == cf.digest(loc['confound']),
            'Cambió la matriz desde finalize')
    cf.load_table(loc['confound'], 14, n)
    # Valida de nuevo que las 12 primeras columnas sean el movimiento y derivadas reales.
    mat = np.loadtxt(loc['confound'], ndmin=2)
    motion = cf.load_table(fp['motion'], 6, n)
    diff = np.vstack((np.zeros((1, 6)), np.diff(motion, axis=0)))
    require(np.allclose(mat[:, :6], motion, atol=1e-6, rtol=0) and
            np.allclose(mat[:, 6:12], diff, atol=1e-6, rtol=0),
            'Movimientos/derivadas dentro de confounds no coinciden')
    return loc, n, tr, original, evfiles, evhashes


def audit(args):
    loc, n, tr, original, evfiles, _ = verify_inputs(args)
    print(json.dumps({'estado': 'INSUMOS_LISTOS_PARA_PREPARAR_NO_APROBACION_GLM',
                      'sujeto': args.sujeto, 'run': args.run,
                      'preproc': str(loc['feat']), 'fsf_historico': str(loc['fsf']),
                      'nvol': n, 'TR': tr, 'evs': [p.name for p in evfiles],
                      'contrastes': int(original['fmri(ncon_orig)']),
                      'confounds': str(loc['confound']),
                      'entrada_glm': 'FEAT preprocesado NATIVO, copia independiente'},
                     indent=2, ensure_ascii=False))


def prepare(args):
    loc, n, tr, original, evfiles, evhashes = verify_inputs(args)
    require(not loc['pre_copy'].exists() and not loc['design'].exists() and
            not loc['provenance'].exists() and not loc['output'].exists() and
            not Path(str(loc['outputbase']) + '+.feat').exists(),
            'Ya hay archivos/diseños/salidas; NO sobrescribir')
    require(not loc['outputbase'].exists(), 'Salida FEAT base ya existe')
    dest = loc['pre_copy']
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_name('.entrada_nativa_en_copia_' + uuid.uuid4().hex[:10] + '.feat')
    def ignore(dirname, names):
        excluded = {'stats', 'tsplot', 'reg_standard'}
        return [name for name in names if name in excluded or
                name.startswith('filtered_func_data_MNI')]
    try:
        shutil.copytree(loc['feat'], temp, symlinks=True, ignore=ignore)
        require((temp / 'filtered_func_data.nii.gz').is_file(), 'No se copió el BOLD nativo')
        require(not (temp / 'stats').exists(), 'Copia contiene stats')
        require(cf.digest(temp / 'filtered_func_data.nii.gz') ==
                cf.digest(loc['feat'] / 'filtered_func_data.nii.gz'),
                'La copia BOLD no es idéntica al origen')
        temp.rename(dest)
    except Exception:
        print('Copia parcial para investigar, sin tocar fuente: ' + str(temp), file=sys.stderr)
        raise
    changes = {
        'fmri(outputdir)': quote_tcl(loc['outputbase']),
        'feat_files(1)': quote_tcl(dest),
        'fmri(level)': '1', 'fmri(analysis)': '2', 'fmri(inputtype)': '1',
        'fmri(filtering_yn)': '0', 'fmri(stats_yn)': '1',
        'fmri(poststats_yn)': '0', 'fmri(prewhiten_yn)': '1',
        'fmri(motionevs)': '0', 'fmri(confoundevs)': '1',
        'confoundev_files(1)': quote_tcl(loc['confound']),
        'fmri(ndelete)': '0', 'fmri(npts)': str(n), 'fmri(tr)': f'{tr:.6f}',
        'fmri(reginitial_highres_yn)': '0', 'fmri(reghighres_yn)': '0',
        'fmri(regstandard_yn)': '0', 'fmri(relative_yn)': '0',
    }
    for i, ev in enumerate(evfiles, 1):
        changes[f'fmri(custom{i})'] = quote_tcl(ev)
    # Si falta una clave fundamental en el FSF original, DETENER: no generar otra plantilla inventada.
    newtext = update_fsf(loc['fsf'].read_text(encoding='utf-8'), changes)
    loc['design'].write_text(newtext, encoding='utf-8')
    record = {'fecha_utc': now(), 'sujeto': args.sujeto, 'run': args.run,
              'historia_fsf': str(loc['fsf']), 'historia_fsf_sha256': cf.digest(loc['fsf']),
              'input_preprocesado': str(loc['feat']), 'input_nativo_sha256':
                   cf.digest(loc['feat'] / 'filtered_func_data.nii.gz'),
              'copia_de_preprocesado': str(dest), 'fsf_creado_sha256': cf.digest(loc['design']),
              'confounds': str(loc['confound']), 'confounds_sha256': cf.digest(loc['confound']),
              'eventos_sha256': evhashes, 'modelo_original': '8 EV + 8 derivadas + 21 COPE',
              'output_feAT': str(loc['output']), 'preflight': 'PENDIENTE',
              'run_FEAT': 'NO EJECUTADO'}
    with loc['provenance'].open('x', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print('FSF NATIVO PREPARADO:', loc['design'])
    print('ENTRADA FEAT NATIVA COPIADA:', dest)
    print('Siguiente paso: diseno (sin ejecutar FEAT).')


def verify_prepared(args):
    loc, n, tr, orig, evs, hashes = verify_inputs(args)
    require(loc['pre_copy'].is_dir() and loc['design'].is_file() and
            loc['provenance'].is_file(), 'Primero ejecutar preparar')
    doc = json.loads(loc['provenance'].read_text(encoding='utf-8'))
    require(doc['sujeto'] == args.sujeto and doc['run'] == args.run,
            'Diseño de otro sujeto o run')
    require(doc['historia_fsf_sha256'] == cf.digest(loc['fsf']) and
            doc['fsf_creado_sha256'] == cf.digest(loc['design']) and
            doc['confounds_sha256'] == cf.digest(loc['confound']) and
            doc['input_nativo_sha256'] == cf.digest(loc['feat']/'filtered_func_data.nii.gz') and
            doc['input_nativo_sha256'] == cf.digest(loc['pre_copy']/'filtered_func_data.nii.gz'),
            'Cambios posteriores al preparado; detener')
    require(doc['eventos_sha256'] == hashes, 'Cambió algún EV después de preparar')
    data, _ = read_fsf(loc['design'])
    require(data['feat_files(1)'] == str(loc['pre_copy']) and
            data['fmri(outputdir)'] == str(loc['outputbase']) and
            data['confoundev_files(1)'] == str(loc['confound']) and
            data['fmri(inputtype)'] == '1' and data['fmri(filtering_yn)'] == '0',
            'FSF preparado no cumple modo Statistics sobre FEAT')
    require(not loc['output'].exists() and not Path(str(loc['outputbase'])+'+.feat').exists(),
            'Salida FEAT ya existe; no reejecutar ni sobrescribir')
    return loc, doc, n


def vesta(path, token):
    text = path.read_text(encoding='utf-8')
    m = re.search(r'^/' + token + r'\s+(\d+)', text, re.M)
    require(m is not None, f'Falta {token} en {path}')
    return int(m.group(1))


def design(args):
    loc, doc, n = verify_prepared(args)
    require(shutil.which('feat_model'), 'Se requiere FSL feat_model en G15')
    require(not (loc['design'].with_suffix('.mat')).exists(),
            'Ya existe diseño; conservar para revisión, no sobrescribir')
    cmd = ['feat_model', str(loc['design'].with_suffix('')),
           str(loc['confound'])]
    print('Comprobando con FSL:', ' '.join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    mat = loc['design'].with_suffix('.mat')
    contrast = loc['design'].with_suffix('.con')
    require(mat.is_file() and contrast.is_file(), 'feat_model no generó diseño/contrastes')
    require(vesta(mat, 'NumPoints') == n and vesta(mat, 'NumWaves') == 30 and
            vesta(contrast, 'NumContrasts') == 21,
            'Matriz inesperada. Se esperan volúmenes x 30 regresores, 21 contrastes')
    matrix_txt = mat.read_text(encoding='utf-8').split('/Matrix', 1)
    require(len(matrix_txt) == 2, 'Falta /Matrix en design.mat')
    import io
    model = np.loadtxt(io.StringIO(matrix_txt[1]), ndmin=2)
    require(model.shape == (n, 30) and np.isfinite(model).all(),
            'Matriz final inválida/no finita')
    require(np.linalg.matrix_rank(model) == 30,
            'Matriz sin rango completo: revisar EVs y confounds')
    valid = {'fecha_utc': now(), 'fsf_sha256': cf.digest(loc['design']),
             'ev_sha256': doc['eventos_sha256'], 'confounds_sha256': cf.digest(loc['confound']),
             'design_mat_sha256': cf.digest(mat), 'contrastes_sha256': cf.digest(contrast),
             'filas': n, 'columnas': 30, 'rango': 30, 'contrastes': 21}
    valfile = loc['design'].with_suffix('.validacion.json')
    require(not valfile.exists(), 'Validación anterior existente; no sobrescribir')
    with valfile.open('x', encoding='utf-8') as f:
        json.dump(valid, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print('DISEÑO APTO PARA REVISIÓN: npts x 30, rango 30 y 21 contrastes. Aún NO es QC visual.')


def execute(args):
    require(args.confirmo_ejecutar, 'Para lanzar FEAT agregar --confirmo-ejecutar')
    loc, doc, n = verify_prepared(args)
    validation = loc['design'].with_suffix('.validacion.json')
    require(validation.is_file(), 'Primero ejecutar diseno y revisar la matriz')
    info = json.loads(validation.read_text(encoding='utf-8'))
    require(info['fsf_sha256'] == cf.digest(loc['design']) and
            info['ev_sha256'] == doc['eventos_sha256'] and
            info['confounds_sha256'] == cf.digest(loc['confound']) and
            info['design_mat_sha256'] == cf.digest(loc['design'].with_suffix('.mat')),
            'Algo cambió luego de feat_model; abortar')
    require(shutil.which('feat'), 'FSL feat no disponible en PATH')
    log = loc['design'].with_suffix('.ejecucion.log')
    require(not log.exists(), 'Ya existe log de ejecución; no lanzar dos veces')
    with log.open('x', encoding='utf-8') as f:
        completed = subprocess.run(['feat', str(loc['design'])],
                                   stdout=f, stderr=subprocess.STDOUT)
    print('feat devolvió:', completed.returncode, 'LOG:', log)
    require(completed.returncode == 0, 'FEAT informó un error; revisar log')
    print('FEAT puede usar procesos asíncronos. Usar verificar DESPUÉS de finalizar en la G15.')


def verify_outputs(args):
    loc = expected_paths(args)
    output = loc['output']
    require(output.is_dir(), 'Aún no existe carpeta resultado ' + str(output))
    fsf, _ = read_fsf(output / 'design.fsf')
    require(fsf.get('fmri(analysis)') == '2' and
            fsf.get('fmri(ncon_real)') == '21', 'Diseño ejecutado inesperado')
    bold = cf.nifti(output / 'filtered_func_data.nii.gz')
    source = cf.nifti(loc['feat'] / 'filtered_func_data.nii.gz')
    cf.same_grid(bold, source, 'Resultado NO está en espacio funcional original')
    mask = cf.nifti(output / 'mask.nii.gz')
    cf.same_grid(mask, bold, 'mask vs BOLD de resultado')
    mask_vals = np.asanyarray(mask.dataobj)
    require(np.isfinite(mask_vals).all(), 'Máscara de primer nivel con NaN/Inf')
    selected = mask_vals > 0.5
    require(selected.any() and selected.sum() < mask_vals.size,
            'Máscara GLM vacía o cubre TODO el volumen: detener')
    for index in range(1, 22):
        for kind in ('cope', 'varcope'):
            file = output/'stats'/f'{kind}{index}.nii.gz'
            img = cf.nifti(file)
            cf.same_grid(img, source, 'Mapas GLM fuera de nativo')
            values = np.asanyarray(img.dataobj)[selected]
            require(np.isfinite(values).all(), f'{file}: NaN/Inf dentro de máscara')
            if kind == 'varcope':
                require((values >= 0).all(), f'{file}: varianza negativa')
    print(json.dumps({'estado': 'MAPAS_PRESENTES_QC_ESTADISTICO_Y_VISUAL_PENDIENTE',
                      'sujeto': args.sujeto, 'run': args.run,
                      'output': str(output),
                      'mask_voxels': int(selected.sum()), 'grid_nativa': list(source.shape[:3]),
                      'contrastes_cope_y_varcope': 21}, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('accion', choices=['auditar', 'preparar', 'diseno', 'ejecutar', 'verificar'])
    p.add_argument('--sujeto', required=True)
    p.add_argument('--run', required=True, type=int)
    p.add_argument('--feat')
    p.add_argument('--fsf', help='FSF realmente usado en ESTE run; por defecto 6037/run1 de G15')
    p.add_argument('--evdir')
    p.add_argument('--trabajo', default='~/TesisDoctoral/fsl_nativo')
    p.add_argument('--confirmo-ejecutar', action='store_true')
    args = p.parse_args(argv)
    functions = {'auditar': audit, 'preparar': prepare, 'diseno': design,
                 'ejecutar': execute, 'verificar': verify_outputs}
    try:
        functions[args.accion](args)
        return 0
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError, KeyError) as e:
        print('DETENIDO:', e, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
