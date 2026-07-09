#!/usr/bin/env python
"""
Companion to Section 6 ("Equation of state and the lattice parameter") of
the workshop notebook.

Builds the same flow as `workshop_lib.build_eos_flow()`: one SCF task per
isotropically-scaled volume of GaAs around its experimental volume. After it
completes, the notebook fits the energy-volume curve with a Birch-Murnaghan
equation of state (`abilab.EOS`) to get the equilibrium volume and bulk
modulus. As noted in the notebook, this flow deliberately uses a coarse
`ecut`/k-mesh to stay cheap -- treat the numbers as illustrative, not
converged.

Usage
-----
    python make_gaas_eos.py
    abirun.py flow_gaas_eos scheduler
    abirun.py flow_gaas_eos status
"""
from pathlib import Path

import numpy as np

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


def build_eos_flow(workdir, scale_volumes=tuple(np.arange(0.94, 1.07, 0.02))):
    """Flow with one SCF task per isotropically-scaled volume of GaAs."""
    flow = flowtk.Flow(workdir=workdir)
    structure = Structure.from_file(str(GAAS_CIF))

    for s in scale_volumes:
        scaled = structure.copy()
        scaled.scale_lattice(structure.volume * s)
        inp = abilab.AbinitInput(structure=scaled, pseudos=["Ga.psp8", "As.psp8"],
                                  pseudo_dir=str(PSEUDO_DIR))
        inp.set_vars(ecut=12, nband=16, paral_kgb=0, iomode=3, tolvrs=1e-8)
        inp.set_kmesh(ngkpt=(4, 4, 4), shiftk=[0, 0, 0])
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
        workdir = Path(__file__).name.replace(".py", "").replace("make_", "flow_")

    flow = build_eos_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
