#!/usr/bin/env python
"""
Companion to `1-Task_to_flow.ipynb`, step 3.

The same two tasks as `run_si_gstate.py` + `run_si_nscf.py` (steps 1-2),
this time registered together in a `Work` inside a `Flow`, with the
dependency expressed as `deps={gs_task: 'DEN'}` -- a reference to the task
object itself, not a hardcoded path. This is the "Task to Flow" step: the
same calculation, but AbiPy now tracks the dependency between tasks for
you, which is what lets a `Flow` be built once and (re)run reliably,
in the right order, however many tasks it has.

Usage
-----
    python run_si_ebands.py
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
SI_CIF = STRUCTURE_DIR / 'mp-149_Si.cif'
FCC_KPATH = [[0.5, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.5, 0.5]]


def si_gs_input(ecut=6, ngkpt=(8, 8, 8)):
    """Return a GS input for Si on a homogeneous k-mesh."""
    structure = Structure.from_file(str(SI_CIF))
    pseudos = ["Si.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=16, paral_kgb=0, iomode=3)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    inp.set_vars(tolvrs=1e-6)
    return inp


def build_si_gs_task(workdir):
    """A single AbinitTask (no Flow, no Work) for the Si ground state."""
    inp = si_gs_input()
    return flowtk.AbinitTask(inp, workdir=workdir)


def si_bandstructure_input(ecut=6):
    """Return a Si band-structure (NSCF) input along the L-Gamma-X path."""
    structure = Structure.from_file(str(SI_CIF))
    pseudos = ["Si.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))

    # A band structure calculation is a non-self-consistent task (iscf=-1).
    inp.set_vars(ecut=ecut, iscf=-1, iomode=3)

    # We require more bands, and the tolerance criterion is on the wavefunction.
    inp.set_vars(nband=40, tolwfr=1e-12)

    # We compute the eigenvalues along a k-point path between high symmetry points.
    inp.set_kpath(ndivsm=10, kptbounds=FCC_KPATH)

    return inp


def build_si_nscf_task(workdir, density):
    """A second AbinitTask, depending on `density` (a Task, or a path/'DEN' pair)."""
    inp = si_bandstructure_input()

    # Dependencies are specified as a dict of the form {file_or_task: property}.
    deps = {density: 'DEN'}

    return flowtk.AbinitTask(inp, workdir=workdir, deps=deps)


def build_si_ebands_task_flow(workdir):
    """Same two Tasks as above, registered in a Work/Flow instead of run by hand."""
    flow = flowtk.Flow(workdir=workdir)
    work = flowtk.Work(workdir=None)

    gs_task = build_si_gs_task(workdir=None)
    nscf_task = build_si_nscf_task(workdir=None, density=gs_task)

    work.register_task(gs_task)
    work.register_task(nscf_task)
    flow.register_work(work)

    return flow


def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow


def main():

    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("make_", "flow_")

    # Initialize the flow object
    flow = build_si_ebands_task_flow(workdir)
    flow = setup_manager(flow, mpi_procs=4, timelimit_hour=0.5)

    # Remove a previous run, if it exists.
    if Path(workdir).exists():
        print(f'Removing existing directory: {workdir}/')
        flow.rmtree()

    # Create directory, write inputs and link external files.
    print(f'Building flow in directory: {workdir}/')
    flow.build_and_pickle_dump()

    # Run each of the tasks sequentially and wait for the result.
    #print('Running flow...')
    #for work in flow:
    #    for task in work:
    #        task.start_and_wait()

    #        # Report calculation status
    #        name = task.name
    #        status = task.check_status()
    #        print(f'Status of task {name}: {status}')


if __name__ == "__main__":
    main()
