"""
siesta_engine.py
ASE+Siesta+ML

Handles the primary functions
"""
import dask
import dask.distributed
from dask.distributed  import Client, LocalCluster
from .calculator import CustomSiesta
import sys
import argparse
import os
from ase.io import read, write
import json

def in_private_dir(method):

    def wrapper_private_dir(dir, *args, **kwargs):
        try:
            os.chdir(dir)
        except FileNotFoundError:
            os.mkdir(dir)
            os.chdir(dir)
        return method(*args, **kwargs)
    return wrapper_private_dir

@in_private_dir
def calculate_system(atoms, fdf_path, kwargs):
    calc = CustomSiesta(**kwargs,
               fdf_path = fdf_path)
    atoms.calc = calc
    atoms.get_potential_energy()
    return atoms

def calculate_distributed(atoms, fdf_path, workdir, kwargs, n_workers = -1):

    kwargs['label']= kwargs.get('label','siesta')
    kwargs['xc']= kwargs.get('xc','PW92')
    kwargs['basis_set']= kwargs.get('basis_set','SZ')
    kwargs['fdf_arguments']= kwargs.get('fdf_arguments',{'MaxSCFIterations': 200})
    kwargs['pseudo_qualifier'] = kwargs.get('pseudo_qualifier','')

    print('Calculating {} systems on'.format(len(atoms)))
    cluster = LocalCluster(n_workers = n_workers, threads_per_worker = 1)
    print(cluster)
    client = Client(cluster)


    futures = client.map(calculate_system,
        [os.path.join(workdir,str(i)) for i,_ in enumerate(atoms)],
        atoms, [fdf_path]*len(atoms), [kwargs]*len(atoms))
    return [f.result() for f in futures]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('xyz', action='store', help ='Path to .xyz/.traj file containing list of configurations')
    parser.add_argument('-fdf', metavar='fdf', type=str, nargs = '?', default='')
    parser.add_argument('-workdir', metavar='workdir', type=str, nargs = '?', default='.')
    parser.add_argument('-pseudoloc', metavar='pseudoloc', type=str, nargs = '?', default='.')
    parser.add_argument('-kwargs', metavar='kwargs', type=json.loads, nargs = '?', default='{}')
    parser.add_argument('-nworkers', metavar='nworkers', type=int, nargs = '?', default=-1)
    args = parser.parse_args()

    print('Passed kwargs: {}'.format(args.kwargs))
    dir = os.path.abspath(args.workdir)
    if args.fdf:
        fdf_path = os.path.abspath(args.fdf)
    else:
        fdf_path = None
    pseudo_path = os.path.abspath(args.pseudoloc)
    os.environ['SIESTA_PP_PATH'] = pseudo_path
    atoms = read(args.xyz, ':')

    results = calculate_distributed(atoms, fdf_path, dir, args.kwargs, args.nworkers)

    results_ext = args.xyz.split('.')[-1]
    results_path = os.path.join(dir, 'results.' + results_ext)
    write(results_path, results)
