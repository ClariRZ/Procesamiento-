"""Pruebas sintéticas para auditar_homogeneidad_y_diseno.py."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CODE = Path(__file__).with_name('auditar_homogeneidad_y_diseno.py')
spec = importlib.util.spec_from_file_location('audit_test', CODE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class TestReadOnly(unittest.TestCase):
    def test_fsf_and_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            f = Path(folder) / 'x.fsf'
            f.write_text('set fmri(ndelete) 0\nset feat_files(1) "/tmp/a.feat"\n')
            self.assertEqual(audit.field(audit.fsf_settings(f), 'ndelete'), '0')
            f.write_text('set fmri(ndelete) 0\nset fmri(ndelete) 1\n')
            with self.assertRaises(ValueError):
                audit.fsf_settings(f)

    def test_pilot_matrix(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'design.mat'
            p.write_text('/NumWaves 30\n/NumPoints 2\n/Matrix\n' +
                         ' '.join(['1'] * 30) + '\n' +
                         ' '.join(['2'] * 30) + '\n')
            header, rows = audit.feat_matrix(p)
            self.assertEqual(header['NumPoints'], 2)
            self.assertEqual(len(rows[0]), 30)
            self.assertAlmostEqual(audit.correlation([1, 2, 3], [3, 5, 7]), 1)

    def test_end_to_end_read_only(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            root = home / 'FEAT'
            feat = root / '5015' / 'run1.feat'
            feat.mkdir(parents=True)
            (feat / 'filtered_func_data.nii.gz').write_text('mock')
            (feat / 'design.fsf').write_text(
                'set fmri(analysis) 1\nset fmri(filtering_yn) 1\n'
                'set fmri(ndelete) 0\nset fmri(paradigm_hp) 100\n'
                'set fmri(smooth) 5\nset fmri(tr) 2\n'
                'set fmri(temphp_yn) 1\nset fmri(st) 5\n'
            )
            binpath = home / 'bin'
            binpath.mkdir()
            stub = binpath / 'fslval'
            stub.write_text('#!/bin/sh\ncase "$2" in dim4) echo 387;; pixdim4) echo 2;; esac\n')
            stub.chmod(0o755)
            env = dict(os.environ)
            env['PATH'] = str(binpath) + ':' + env['PATH']
            before = sorted(str(p.relative_to(home)) for p in home.rglob('*'))
            result = subprocess.run(
                [sys.executable, '-B', str(CODE),
                 '--feat-root', str(root),
                 '--out-root', str(home / 'out'),
                 '--conf-root', str(home / 'conf'),
                 '--pilot-design', str(home / 'not_found.mat')],
                text=True, capture_output=True, env=env)
            after = sorted(str(p.relative_to(home)) for p in home.rglob('*'))
            self.assertEqual(before, after)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('SOLO_LECTURA;', result.stdout)


if __name__ == '__main__':
    unittest.main()
