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
task = f'{lmp} -in in.berendsen_relax -var name {args.name} -var structure_name polycrystall.dat -sf omp -pk omp {args.jobs}'
exitflag = False

print('starting LAMMPS...')
print(task)
with Popen(task.split(), stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    time.sleep(0.1)
    print('\n')
    for line in p.stdout:
        if "lattice found" in  line:
            exitflag = True
        elif "dumpfile" in line:
            dumpfile = (line.replace('dumpfile ', '')).replace('\n', '')
        if not args.verbose:
            if '!' in line:
                print(line.replace('!', ''), end='')
        else:
            print(line, end='')   
                
if not exitflag:
    raise ValueError('Error in LAMMPS')

print('done')

print('All done')