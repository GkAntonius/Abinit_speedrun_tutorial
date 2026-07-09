#!/usr/bin/env python
"""
Companion to Section 4.2 ("k-point convergence") of the workshop notebook.

Builds the same flow as `workshop_lib.build_kpt_conv_flow()`: one SCF task
per automatically-generated k-mesh density. After it completes, the
notebook's `GsrRobot` cell collects the results and plots energy per atom
against k-point density.

Usage
-----
    python run_gaas_convkpt.py
    abirun.py flow_gaas_convkpt scheduler
    abirun.py flow_gaas_convkpt status
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


def build_kpt_conv_flow(workdir, nk_list=(1, 2, 4, 6, 8, 10)):
    """Flow with one SCF task per (automatically-generated) k-mesh density."""
    flow = flowtk.Flow(workdir=workdir)
    for nk in nk_list:
        inp = gs_input(ecut=12)
        inp.set_autokmesh(nk)
        flow.register_scf_task(inp)
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
        workdir = Path(__file__).name.replace(".py", "").replace("run_", "flow_")

    flow = build_kpt_conv_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
