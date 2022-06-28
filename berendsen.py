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
parser.add_argument("-p", "--plot", default=False, action='store_true', required=False, help='only plot graphics')
args = parser.parse_args()

os.chdir('scripts')
if not args.plot:
    outname = 'polycrystall'
    task = f'{lmp} -in in.berendsen_relax -var name {args.name} -var structure_name polycrystall.dat -sf omp -pk omp {args.jobs}'
    exitflag = False
    db_flag = False
    db = 0

    print('starting LAMMPS...')
    print(task)
    with Popen(task.split(), stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        time.sleep(0.1)
        print('\n')
        for line in p.stdout:
            if "Dangerous builds" in  line:
                db = int(line.split()[-1])
                if db>0:
                    db_flag = True
            elif "dumpfile" in line:
                dumpfile = (line.replace('dumpfile ', '')).replace('\n', '')
            elif "All done" in line:
                exitflag = True
            if not args.verbose:
                if '!' in line:
                    print(line.replace('!', ''), end='')
            else:
                print(line, end='')   
                    
    if not exitflag:
        raise ValueError('Error in LAMMPS')

    print('done\n')
    print(f'WARNING!!!\nDengerous neighboor list buildings: {db}')

print('plotting...')
impath = f'../workspace/{args.name}/images'
Path(impath).mkdir(exist_ok=True)  
from scripts.plot_thermal_relax import main as plot
plot_args = parser.parse_args()
plot_args.name = args.name
plot_args.n = args.mean_width
plot_args.inp = 'berendsen_relax'
plot(plot_args)

print('All done')