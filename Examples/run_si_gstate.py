#!/usr/bin/env python
"""
Companion to Section XXXXXX of the
workshop notebook.

Build an abinit calculation and run it.

Usage
-----
    python run_si_gstate.py
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


def gs_input(ecut=6, ngkpt=(8, 8, 8)):
    """Return a GS input for GaAs on a homogeneous k-mesh."""
    structure = Structure.from_file(str(STRUCTURE_DIR / 'mp-149_Si.cif'))
    pseudos = ["Si.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=16, paral_kgb=0, iomode=3)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    inp.set_vars(tolvrs=1e-6)
    return inp


def build_gs_task(workdir):
    inp = gs_input()
    task = flowtk.AbinitTask(inp, workdir=workdir)
    return task


def setup_task_manager(task, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = abilab.TaskManager.from_user_config()
    manager = manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    task.set_manager(manager)
    return task


def main():

    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("run_", "task_")

    # Initialize the task object
    task = build_gs_task(workdir)
    task = setup_task_manager(task, mpi_procs=4, timelimit_hour=0.1)

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
