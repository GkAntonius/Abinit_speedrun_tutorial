#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.3 (band structure).

Builds the same flow as `workshop_lib.build_gaas_ebands_flow()`: a
ground-state run on a homogeneous k-mesh followed by a non-self-consistent
run along the L-Gamma-X path. This flow was already run ahead of time for
the tutorial -- a `bandstructure_flow` built in one call, in contrast with
the manual, task-by-task Si band structure from `1-Task_to_flow.ipynb`
(`run_si_gstate.py` / `run_si_nscf.py` / `run_si_ebands.py`). Compare the
two: GaAs has a direct gap at Gamma, while silicon's fundamental gap is
indirect.

Usage
-----
    python make_gaas_ebands.py
    abirun.py flow_gaas_ebands scheduler
    abirun.py flow_gaas_ebands status
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


def _bandstructure_inputs(structure, pseudos, ecut, ngkpt, kptbounds,
                           nband_scf=20, nband_nscf=40):
    multi = abilab.MultiDataset(structure=structure, pseudos=pseudos,
                                 pseudo_dir=str(PSEUDO_DIR), ndtset=2)
    multi.set_vars(ecut=ecut, nband=nband_scf, nbdbuf=4, paral_kgb=0, iomode=3)

    # Dataset 1: GS run on a homogeneous k-mesh.
    multi[0].set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    multi[0].set_vars(tolvrs=1e-8)
    multi[0].set_vars(occopt=3, tsmear=0.05)

    # Dataset 2: NSCF run along a k-path.
    multi[1].set_kpath(ndivsm=20, kptbounds=kptbounds)
    multi[1].set_vars(nband=nband_nscf, tolwfr=1e-12)

    return multi.split_datasets()


def build_gaas_ebands_flow(workdir):
    scf_input, nscf_input = _bandstructure_inputs(
        Structure.from_file(str(GAAS_CIF)), ["Ga.psp8", "As.psp8"], ecut=40, ngkpt=(8, 8, 8),
        kptbounds=FCC_KPATH)
    return flowtk.bandstructure_flow(workdir, scf_input, nscf_input)


def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow


def build_flow():
    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("make_", "flow_")

    flow = build_gaas_ebands_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=10, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
