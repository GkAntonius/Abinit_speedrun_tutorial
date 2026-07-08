"""
Helper functions for the CEMDI 2026 Abinit/AbiPy workshop notebook.

Everything here revolves around a single test system, gallium arsenide (GaAs),
so that the whole 3h session reuses the same structure and pseudopotentials.
Silicon (Si) is used once, for comparison, in the band-structure section.

The ground-state / convergence / band-structure builders below are direct
adaptations of the scripts originally prepared in AbipyExamples
(Production/004-GaAs-gs, 005-GaAs-conv-ecut, 006-GaAs-conv-kpt,
007-GaAs-ebands, 008-Si-ebands).

The equation-of-state and DFPT phonon builders are new for this workshop.
The phonon flow is a simplified version -- applied to GaAs instead of GaP,
and on a much coarser q-mesh so that it can run in the time available --
of the production DFPT workflow originally in GWPT/Production/020-GaP-dfpt.

This module expects to live in Tutorial/Notebooks/, next to a sibling
Tutorial/Data/ directory containing:

    Data/Pseudos/{Ga,As,Si}.psp8
    Data/Structures/{mp-2534_GaAs.cif,mp-149_Si.cif}

Both are distributed with this tutorial -- see Tutorial/Data/.
"""

from pathlib import Path

import numpy as np

import abipy.abilab as abilab
import abipy.flowtk as flowtk
from abipy.abilab import Structure

# ---------------------------------------------------------------------------
# Paths. Data/ is a sibling of the Notebooks/ folder this file lives in
# (Tutorial/Data, Tutorial/Notebooks/workshop_lib.py).
# ---------------------------------------------------------------------------
NOTEBOOK_DIR = Path(__file__).resolve().parent
DATA_DIR = NOTEBOOK_DIR.parent / "Data"
PSEUDO_DIR = DATA_DIR / "Pseudos"
STRUCTURE_DIR = DATA_DIR / "Structures"

GAAS_CIF = STRUCTURE_DIR / "mp-2534_GaAs.cif"
SI_CIF = STRUCTURE_DIR / "mp-149_Si.cif"

# High-symmetry path L - Gamma - X, used for both GaAs and Si band structures.
FCC_KPATH = [
    [0.5, 0.0, 0.0],  # L
    [0.0, 0.0, 0.0],  # Gamma
    [0.0, 0.5, 0.5],  # X
]


def gaas_structure():
    """Return the AbiPy Structure for GaAs (Materials Project mp-2534)."""
    return Structure.from_file(str(GAAS_CIF))


def si_structure():
    """Return the AbiPy Structure for Si (Materials Project mp-149)."""
    return Structure.from_file(str(SI_CIF))


# ---------------------------------------------------------------------------
# 1) Ground-state total energy  (Production/004-GaAs-gs)
# ---------------------------------------------------------------------------
def gs_input(ecut=6, ngkpt=(8, 8, 8)):
    """Return a GS input for GaAs on a homogeneous k-mesh."""
    structure = gaas_structure()
    pseudos = ["Ga.psp8", "As.psp8"]

    inp = abilab.AbinitInput(structure=structure, pseudos=pseudos, pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=16, paral_kgb=0, iomode=3)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])
    inp.set_vars(tolvrs=1e-6)
    return inp


def build_gs_flow(workdir="flow_gaas_gstate"):
    """Flow with a single SCF task: the total energy of GaAs."""
    flow = flowtk.Flow(workdir=workdir)
    flow.register_scf_task(gs_input())
    return flow


# ---------------------------------------------------------------------------
# 2) ecut convergence  (Production/005-GaAs-conv-ecut)
# ---------------------------------------------------------------------------
def build_ecut_conv_flow(workdir="flow_gaas_convecut", ecut_list=range(10, 40, 5)):
    """Flow with one SCF task per value of ecut."""
    flow = flowtk.Flow(workdir=workdir)
    for ecut in ecut_list:
        flow.register_scf_task(gs_input(ecut=ecut))
    return flow


