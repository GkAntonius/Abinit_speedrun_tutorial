#!/usr/bin/env python
"""
Companion to Section 7 ("Phonons from DFPT") of the workshop notebook.

Builds the same flow as `workshop_lib.build_phonon_flow()`: a ground-state
task producing the WFK file, followed by the symmetry-irreducible DFPT
atomic-perturbation tasks needed to assemble the dynamical matrix (and Born
effective charges) on a coarse q-mesh. This has more tasks than the other
example flows, so it is the best candidate for running in the background
with `nohup` (see below) rather than waiting on it in a foreground shell.

Usage
-----
    python make_gaas_phonons.py
    abirun.py flow_gaas_phonons scheduler   # repeat if interrupted
    abirun.py flow_gaas_phonons status       # check progress / list tasks

    nohup python make_gaas_phonons.py > log 2> err &   # ... run in the background
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


def build_phonon_flow(workdir, ecut=8, ngkpt=(4, 4, 4), ph_ngqpt=(2, 2, 2)):
    """
    PhononFlow for GaAs: one GS task producing the WFK file used by DFPT,
    followed by the (symmetry-irreducible) atomic-perturbation tasks needed
    to build the dynamical matrix on a `ph_ngqpt` q-mesh.
    """
    structure = Structure.from_file(str(GAAS_CIF))
    inp = abilab.AbinitInput(structure=structure, pseudos=["Ga.psp8", "As.psp8"],
                              pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=16, paral_kgb=0, iomode=3, tolvrs=1e-8)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])

    return flowtk.PhononFlow.from_scf_input(workdir, inp, ph_ngqpt=ph_ngqpt, with_becs=True)


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

    flow = build_phonon_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
