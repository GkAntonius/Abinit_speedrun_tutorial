#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.4 (phonons).

Builds the same flow as `workshop_lib.build_mgo_phonon_flow()`: a
ground-state task producing the WFK file, followed by the
symmetry-irreducible DFPT atomic-perturbation tasks needed to assemble the
dynamical matrix (and Born effective charges) on a coarse q-mesh. This flow
was already run ahead of time for the tutorial -- it has more tasks than
the others, so it's the best candidate for actually running yourself with
`nohup` (see below) rather than waiting on it in a foreground shell.

MgO (rocksalt) is a strongly ionic, polar material -- a good showcase for
the LO-TO splitting driven by the Born effective charges computed here.

Usage
-----
    python make_mgo_phonons.py
    abirun.py flow_mgo_phonons scheduler
    abirun.py flow_mgo_phonons status

    nohup python make_mgo_phonons.py > log 2> err &   # ... run in the background
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
MGO_CIF = STRUCTURE_DIR / 'mp-1265_MgO.cif'


def build_mgo_phonon_flow(workdir, ecut=24, ngkpt=(4, 4, 4), ph_ngqpt=(2, 2, 2)):
    """
    PhononFlow for MgO: one GS task producing the WFK file used by DFPT,
    followed by the (symmetry-irreducible) atomic-perturbation tasks needed
    to build the dynamical matrix on a `ph_ngqpt` q-mesh.
    """
    structure = Structure.from_file(str(MGO_CIF))
    inp = abilab.AbinitInput(structure=structure, pseudos=["Mg.psp8", "O.psp8"],
                              pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=12, paral_kgb=0, iomode=3, tolvrs=1e-8)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])

    return flowtk.PhononFlow.from_scf_input(workdir, inp, ph_ngqpt=ph_ngqpt, with_becs=False)


def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow


def build_flow():
    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("make_", "flow_")

    flow = build_mgo_phonon_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