# ---------------------------------------------------------------------------
# 3) k-point convergence  (Production/006-GaAs-conv-kpt)
# ---------------------------------------------------------------------------
def build_kpt_conv_flow(workdir="flow_gaas_convkpt", nk_list=(1, 2, 4, 6, 8, 10)):
    """Flow with one SCF task per (automatically-generated) k-mesh density."""
    flow = flowtk.Flow(workdir=workdir)
    for nk in nk_list:
        inp = gs_input(ecut=12)
        inp.set_autokmesh(nk)
        flow.register_scf_task(inp)
    return flow


# ---------------------------------------------------------------------------
# 4) Band structures  (Production/007-GaAs-ebands, 008-Si-ebands)
# ---------------------------------------------------------------------------
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


def build_gaas_ebands_flow(workdir="flow_gaas_ebands"):
    scf_input, nscf_input = _bandstructure_inputs(
        gaas_structure(), ["Ga.psp8", "As.psp8"], ecut=40, ngkpt=(4, 4, 4),
        kptbounds=FCC_KPATH)
    return flowtk.bandstructure_flow(workdir, scf_input, nscf_input)


def build_si_ebands_flow(workdir="flow_si_ebands"):
    scf_input, nscf_input = _bandstructure_inputs(
        si_structure(), ["Si.psp8"], ecut=25, ngkpt=(4, 4, 4),
        kptbounds=FCC_KPATH)
    return flowtk.bandstructure_flow(workdir, scf_input, nscf_input)


# ---------------------------------------------------------------------------
# 5) Equation of state / lattice parameter (new).
#    Several GS runs at scaled volumes around the experimental/relaxed
#    volume, then a Birch-Murnaghan fit with abilab.EOS -- the same idea
#    as the "Determination of the lattice parameters" section of the AbiPy
#    base3 (silicon) lesson, applied here to GaAs.
# ---------------------------------------------------------------------------
def build_eos_flow(workdir="flow_gaas_eos", scale_volumes=tuple(np.arange(0.94, 1.07, 0.02))):
    """Flow with one SCF task per isotropically-scaled volume of GaAs."""
    flow = flowtk.Flow(workdir=workdir)
    structure = gaas_structure()

    for s in scale_volumes:
        scaled = structure.copy()
        scaled.scale_lattice(structure.volume * s)
        inp = abilab.AbinitInput(structure=scaled, pseudos=["Ga.psp8", "As.psp8"],
                                  pseudo_dir=str(PSEUDO_DIR))
        inp.set_vars(ecut=12, nband=16, paral_kgb=0, iomode=3, tolvrs=1e-8)
        inp.set_kmesh(ngkpt=(4, 4, 4), shiftk=[0, 0, 0])
        flow.register_scf_task(inp)

    return flow


# ---------------------------------------------------------------------------
# 6) DFPT phonons (new; simplified/adapted from GWPT/Production/020-GaP-dfpt).
# ---------------------------------------------------------------------------
def build_phonon_flow(workdir="flow_gaas_phonons", ecut=8, ngkpt=(4, 4, 4), ph_ngqpt=(2, 2, 2)):
    """
    PhononFlow for GaAs: one GS task producing the WFK file used by DFPT,
    followed by the (symmetry-irreducible) atomic-perturbation tasks needed
    to build the dynamical matrix on a `ph_ngqpt` q-mesh.
    """
    structure = gaas_structure()
    inp = abilab.AbinitInput(structure=structure, pseudos=["Ga.psp8", "As.psp8"],
                              pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=16, paral_kgb=0, iomode=3, tolvrs=1e-8)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])

    return flowtk.PhononFlow.from_scf_input(workdir, inp, ph_ngqpt=ph_ngqpt, with_becs=True)


# ---------------------------------------------------------------------------
# Generic scheduler/manager helper reused by every flow builder above.
# ---------------------------------------------------------------------------
def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow
