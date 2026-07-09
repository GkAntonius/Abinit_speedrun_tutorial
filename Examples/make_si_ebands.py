#!/usr/bin/env python
"""
Companion to Section 5 ("Band structures: GaAs vs Si") of the workshop
notebook, Si half.

Builds the same flow as `workshop_lib.build_si_ebands_flow()`: a
ground-state run on a homogeneous k-mesh followed by a non-self-consistent
run along the L-Gamma-X path, this time for silicon. See also
`make_gaas_ebands.py` for the GaAs run this is compared against -- GaAs has a
direct gap at Gamma, while silicon's fundamental gap is indirect.

Usage
-----
    python make_si_ebands.py
    abirun.py flow_si_ebands scheduler
    abirun.py flow_si_ebands status
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


def _bandstructure_inputs(structure, pseudos, ecut, ngkpt, kptbounds,
                           nband_scf=16, nband_nscf=40):
    multi = abilab.MultiDataset(structure=structure, pseudos=pseudos,
                                 pseudo_dir=str(PSEUDO_DIR), ndtset=2)
    multi.set_vars(ecut=ecut, nband=nband_scf, nbdbuf=4, paral_kgb=0, iomode=3)

    # Dataset 1: GS run on a homogeneous k-mesh.
    multi[0].set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    multi[0].set_vars(tolvrs=1e-8)

    # Dataset 2: NSCF run along a k-path.
    multi[1].set_kpath(ndivsm=10, kptbounds=kptbounds)
    multi[1].set_vars(nband=nband_nscf, tolwfr=1e-12)

    return multi.split_datasets()


def build_si_ebands_flow(workdir):
    scf_input, nscf_input = _bandstructure_inputs(
        Structure.from_file(str(SI_CIF)), ["Si.psp8"], ecut=25, ngkpt=(4, 4, 4),
        kptbounds=FCC_KPATH)
    return flowtk.bandstructure_flow(workdir, scf_input, nscf_input)


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

    flow = build_si_ebands_flow(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()
