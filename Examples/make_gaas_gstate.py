#!/usr/bin/env python
"""
Companion to Section 3 ("Ground-state total energy of GaAs") of the
workshop notebook.

Builds the same flow as `workshop_lib.build_gs_flow()` and writes it to
disk, so it can be launched and monitored from a terminal on the cluster
instead of blocking the notebook kernel with `flow.make_scheduler().start()`.

Usage
-----
    python make_gaas_gstate.py
    abirun.py flow_gaas_gstate scheduler   # ... then run it (repeat if interrupted)
    abirun.py flow_gaas_gstate status      # ... or just check progress
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


def gs_input(ecut=6, ngkpt=(8, 8, 8)):
    """Return a GS input for GaAs on a homogeneous k-mesh."""
    structure = Structure.from_file(str(GAAS_CIF))
    pseudos = ["Ga.psp8", "As.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=16, paral_kgb=0, iomode=3)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    inp.set_vars(tolvrs=1e-6)
    return inp


def build_gs_flow(workdir):
    """Flow with a single SCF task: the total energy of GaAs."""
    flow = flowtk.Flow(workdir=workdir)
    flow.register_scf_task(gs_input())
    return flow


def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow


def build_flow(workdir=None):
    # Set working directory (default is constructed from the script name)
    if not workdir:
        workdir = Path(__file__).name.replace(".py", "").replace("make_", "flow_")

    flow = build_gs_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
