"""Pruebas sintéticas, sin MRI reales ni instalación de FSL; FSL se simula.
Ejecutar desde raíz: python3 -m unittest discover -s tests -v
"""
import argparse
from contextlib import ExitStack
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
C = ROOT/'01_confundidores/automatizacion/confundidores.py'
F = ROOT/'02_primer_nivel/automatizacion/primer_nivel.py'
spec = importlib.util.spec_from_file_location('confundidores', C)
cf = importlib.util.module_from_spec(spec)
sys.modules['confundidores'] = cf
spec.loader.exec_module(cf)
spec2 = importlib.util.spec_from_file_location('primer_nivel', F)
first = importlib.util.module_from_spec(spec2)
sys.modules['primer_nivel'] = first
spec2.loader.exec_module(first)


class FakeHeader:
    def get_zooms(self):
        return (2., 2., 2., 2.)
    def get_xyzt_units(self):
        return ('mm', 'sec')


class FakeImage:
    affine = np.eye(4)
    header = FakeHeader()
    def __init__(self, data):
        self.dataobj = np.asarray(data, dtype=float)
        self.shape = self.dataobj.shape


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pre = self.root/'input'/ '6037' / 'run1.feat'
        self.evdir = self.root/'eventos'/'6037'/'evs'/'run-1'
        self.oldfsf = self.root/'anterior'/'design.fsf'
        self.work = self.root/'trabajo'
        self.n = 40
        self.pre.mkdir(parents=True)
        (self.pre/'reg').mkdir()
        (self.pre/'mc').mkdir()
        self.evdir.mkdir(parents=True)
        self.oldfsf.parent.mkdir()
        for relative in ('filtered_func_data.nii.gz', 'example_func.nii.gz',
                         'mask.nii.gz', 'reg/highres.nii.gz',
                         'reg/highres2example_func.mat', 'mc/prefiltered_func_data_mcf.par'):
            file = self.pre/relative
            file.write_bytes(b'fixture-' + relative.encode())
        np.savetxt(self.pre/'reg/highres2example_func.mat', np.eye(4))
        moves = np.random.default_rng(20).normal(size=(self.n, 6))
        np.savetxt(self.pre/'mc/prefiltered_func_data_mcf.par', moves, fmt='%.15g')
        (self.pre/'design.fsf').write_text('set fmri(analysis) 1\nset fmri(ndelete) 0\n'
            'set fmri(npts) 40\nset fmri(tr) 2\nset fmri(smooth) 8\n'
            'set fmri(paradigm_hp) 100\n', encoding='utf-8')
        fsf = {
            'fmri(level)':'1', 'fmri(analysis)':'2', 'fmri(inputtype)':'2',
            'fmri(outputdir)': '"/OLD/feat"', 'feat_files(1)':'"/OLD/MNI"',
            'fmri(evs_orig)':'8', 'fmri(evs_real)':'16',
            'fmri(ncon_orig)':'21', 'fmri(ncon_real)':'21',
            'fmri(npts)':'40', 'fmri(tr)':'2', 'fmri(ndelete)':'0',
            'fmri(prewhiten_yn)':'1', 'fmri(motionevs)':'0',
            'fmri(confoundevs)':'1', 'confoundev_files(1)':'"/OLD/WM.txt"',
            'fmri(filtering_yn)':'1', 'fmri(stats_yn)':'1',
            'fmri(poststats_yn)':'0', 'fmri(reginitial_highres_yn)':'0',
            'fmri(reghighres_yn)':'0','fmri(regstandard_yn)':'1',
            'fmri(relative_yn)':'0'
        }
        for ev, name in enumerate(first.EVS,1):
            fsf[f'fmri(evtitle{ev})'] = f'"{name}"'
            fsf[f'fmri(custom{ev})'] = '"/old/not/valid.txt"'
            fsf[f'fmri(shape{ev})'] = '3'
            fsf[f'fmri(convolve{ev})'] = '3'
            fsf[f'fmri(deriv_yn{ev})'] = '1'
            np.savetxt(self.evdir/f'{name}.txt', [[ev, 1., 1.]],fmt='%.4f')
        for contrast in range(1,22):
            fsf[f'fmri(conname_orig.{contrast})'] = f'"contraste{contrast}"'
            fsf[f'fmri(conname_real.{contrast})'] = f'"contraste{contrast}"'
            for ev in range(1,9):
                weight = (1 if ev==1 else (-1 if ev==2 else 0))
                fsf[f'fmri(con_orig{contrast}.{ev})'] = str(weight)
                fsf[f'fmri(con_real{contrast}.{2*ev-1})'] = str(weight)
                fsf[f'fmri(con_real{contrast}.{2*ev})'] = '0'
        self.oldfsf.write_text('\n'.join(f'set {k} {v}' for k,v in fsf.items())+'\n')
        self.check_files = {}
        native=np.ones((4,4,4,self.n))
        anatomical=np.ones((5,5,5))
        brain=np.zeros((4,4,4));brain.flat[:20] = 1
        wm=np.zeros((4,4,4));wm.flat[2:9]=1
        csf=np.zeros((4,4,4));csf.flat[12:15]=1
        self.default = {'bold':FakeImage(native),'func':FakeImage(np.ones((4,4,4))),
                        't1':FakeImage(anatomical),'brain':FakeImage(brain),
                        'wm':FakeImage(wm),'csf':FakeImage(csf)}
        self.args=argparse.Namespace(accion='auditar',sujeto='6037',run=1,
                 feat=str(self.pre), trabajo=str(self.work),
                 confirmo_registro=False,confirmo_mascaras=False,nota='')
        self.args1=argparse.Namespace(accion='auditar',sujeto='6037',run=1,
                 feat=str(self.pre), fsf=str(self.oldfsf), evdir=str(self.evdir),
                 trabajo=str(self.work), confirmo_ejecutar=False)
        self.source_sha=cf.digest(self.pre/'filtered_func_data.nii.gz')

    def fake_img(self,path):
        path=Path(path)
        if path.name.startswith('mask_wm_func'):
            return self.default['wm']
        if path.name.startswith('mask_csf_func'):
            return self.default['csf']
        if path.name=='mask.nii.gz':
            return self.default['brain']
        if path.name=='highres.nii.gz':
            return self.default['t1']
        if path.name=='filtered_func_data.nii.gz':
            return self.default['bold']
        return self.default['func']

    def fsl_stub(self,*parts):
        parts=[str(p) for p in parts]
        if parts[0]=='fast':
            prefix=Path(parts[parts.index('-o')+1])
            for idx in (0,2):
                Path(str(prefix)+f'_pve_{idx}.nii.gz').write_bytes(b'fakeFAST')
        if parts[0] in ('fslmaths','flirt','fslmeants'):
            if '-o' in parts:
                out=Path(parts[parts.index('-o')+1])
            else:
                out=Path(parts[-1])
            out.parent.mkdir(parents=True, exist_ok=True)
            if parts[0]=='fslmeants':
                x=np.linspace(0, 1, self.n) + (2 if 'wm' in out.name else 0)
                np.savetxt(out, x,fmt='%.8g')
            else:
                out.write_bytes(b'fake image')

    def prepare_cf(self):
        with patch.object(cf,'nifti',side_effect=self.fake_img),\
             patch.object(cf,'run_command',side_effect=self.fsl_stub),\
             patch.object(cf,'require_programs'):
            cf.create_masks(self.args)
            self.args.confirmo_registro=True
            self.args.confirmo_mascaras=True
            self.args.nota='Revisión humana registrada en prueba sintética'
            cf.approve(self.args)
            cf.finalize(self.args)
        self.assertEqual(cf.digest(self.pre/'filtered_func_data.nii.gz'),self.source_sha)


class ConfoundsTests(Fixture):
    def test_audit_is_read_only_and_detects_native_geometry(self):
        with patch.object(cf,'nifti',side_effect=self.fake_img):
            cf.audit(self.args)
        self.assertFalse(self.work.exists())

    def test_pilot_masks_qc_confounds_40_by_14(self):
        self.prepare_cf()
        out=self.work/'6037/run1/01_confundidores/finales/todos_confounds_nativo.txt'
        m=np.loadtxt(out)
        self.assertEqual(m.shape,(40,14))
        raw=np.loadtxt(self.pre/'mc/prefiltered_func_data_mcf.par')
        np.testing.assert_allclose(m[:, :6],raw,atol=1e-9)
        np.testing.assert_allclose(m[0,6:12],np.zeros(6),atol=1e-12)
        np.testing.assert_allclose(m[1:,6:12],np.diff(raw,axis=0),atol=1e-9)

    def test_cannot_finalize_before_visual_approval(self):
        with patch.object(cf,'nifti',side_effect=self.fake_img),\
             patch.object(cf,'run_command',side_effect=self.fsl_stub),\
             patch.object(cf,'require_programs'):
            cf.create_masks(self.args)
            with self.assertRaisesRegex(ValueError,'Falta revisión humana'):
                cf.finalize(self.args)

    def test_nan_tissue_mask_fails_closed(self):
        bad=FakeImage(self.default['wm'].dataobj.copy())
        bad.dataobj.flat[3]=np.nan
        with patch.object(cf,'nifti',return_value=bad):
            with self.assertRaisesRegex(ValueError,'NaN'):
                cf.check_mask_file(Path('fake'),self.default['bold'],self.default['brain'],'wm')

    def test_inflated_func_mask_blocks_audit(self):
        self.default['brain']=FakeImage(np.ones((4,4,4)))
        with patch.object(cf,'nifti',side_effect=self.fake_img):
            with self.assertRaisesRegex(ValueError,'inflada|80%'):
                cf.input_audit(self.pre)

    def test_refuse_reprocess_existing(self):
        self.prepare_cf()
        with patch.object(cf,'nifti',side_effect=self.fake_img),\
             patch.object(cf,'run_command',side_effect=self.fsl_stub),\
             patch.object(cf,'require_programs'):
            with self.assertRaisesRegex(ValueError,'Ya existen máscaras'):
                cf.create_masks(self.args)


class FirstLevelTests(Fixture):
    def test_historical_contrasts_and_derivatives_preserved(self):
        orig, files, hashes=first.validate_model(self.oldfsf,40,2.,self.evdir)
        self.assertEqual(len(files),8)
        self.assertEqual(orig['fmri(ncon_real)'],'21')
        self.assertEqual(len(hashes),8)

    def test_wrong_contrast_blocks_before_copy(self):
        source=self.oldfsf.read_text()
        self.oldfsf.write_text(source.replace('set fmri(con_real1.1) 1',
                                             'set fmri(con_real1.1) -1'))
        with self.assertRaisesRegex(ValueError,'pesos no coinciden'):
            first.validate_model(self.oldfsf,40,2.,self.evdir)

    def test_unsafe_path_rejected(self):
        with self.assertRaisesRegex(ValueError,'Tcl'):
            first.quote_tcl('/ruta/[exec rm]')

    def test_full_audit_prepare_design_preflight_and_protection(self):
        self.prepare_cf()
        with patch.object(cf,'nifti',side_effect=self.fake_img):
            first.audit(self.args1)
            first.prepare(self.args1)
            generated=self.work/'6037/run1/02_primer_nivel/diseno_run_nativo.fsf'
            cfg,_=first.read_fsf(generated)
            self.assertEqual(cfg['fmri(inputtype)'],'1')
            self.assertEqual(cfg['fmri(filtering_yn)'],'0')
            self.assertTrue(cfg['feat_files(1)'].endswith('entrada_nativa.feat'))
            self.assertEqual(cfg['fmri(ncon_real)'],'21')
            self.assertFalse((self.work/'6037/run1/02_primer_nivel/run_firstlevel_nativo.feat').exists())
            self.assertEqual(cf.digest(self.pre/'filtered_func_data.nii.gz'),self.source_sha)
            with self.assertRaisesRegex(ValueError,'Ya hay archivos'):
                first.prepare(self.args1)
            # Fake feat_model: reproduce output format (sin afirmar ejecución real FSL).
            def model_stub(cmd,check=False):
                name=Path(str(cmd[1]))
                vals=np.random.default_rng(101).normal(size=(40,30))
                with open(str(name)+'.mat','w') as f:
                    f.write('/NumWaves\t30\n/NumPoints\t40\n/Matrix\n')
                    np.savetxt(f, vals)
                (Path(str(name)+'.con')).write_text('/NumContrasts 21\n')
            with patch.object(first.shutil,'which',return_value='/fake/bin/feat_model'),\
                 patch.object(first.subprocess,'run',side_effect=model_stub):
                first.design(self.args1)
            self.assertTrue(generated.with_suffix('.validacion.json').is_file())
            self.args1.confirmo_ejecutar=True
            def feat_stub(cmd,stdout=None,stderr=None):
                class Result: returncode=0
                return Result()
            with patch.object(first.shutil,'which',return_value='/fake/bin/feat'),\
                 patch.object(first.subprocess,'run',side_effect=feat_stub):
                first.execute(self.args1)
            self.assertTrue(generated.with_suffix('.ejecucion.log').exists())
            with self.assertRaisesRegex(ValueError,'Ya existe log'):
                with patch.object(first.shutil,'which',return_value='/fake/bin/feat'):
                    first.execute(self.args1)
            self.assertEqual(cf.digest(self.pre/'filtered_func_data.nii.gz'),self.source_sha)

    def test_changed_event_invalidates_pilot(self):
        self.prepare_cf()
        with patch.object(cf,'nifti',side_effect=self.fake_img):
            first.prepare(self.args1)
            path=self.evdir/'Likert.txt'
            path.write_text('2 3 1\n')
            with self.assertRaisesRegex(ValueError,'Cambió algún EV'):
                first.verify_prepared(self.args1)


if __name__=='__main__':
    unittest.main()
