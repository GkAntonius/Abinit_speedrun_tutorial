"""
Helper functions for the CEMDI 2026 Abinit/AbiPy workshop notebook.

Everything here revolves around a single test system, gallium arsenide (GaAs),
so that the whole 3h session reuses the same structure and pseudopotentials.
Silicon (Si) is used in the manual Task/Flow examples of `1-Task_to_flow.ipynb`,
and again, for comparison, in the band-structure section of `2-Existing_flows.ipynb`.

The ground-state / convergence / band-structure builders below are direct
adaptations of the scripts originally prepared in AbipyExamples
(Production/004-GaAs-gs, 005-GaAs-conv-ecut, 006-GaAs-conv-kpt,
007-GaAs-ebands, 008-Si-ebands).

The Si Task/Flow builders (`si_gs_input`, `build_si_gs_task`,
`si_bandstructure_input`, `build_si_nscf_task`, `build_si_ebands_task_flow`,
`setup_task_manager`) back the `run_si_*.py` scripts generated for
`1-Task_to_flow.ipynb` -- see `../.Examples_generate/generate_examples.py`.

The equation-of-state and DFPT phonon builders are new for this workshop.
The phonon flow is a simplified version -- applied to MgO instead of GaP,
and on a much coarser q-mesh so that it can run in the time available --
of the production DFPT workflow originally in GWPT/Production/020-GaP-dfpt.
MgO is used instead of GaAs here because it's strongly ionic/polar, which
makes the LO-TO splitting (driven by the Born effective charges) much more
visible than it would be for GaAs.

This module expects to live in Tutorial/Notebooks/, next to a sibling
Tutorial/Data/ directory containing:

    Data/Pseudos/{Ga,As,Si}.psp8
    Data/Structures/{mp-2534_GaAs.cif,mp-149_Si.cif}

Both are distributed with this tutorial -- see Tutorial/Data/.
"""

import inspect
from pathlib import Path
import subprocess

import numpy as np

import abipy.abilab as abilab
import abipy.flowtk as flowtk
from abipy.abilab import Structure
from IPython.display import Code, display

# ---------------------------------------------------------------------------
# Notebook helper: syntax-highlighted source, without depending on
# abipy.abilab.print_source (which is really just this, hardcoded to
# pygments+HTML instead of IPython's own Code display class).
# ---------------------------------------------------------------------------
#def print_source(obj):
#    """Display the source of a function/class as syntax-highlighted code."""
#    display(Code(inspect.getsource(obj), language="python"))

def print_source(obj):
    """Let us make use of abilab wrapper (looks much better than IPython)."""
    display(abilab.print_source(obj))


def run_shell_command(command, silent=False):
    """Run a shell command in the background, without waiting for it.

    If `silent` is True, also discard its stdout instead of letting it
    inherit the notebook kernel's own (where it would otherwise show up).
    """
    kwargs = {
        # stderr is always discarded: programs that probe the terminal
        # (e.g. `stty`, called internally by abirun.py) print a harmless
        # "stdin isn't a terminal" complaint there whenever stdin isn't a
        # real tty -- which it never is here, since the notebook kernel's
        # own stdin isn't one either. This is environment noise, not a real
        # error; check `abirun.py FLOWDIR status` or the flow's own logs if
        # something actually goes wrong.
        "stderr": subprocess.DEVNULL,
    }
    if silent:
        kwargs["stdout"] = subprocess.DEVNULL
    subprocess.Popen(command.split(), **kwargs)


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
ALN_CIF = STRUCTURE_DIR / "mp-661_AlN.cif"
MGO_CIF = STRUCTURE_DIR / "mp-1265_MgO.cif"

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


def aln_structure():
    """Return the AbiPy Structure for AlN (Materials Project mp-661)."""
    return Structure.from_file(str(ALN_CIF))


def mgo_structure():
    """Return the AbiPy Structure for MgO (Materials Project mp-1265)."""
    return Structure.from_file(str(MGO_CIF))


# ---------------------------------------------------------------------------
# 0) Si ground-state / band-structure Tasks, built by hand instead of via a
#    Flow -- used by 1-Task_to_flow.ipynb's run_si_gstate.py / run_si_nscf.py
#    / run_si_ebands.py to show the Task -> Flow progression before the rest
#    of this module moves on to GaAs Flows.
# ---------------------------------------------------------------------------
def si_gs_input(ecut=6, ngkpt=(8, 8, 8)):
    """Return a GS input for Si on a homogeneous k-mesh."""
    structure = si_structure()
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
    structure = si_structure()
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


def setup_task_manager(task, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    """Same as setup_manager(), for a standalone Task instead of a Flow."""
    manager = abilab.TaskManager.from_user_config()
    manager = manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    task.set_manager(manager)
    return task


# ---------------------------------------------------------------------------
# 1) Ground-state total energy.
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
# 2) ecut convergence.
# ---------------------------------------------------------------------------
def build_ecut_conv_flow(workdir="flow_gaas_convecut", ecut_list=range(10, 50, 5)):
    """Flow with one SCF task per value of ecut."""
    flow = flowtk.Flow(workdir=workdir)
    for ecut in ecut_list:
        flow.register_scf_task(gs_input(ecut=ecut))
    return flow


# ---------------------------------------------------------------------------
# 3) k-point convergence.
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
# 4) Band structures.
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
# 5) Equation of state / lattice parameter.
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
# 6) DFPT phonons.
# ---------------------------------------------------------------------------
def build_mgo_phonon_flow(workdir="flow_mgo_phonons", ecut=24, ngkpt=(4, 4, 4), ph_ngqpt=(2, 2, 2)):
    """
    PhononFlow for MgO: one GS task producing the WFK file used by DFPT,
    followed by the (symmetry-irreducible) atomic-perturbation tasks needed
    to build the dynamical matrix on a `ph_ngqpt` q-mesh.
    """
    structure = mgo_structure()
    inp = abilab.AbinitInput(structure=structure, pseudos=["Mg.psp8", "O.psp8"],
                              pseudo_dir=str(PSEUDO_DIR))
    inp.set_vars(ecut=ecut, nband=12, paral_kgb=0, iomode=3, tolvrs=1e-8)
    inp.set_kmesh(ngkpt=ngkpt, shiftk=[0, 0, 0])

    return flowtk.PhononFlow.from_scf_input(workdir, inp, ph_ngqpt=ph_ngqpt, with_becs=False)


# ---------------------------------------------------------------------------
# 7) Structural relaxation.
#    Relaxes both the atomic positions and the cell volume of AlN, driven by
#    the computed forces and stresses -- see 2-Existing_flows.ipynb, section
#    2.2, for the corresponding `ionmov`/`optcell` discussion.
# ---------------------------------------------------------------------------
def aln_relax_input(ecut=12, ngkpt=(4, 4, 3)):
    """Return a relaxation input for AlN: relax atomic positions and the
    cell volume (`ionmov=2`, `optcell=1`), converging on the max force
    (`tolmxf`)."""
    structure = aln_structure()
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


def build_aln_relax_flow(workdir="flow_aln_relax"):
    """Flow with a single relaxation task for AlN."""
    flow = flowtk.Flow(workdir=workdir)
    flow.register_relax_task(aln_relax_input())
    return flow


# ---------------------------------------------------------------------------
# Generic scheduler/manager helper reused by every flow builder above.
# ---------------------------------------------------------------------------
def setup_manager(flow, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    manager = flow.manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    for work in flow:
        work.set_manager(manager)
    return flow
