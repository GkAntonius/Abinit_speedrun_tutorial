#!/usr/bin/env python
"""
Companion to `3-Relaxation.ipynb`.

Builds the same flow as `workshop_lib.build_aln_relax_flow()`: a single
relaxation task for AlN, with `ionmov=2` (Broyden atomic relaxation) and
`optcell=1` (also optimize the cell volume, keeping its shape fixed --
`rprim` unchanged, `acell` dilated isotropically), converging on the max
force (`tolmxf`) instead of the `tolvrs` used for a fixed-geometry SCF run.
This flow was already run ahead of time for the tutorial;
`save_aln_structure.py` extracts the relaxed structure from its output.
Re-run this script yourself if you want to reproduce or tweak it.

Usage
-----
    python make_aln_relax.py
    abirun.py flow_aln_relax scheduler
    abirun.py flow_aln_relax status
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
ALN_CIF = STRUCTURE_DIR / 'mp-661_AlN.cif'


def aln_relax_input(ecut=12, ngkpt=(4, 4, 3)):
    """Return a relaxation input for AlN: relax atomic positions and the
    cell volume (`ionmov=2`, `optcell=1`), converging on the max force
    (`tolmxf`)."""
    structure = Structure.from_file(str(ALN_CIF))
    pseudos = ["Al.psp8", "N.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(
        ecut=ecut,
        nband=14,
        ionmov=2,
        optcell=1,
        strfact=100,
        tolvrs=1e-6,
        tolmxf=1e-5,
        ntime=100,
        iomode=3,
    )
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    return inp


def build_aln_relax_flow(workdir):
    """Flow with a single relaxation task for AlN."""
    flow = flowtk.Flow(workdir=workdir)
    flow.register_relax_task(aln_relax_input())
    return flow


def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow


def build_flow(workdir=None):
    # Set working directory (default is constructed from the script name,
    # stripping a leading "run_" or "make_" and prepending "flow_").
    if not workdir:
        name = Path(__file__).name.replace(".py", "")
        for prefix in ("run_", "make_"):
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        workdir = f"flow_{name}"

    flow = build_aln_relax_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
