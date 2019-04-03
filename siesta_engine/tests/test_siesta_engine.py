"""
Unit and regression test for the siesta_engine package.
"""

# Import package, test suite, and other packages as needed
import siesta_engine
import pytest
import sys
from ase.io import read
import os
test_dir = os.path.dirname(os.path.abspath(__file__))

os.environ['SIESTA_PP_PATH'] = os.path.join(test_dir)

def test_siesta_engine_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "siesta_engine" in sys.modules

def test_fdf_creator():
    atoms = read(os.path.join(test_dir,'water.traj'),'0')
    try:
        os.chdir(os.path.join(test_dir, 'siesta'))
    except FileNotFoundError:
        os.mkdir(os.path.join(test_dir, 'siesta'))
        os.chdir(os.path.join(test_dir, 'siesta'))
    atoms.calc = \
    siesta_engine.calculator.CustomSiesta(label='H2O',
               xc='PW92',
               basis_set='SZ',
               fdf_arguments={'MaxSCFIterations': 100},
               fdf_path = os.path.join(test_dir,'custom.fdf'),
               pseudo_qualifier = '')

    atoms.get_potential_energy()
