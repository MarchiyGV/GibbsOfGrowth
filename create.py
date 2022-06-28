from pathlib import Path
import argparse, os, sys, shutil
from subprocess import Popen, PIPE
import time, re, shutil, sys, glob
import numpy as np
sys.path.insert(1, f'{sys.path[0]}/scripts')
from set_lammps import lmp

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", required=True)
parser.add_argument("-j", "--jobs", type=int, required=False, default=1)
parser.add_argument("-v", "--verbose", default=False, action='store_true', required=False)
args = parser.parse_args()

outname = 'polycrystall'
os.chdir('scripts')
task = f'{lmp} -in in.find_minimum -var name {args.name} -sf omp -pk omp {args.jobs}'
exitflag = False

print('finding structure...')
print(task)
with Popen(task.split(), stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    time.sleep(0.1)
    print('\n')
    for line in p.stdout:
        if "lattice found" in  line:
            exitflag = True
        if '!!' in line:
            s = line.replace('!!', '')
            s = s.replace('%', "'")
            exec(s)
            print(s, end='')
        elif (not args.verbose) and ('!' in line):
            print(line.replace('!', ''), end='')
        elif args.verbose:
            print(line, end='')   
                
if not exitflag:
    raise ValueError('Error in LAMMPS')

atmsk_path = f'../workspace/{args.name}/tmp_atomsk'
Path(atmsk_path).mkdir(exist_ok=True)
os.chdir(atmsk_path)

print('done\ncreating lattice seed...')

task = f'atomsk --create {lat} {a0} {element1} lammps -overwrite'
print(task)
with Popen(task.split(), stdout=PIPE, stdin=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in p.stdout:
        if args.verbose:
            print(line, end='')  
        elif 'ERROR' in line:
            print(line)
shutil.move(f'{element1}.lmp', f'../dat/{element1}.dat')
print('done\n')
print('All done')

print('done\ncreating polycrystal...')

Lx, Ly, Lz = 100, 100, 100
N = 10
fname = 'polycrystal.txt'
file = f"""
box {Lx} {Ly} {Lz}
random {N}
"""
with open(fname, 'w') as f:
    f.write(file)

exitflag = False

task = f'atomsk --polycrystal ../dat/{element1}.dat {fname} {outname}.lmp -wrap -overwrite -nthreads {args.jobs}'
print(task)
with Popen(task.split(), stdout=PIPE, stdin=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in p.stdout:
        if args.verbose:
            print(line, end='')  
        elif 'ERROR' in line:
            print(line)
        '''
        if 'Do you want to overwrite it (y/n)' in line:
            p.stdin.write("y\n")
        if 'Y=overwrite all' in line:
            p.stdin.write("Y\n")
        '''
shutil.move(f'{outname}.lmp', f'../dat/{outname}.dat')
print('done\n')
print('All done')