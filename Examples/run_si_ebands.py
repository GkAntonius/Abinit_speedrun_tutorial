#!/usr/bin/env python
"""
Companion to Section XXXXXX of the
workshop notebook.

Build an abinit calculation and run it.

Usage
-----
    python run_si_nscf.py
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


def bandstructure_input(ecut=6):
    """Return a band structure input for GaAs."""
    structure = Structure.from_file(str(STRUCTURE_DIR / 'mp-149_Si.cif'))
    pseudos = ["Si.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))

    # A band structure calculation is a non-self-consistent task (iscf=-1)
    inp.set_vars(ecut=ecut, iscf=-1, iomode=3)

    # We require more bands, and the tolerance criterion is on the wavefunction.
    inp.set_vars(nband=40, tolwfr=1e-12)

    # We compute the eigenvalues along a k-point path between high symmetry points.
    FCC_KPATH = [[0.5, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.5, 0.5]]
    inp.set_kpath(ndivsm=10, kptbounds=FCC_KPATH)

    return inp


def build_nscf_task(workdir, density):

    # Create the input object
    inp = bandstructure_input()

    # Dependencies are specified as a dict of the form {file_or_task : property}
    deps = {density : 'DEN'}

    # Create the task object
    task = flowtk.AbinitTask(inp, workdir=workdir, deps=deps)
    return task


def build_ebands_flow(workdir):
    flow = flowtk.Flow(workdir=workdir)
    work = flowtk.Work(workdir=None)

    gs_task = build_gs_task(workdir=None)
    nscf_task = build_nscf_task(workdir=None, density=gs_task)

    work.register_task(gs_task)
    work.register_task(nscf_task)

    flow.register_work(work)

    return flow


def setup_flow_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = abilab.TaskManager.from_user_config()
    manager = manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        for task in work:
            task.set_manager(manager)
    return flow


def main():

    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("run_", "flow_")

    # Initialize the task object
    flow = build_ebands_flow(workdir)
    flow = setup_flow_manager(flow, mpi_procs=4, timelimit_hour=0.5)

    # Remove a previous run, if it exists.
    if Path(workdir).exists():
        print(f'Removing existing directory: {workdir}/')
        flow.rmtree()

    # Create directory, write inputs and link external files.
    print(f'Building flow in directory: {workdir}/')
    flow.build_and_pickle_dump()

    # Run each of the task sequentially and wait for the result.
    print('Running flow...')
    for work in flow:
        for task in work:
            task.start_and_wait()

            # Report calculation status
            name = task.name
            status = task.check_status()
            print(f'Status of task {name}: {status}')


if __name__ == "__main__":
    main()
