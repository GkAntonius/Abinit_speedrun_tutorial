#!/usr/bin/env python
"""
Companion to Section XXXXXX of the
workshop notebook.

Build an abinit calculation and run it.

Usage
-----
    python run_gaas_ebands.py
"""
from pathlib import Path

import abipy.abilab as abilab
import abipy.flowtk as flowtk
from abipy.abilab import Structure

# This script is meant to be copied -- together with the rest of this
# Tutorial/ directory -- into your own work directory. Data/Pseudos and
# Data/Structures are located relative to *this file*.
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Data"
PSEUDO_DIR = DATA_DIR / "Pseudos"
STRUCTURE_DIR = DATA_DIR / "Structures"
GAAS_CIF = STRUCTURE_DIR / 'mp-2534_GaAs.cif'
FCC_KPATH = [[0.5, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.5, 0.5]]

def bandstructure_input(ecut=6):
    """Return a band structure input for GaAs."""
    structure = Structure.from_file(str(GAAS_CIF))
    pseudos = ["Ga.psp8", "As.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))

    # A band structure calculation is a non-self-consistent task (iscf=-1)
    inp.set_vars(ecut=ecut, iscf=-1, iomode=3)

    # We require more bands, and the tolerance criterion is on the wavefunction.
    inp.set_vars(nband=40, tolwfr=1e-12)

    # We compute the eigenvalues along a k-point path between high symmetry points.
    inp.set_kpath(ndivsm=10, kptbounds=FCC_KPATH)

    return inp

def build_bandstructure_task(workdir):
    inp = bandstructure_input()
    deps = {'task_gaas_gstate/outdata/out_DEN.nc' : 'DEN'}
    task = flowtk.AbinitTask(inp, workdir=workdir, deps=deps)
    return task


def setup_manager(task, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = abilab.TaskManager.from_user_config()
    manager = manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    task.set_manager(manager)
    return task


def main():

    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("run_", "task_")

    # Initialize the task object
    task = build_bandstructure_task(workdir)
    task = setup_manager(task, mpi_procs=4, timelimit_hour=0.5)

    # Remove a previous run, if it exists.
    if Path(workdir).exists():
        print(f'Removing existing directory: {workdir}/')
        task.rmtree()

    # Create directory, write inputs and link external files.
    print(f'Building task in directory: {workdir}/')
    task.build()
    task.make_links()

    # Run the calculation and wait for the result
    print('Running task...')
    task.start_and_wait()

    # Report calculation status
    status = task.check_status()
    print(f'Status: {status}')


if __name__ == "__main__":
    main()
