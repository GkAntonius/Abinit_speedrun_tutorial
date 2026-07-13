#!/usr/bin/env python
"""
Generate the standalone `run_*.py` / `make_*.py` example scripts in this
directory from `../Notebooks/workshop_lib.py`.

Naming convention: the three `run_si_*.py` scripts (used in
`1-Task_to_flow.ipynb`) build and launch a Task/Flow live, in one sitting,
and print their own status when done. Everything under
`2-Existing_flows.ipynb` (convergence, band structures, phonons) is a
`make_*` script instead: these flows take longer, so they were already run
ahead of time for the tutorial, and the notebooks mostly analyze their
(pre-existing) results -- `make_*` here means "this is how that flow was
constructed", not "run this now". `run_*_anaddb.py` and `plot_*.py` scripts
are a third flavor: they don't build a Task/Flow at all, just open the
output of one that already ran and post-process/plot it. All flavors are
generated the same way, via a `Recipe.kind` (see below) that only changes
the part of the script after the header/path setup.

Why generate rather than hand-write: each script is meant to be copied by a
student into their own work directory and run on its own, so it must NOT
`import workshop_lib`. But the notebooks' analysis cells assume the flows
were built with *exactly* the same `AbinitInput`/`Flow` code as
`workshop_lib.py` -- so hand-duplicating that code into each script would
risk the two silently drifting apart. Instead, this script pulls the
relevant functions (input builders, `build_*_flow()`, `setup_manager()`)
straight out of `workshop_lib.py` with `inspect.getsource()`, inlines the
`gaas_structure()`/`si_structure()` calls, and stitches the result into a
self-contained script with its own path setup.

Whenever `workshop_lib.py` changes, re-run this from `Tutorial/Examples/`:

    python generate_examples.py
"""
import inspect
import re
import sys
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = PARENT / 'Examples'

NOTEBOOKS_DIR = PARENT / "Notebooks"
sys.path.insert(0, str(NOTEBOOKS_DIR))
import workshop_lib as wlib  # noqa: E402  (needs the sys.path tweak above)

WORKDIR_DEFAULT_RE = re.compile(r'workdir="flow_[A-Za-z0-9_]*"')


def src(name):
    """Source of a top-level function in workshop_lib.py, by name.

    `gaas_structure()`/`si_structure()`/`aln_structure()`/`mgo_structure()`
    calls are inlined as `Structure.from_file(str(GAAS_CIF))`/`...(str(SI_CIF))`/
    `...(str(ALN_CIF))`/`...(str(MGO_CIF))` (so the generated script doesn't
    need those four helpers), and a `workdir="flow_..."` default, if
    present, is stripped so the caller must always pass `workdir` explicitly.
    """
    text = inspect.getsource(getattr(wlib, name)).rstrip("\n")
    text = text.replace("gaas_structure()", "Structure.from_file(str(GAAS_CIF))")
    text = text.replace("si_structure()", "Structure.from_file(str(SI_CIF))")
    text = text.replace("aln_structure()", "Structure.from_file(str(ALN_CIF))")
    text = text.replace("mgo_structure()", "Structure.from_file(str(MGO_CIF))")
    text = WORKDIR_DEFAULT_RE.sub("workdir", text, count=1)
    return text


class Recipe:
    """
    `kind` picks the `main()` footer (see `render()`):

    * "make_flow" (default) -- builds a Flow and just pickles it, for
      `abirun.py ... scheduler` to pick up later. Used under
      `2-Existing_flows.ipynb`.
    * "run_task" -- builds a single Task and runs it synchronously
      (`task.start_and_wait()`). Used by steps 1-2 of `1-Task_to_flow.ipynb`.
    * "run_flow" -- builds a Flow but, instead of a scheduler, runs each of
      its Tasks synchronously in a plain loop. Used by step 3 of
      `1-Task_to_flow.ipynb`.
    * "script" -- doesn't build anything; `body` is the literal `main()` (+
      `if __name__ == "__main__":` guard) of a script that just opens the
      output of an existing Task/Flow/anaddb run and post-processes or
      plots it. Used by `save_aln_structure.py`, `plot_si_bands_*.py`,
      `plot_gaas_convecut.py`, `run_mgo_anaddb.py` and `plot_mgo_phonons.py`.

    `build_expr` is the expression (given `workdir`) that builds the
    Task/Flow for "run_task"/"run_flow"; "make_flow" instead calls
    `entry_fn(workdir=workdir)`.
    """
    def __init__(self, fname, docstring, chunks=(), entry_fn=None,
                 extra_imports="", needs_gaas_cif=False, needs_si_cif=False,
                 needs_aln_cif=False, needs_mgo_cif=False, needs_fcc_kpath=False,
                 kind="make_flow", build_expr=None, timelimit_hour=2.0, body=None):
        self.fname = fname
        self.docstring = docstring
        self.chunks = chunks
        self.entry_fn = entry_fn
        self.extra_imports = extra_imports
        self.needs_gaas_cif = needs_gaas_cif
        self.needs_si_cif = needs_si_cif
        self.needs_aln_cif = needs_aln_cif
        self.needs_mgo_cif = needs_mgo_cif
        self.needs_fcc_kpath = needs_fcc_kpath
        self.kind = kind
        self.build_expr = build_expr
        self.timelimit_hour = timelimit_hour
        self.body = body


RECIPES = [
    Recipe(
        fname="run_si_gstate.py",
        docstring="""\
Companion to `1-Task_to_flow.ipynb`, step 1.

The simplest possible unit of work in AbiPy: a single `AbinitTask` wrapping
one `AbinitInput`, built and run directly -- no `Flow`, no `Work`, just one
Task. Produces the ground-state density of silicon, which `run_si_nscf.py`
(step 2) depends on.

Usage
-----
    python run_si_gstate.py
""",
        chunks=["si_gs_input", "build_si_gs_task", "setup_task_manager"],
        needs_si_cif=True,
        kind="run_task",
        build_expr="build_si_gs_task(workdir)",
        timelimit_hour=0.1,
    ),
    Recipe(
        fname="run_si_nscf.py",
        docstring="""\
Companion to `1-Task_to_flow.ipynb`, step 2.

A second `AbinitTask` (non-self-consistent, along a k-point path), manually
depending on the density produced by `run_si_gstate.py` (step 1) via a
*hardcoded path* to that task's output directory. This works, but it's
fragile -- if step 1's workdir changes, this breaks silently. `run_si_ebands.py`
(step 3) shows how a `Flow` fixes that by tracking the dependency between
tasks instead of a path.

Usage
-----
    python run_si_gstate.py   # must run first -- produces the DEN file below
    python run_si_nscf.py
""",
        chunks=["si_bandstructure_input", "build_si_nscf_task", "setup_task_manager"],
        needs_si_cif=True,
        needs_fcc_kpath=True,
        kind="run_task",
        build_expr="build_si_nscf_task(workdir, density='task_si_gstate/outdata/out_DEN.nc')",
        timelimit_hour=0.5,
    ),
    Recipe(
        fname="plot_si_bands_1.py",
        docstring="""\
Companion to `1-Task_to_flow.ipynb`, step 2 (plotting).

Plots the band structure from `task_si_nscf/`, the output of the two
manually-chained tasks in `run_si_gstate.py` + `run_si_nscf.py`. Compare
with `plot_si_bands_2.py`, which plots the same physics from the `Flow`
version (`run_si_ebands.py`) instead.

Usage
-----
    python plot_si_bands_1.py
""",
        extra_imports="import numpy as np\n\nimport matplotlib.pyplot as plt",
        kind="script",
        body='''\
def main():
    # Get task directory
    dirname = SCRIPT_DIR / 'task_si_nscf'
    gsr_path = dirname / 'outdata' / 'out_GSR.nc'

    # Extract results
    gsr = abilab.abiopen(str(gsr_path))
    ebands = gsr.ebands

    fig = ebands.plot(color='b', show=False)
    ax = fig.gca()
    ax.set_ylim(-12.5, 7.5)

    # Make file name for figure
    plotdir = Path('Plots')
    plotdir.mkdir(exist_ok=True)
    figname = plotdir / Path(__file__).name.replace(".py", ".png").replace("plot_", "")
    print(figname)

    # Save figure file
    fig.savefig(figname, dpi=200)

    # Display the figure
    plt.show()

if __name__ == "__main__":
    main()''',
    ),
    Recipe(
        fname="run_si_ebands.py",
        docstring="""\
Companion to `1-Task_to_flow.ipynb`, step 3.

The same two tasks as `run_si_gstate.py` + `run_si_nscf.py` (steps 1-2),
this time registered together in a `Work` inside a `Flow`, with the
dependency expressed as `deps={gs_task: 'DEN'}` -- a reference to the task
object itself, not a hardcoded path. This is the "Task to Flow" step: the
same calculation, but AbiPy now tracks the dependency between tasks for
you, which is what lets a `Flow` be built once and (re)run reliably,
in the right order, however many tasks it has.

Usage
-----
    python run_si_ebands.py
""",
        chunks=["si_gs_input", "build_si_gs_task", "si_bandstructure_input",
                "build_si_nscf_task", "build_si_ebands_task_flow", "setup_manager"],
        needs_si_cif=True,
        needs_fcc_kpath=True,
        kind="run_flow",
        build_expr="build_si_ebands_task_flow(workdir)",
        timelimit_hour=0.5,
    ),
    Recipe(
        fname="plot_si_bands_2.py",
        docstring="""\
Companion to `1-Task_to_flow.ipynb`, step 3 (plotting).

Plots the band structure from `flow_si_ebands/`, the output of the `Flow`
version of the same calculation (`run_si_ebands.py`). Compare with
`plot_si_bands_1.py`, which plots the same physics from the two
manually-chained tasks instead.

Usage
-----
    python plot_si_bands_2.py
""",
        extra_imports="import numpy as np\n\nimport matplotlib.pyplot as plt",
        kind="script",
        body='''\
def main():
    # Get flow directory
    dirname = SCRIPT_DIR / 'flow_si_ebands'
    flow = flowtk.Flow.from_file(dirname)     # Open flow object.
    task = flow[0][1]                         # Select the second task of the first work.
    gsr_path = task.outdir.has_abiext('GSR')  # Retrieve output GSR file of this task.

    # Extract results
    gsr = abilab.abiopen(str(gsr_path))
    ebands = gsr.ebands

    fig = ebands.plot(color='b', show=False)
    ax = fig.gca()
    ax.set_ylim(-12.5, 7.5)

    # Make file name for figure
    plotdir = Path('Plots')
    plotdir.mkdir(exist_ok=True)
    figname = plotdir / Path(__file__).name.replace(".py", ".png").replace("plot_", "")
    print(figname)

    # Save figure file
    fig.savefig(figname, dpi=200)

    # Display the figure
    plt.show()

if __name__ == "__main__":
    main()''',
    ),
    Recipe(
        fname="make_si_ebands.py",
        docstring="""\
Companion to `1-Task_to_flow.ipynb`, step 3.

The same two tasks as `run_si_gstate.py` + `run_si_nscf.py` (steps 1-2),
this time registered together in a `Work` inside a `Flow`, with the
dependency expressed as `deps={gs_task: 'DEN'}` -- a reference to the task
object itself, not a hardcoded path. This is the "Task to Flow" step: the
same calculation, but AbiPy now tracks the dependency between tasks for
you, which is what lets a `Flow` be built once and (re)run reliably,
in the right order, however many tasks it has.

Usage
-----
    python make_si_ebands.py
    abirun.py flow_si_ebands scheduler
""",
        chunks=["si_gs_input", "build_si_gs_task", "si_bandstructure_input",
                "build_si_nscf_task", "build_si_ebands_task_flow", "setup_manager"],
        needs_si_cif=True,
        needs_fcc_kpath=True,
        kind="make_flow",
        build_expr="build_si_ebands_task_flow(workdir)",
        timelimit_hour=0.5,
    ),
    Recipe(
        fname="make_gaas_convecut.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.1 (ecut convergence).

Builds the same flow as `workshop_lib.build_ecut_conv_flow()`: one SCF task
per value of `ecut`. This flow was already run ahead of time for the
tutorial; the notebook's `GsrRobot` / `ConvergenceAnalyzer` cells collect
the results into a convergence plot. Re-run this script yourself if you
want to reproduce or tweak it.

Usage
-----
    python make_gaas_convecut.py
    abirun.py flow_gaas_convecut scheduler
    abirun.py flow_gaas_convecut status
""",
        chunks=["gs_input", "build_ecut_conv_flow", "setup_manager"],
        entry_fn="build_ecut_conv_flow",
        needs_gaas_cif=True,
    ),
    Recipe(
        fname="plot_gaas_convecut.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.1 (ecut convergence) --
plotting.

Opens `flow_gaas_convecut/`, the output of `make_gaas_convecut.py`, and
fits/plots the ecut convergence with
`abipy.tools.plotting.ConvergenceAnalyzer` -- the same analysis shown
inline in the notebook, saved here to `Plots/gaas_convecut_convecut.png`.

Usage
-----
    python plot_gaas_convecut.py
""",
        extra_imports="from abipy.tools.plotting import ConvergenceAnalyzer",
        kind="script",
        body='''\
def main():
    # Get flow directory
    workdir = SCRIPT_DIR / 'flow_gaas_convecut'
    print(workdir)

    # Make file name for figure
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '')
    figname = str(prefix) + '_convecut.png'
    print(figname)

    # Extract results
    ecut_Ha = []
    energy_per_atom_eV = []

    flow = flowtk.Flow.from_file(str(workdir))

    for work in flow:
        # Select task in work
        task = work[0]

        gsr_path = task.outdir.has_abiext('GSR')
        print(gsr_path)

        gsr = abilab.abiopen(gsr_path)
        ecut_Ha.append(gsr.ecut)
        energy_per_atom_eV.append(gsr.energy_per_atom)

    # Plot results
    ca = ConvergenceAnalyzer.from_xy_label_vals("ecut (Ha)", ecut_Ha,
                                                "E/natom (eV)", energy_per_atom_eV, tols=1e-3)

    fig = ca.plot(savefig=str(figname), show=True, dpi=200)

if __name__ == "__main__":
    main()''',
    ),
    Recipe(
        fname="make_gaas_convkpt.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.1 (k-point convergence).

Builds the same flow as `workshop_lib.build_kpt_conv_flow()`: one SCF task
per automatically-generated k-mesh density. This flow was already run ahead
of time for the tutorial; the notebook's `GsrRobot` cell collects the
results and plots energy per atom against k-point density. Re-run this
script yourself if you want to reproduce or tweak it.

Usage
-----
    python make_gaas_convkpt.py
    abirun.py flow_gaas_convkpt scheduler
    abirun.py flow_gaas_convkpt status
""",
        chunks=["gs_input", "build_kpt_conv_flow", "setup_manager"],
        entry_fn="build_kpt_conv_flow",
        needs_gaas_cif=True,
    ),
    Recipe(
        fname="make_gaas_ebands.py",
        docstring="""\
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
""",
        chunks=["_bandstructure_inputs", "build_gaas_ebands_flow", "setup_manager"],
        entry_fn="build_gaas_ebands_flow",
        needs_gaas_cif=True,
        needs_fcc_kpath=True,
    ),
    Recipe(
        fname="make_mgo_phonons.py",
        docstring="""\
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
    abirun.py flow_mgo_phonons scheduler   # repeat if interrupted
    abirun.py flow_mgo_phonons status       # check progress / list tasks

    nohup python make_mgo_phonons.py > log 2> err &   # ... run in the background
""",
        chunks=["build_mgo_phonon_flow", "setup_manager"],
        entry_fn="build_mgo_phonon_flow",
        needs_mgo_cif=True,
    ),
    Recipe(
        fname="run_mgo_anaddb.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.4 (phonons) -- the anaddb
post-processing step.

Opens `flow_mgo_phonons/w1/outdata/out_DDB`, the output of
`make_mgo_phonons.py`, and calls `anaget_phbst_and_phdos_files` to
Fourier-interpolate the dynamical matrix onto a dense q-mesh (for the
phonon DOS) and along a high-symmetry q-path (for the phonon band
structure). Results are written to `task_mgo_anaddb/` -- `plot_mgo_phonons.py`
reads them from there.

Usage
-----
    python run_mgo_anaddb.py
""",
        kind="script",
        body='''\
def main():
    ddb_path = SCRIPT_DIR / 'flow_mgo_phonons' / 'w1' / 'outdata' / 'out_DDB'
    workdir = SCRIPT_DIR / 'task_mgo_anaddb'

    with abilab.abiopen(str(ddb_path)) as ddb:
        phbst_file, phdos_file = ddb.anaget_phbst_and_phdos_files(
            workdir=str(workdir),
            nqsmall=10,
            ndivsm=40,
            asr=2,
            chneut=1,
            dipdip=1,
            dos_method='tetra',
            lo_to_splitting='automatic',
            mpi_procs=1,
            verbose=True)

if __name__ == "__main__":
    main()''',
    ),
    Recipe(
        fname="plot_mgo_phonons.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.4 (phonons) -- plotting.

Plots the phonon band structure from `task_mgo_anaddb/`, the output of
`run_mgo_anaddb.py`. Several alternative plots (phonon DOS, projected DOS,
colored/matched bands, harmonic thermodynamics, ...) are left commented
out below as a starting point -- uncomment whichever you need.

Usage
-----
    python plot_mgo_phonons.py
""",
        kind="script",
        body='''\
def main():
    workdir = SCRIPT_DIR / 'task_mgo_anaddb'
    out_anaddb_path = workdir / 'outdata' / 'out_anaddb.nc'
    phbst_path = workdir / 'outdata' / 'out_PHBST.nc'
    phdos_path = workdir / 'outdata' / 'out_PHDOS.nc'

    plotdir = Path('Plots')
    plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '.png')

    with abilab.abiopen(str(phbst_path)) as phbst_file:
        phbands = phbst_file.phbands

    with abilab.abiopen(str(phdos_path)) as phdos_file:
        phdos = phdos_file.phdos
        #phbands.read_non_anal_from_file(str(out_anaddb_path))

    #fig = phbands.plot_with_phdos(phdos, units="mev", show=False); fig.savefig(str(prefix) + '_phbs_dos.png', dpi=200)
    #fig = phbands.plot_colored_matched(units="mev", show=False); fig.savefig(str(prefix) + '_phbs_colored.png', dpi=200)
    fig = phbands.plot(units="mev", color='b', show=False)
    ax = fig.gca()
    ax.set_ylim(0, 80)
    fig.savefig(str(prefix) + '_phbands.png', dpi=200)

if __name__ == "__main__":
    main()''',
    ),
    Recipe(
        fname="make_aln_relax.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.2 (relaxation).

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
""",
        chunks=["aln_relax_input", "build_aln_relax_flow", "setup_manager"],
        entry_fn="build_aln_relax_flow",
        needs_aln_cif=True,
    ),
    Recipe(
        fname="save_aln_structure.py",
        docstring="""\
Companion to `2-Existing_flows.ipynb`, section 2.2 (relaxation).

Opens `flow_aln_relax/`, the output of `make_aln_relax.py`, and saves the
relaxed AlN structure (atomic positions and cell) to a `.cif` file --
useful if you want to reuse the relaxed geometry as the input structure of
a later calculation (e.g. a band structure or phonon flow at the relaxed
volume, instead of the experimental one).

Usage
-----
    python save_aln_structure.py
""",
        kind="script",
        body='''\
def main():
    # Get flow directory
    workdir = SCRIPT_DIR / 'flow_aln_relax'
    flow = flowtk.Flow.from_file(workdir)     # Open flow object.
    task = flow[0][0]                         # Select the first task of the first work.
    gsr_path = task.outdir.has_abiext('GSR')  # Retrieve output GSR file of this task.

    # Extract results
    gsr = abilab.abiopen(str(gsr_path))
    structure = gsr.structure
    print(structure)

    # Make file name for the relaxed structure
    savedir = Path('Data');  savedir.mkdir(exist_ok=True)
    filename = savedir / 'AlN_relaxed.cif'

    print(filename)
    structure.to(filename=str(filename))

if __name__ == "__main__":
    main()''',
    ),
]


def render(recipe):
    header = [
        "#!/usr/bin/env python",
        '"""',
        recipe.docstring.rstrip("\n"),
        '"""',
        "from pathlib import Path",
        "",
    ]
    if recipe.extra_imports:
        header.append(recipe.extra_imports)
        header.append("")
    header += [
        "import abipy.abilab as abilab",
        "import abipy.flowtk as flowtk",
        "from abipy.abilab import Structure",
        "",
        "# This script is meant to be copied -- together with the rest of this",
        "# Tutorial/ directory -- into your own work directory. Data/Pseudos and",
        "# Data/Structures are located relative to *this file*.",
        "SCRIPT_DIR = Path(__file__).resolve().parent",
        'DATA_DIR = SCRIPT_DIR.parent / "Data"',
        'PSEUDO_DIR = DATA_DIR / "Pseudos"',
        'STRUCTURE_DIR = DATA_DIR / "Structures"',
    ]
    if recipe.needs_gaas_cif:
        header.append(f"GAAS_CIF = STRUCTURE_DIR / {wlib.GAAS_CIF.name!r}")
    if recipe.needs_si_cif:
        header.append(f"SI_CIF = STRUCTURE_DIR / {wlib.SI_CIF.name!r}")
    if recipe.needs_aln_cif:
        header.append(f"ALN_CIF = STRUCTURE_DIR / {wlib.ALN_CIF.name!r}")
    if recipe.needs_mgo_cif:
        header.append(f"MGO_CIF = STRUCTURE_DIR / {wlib.MGO_CIF.name!r}")
    if recipe.needs_fcc_kpath:
        header.append(f"FCC_KPATH = {wlib.FCC_KPATH!r}")

    chunks = [src(name) for name in recipe.chunks]

    if recipe.kind == "make_flow":
        footer = f'''def build_flow(workdir=None):
    # Set working directory (default is constructed from the script name,
    # stripping a leading "run_" or "make_" and prepending "flow_").
    if not workdir:
        name = Path(__file__).name.replace(".py", "")
        for prefix in ("run_", "make_"):
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        workdir = f"flow_{{name}}"

    flow = {recipe.entry_fn}(workdir=workdir)
    flow = setup_manager(flow, mpi_procs=4, omp_threads=1)
    return flow


if __name__ == "__main__":
    flow = build_flow()
    flow.build_and_pickle_dump()'''

    elif recipe.kind == "run_task":
        footer = f'''def main():

    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("run_", "task_")

    # Initialize the task object
    task = {recipe.build_expr}
    task = setup_task_manager(task, mpi_procs=4, timelimit_hour={recipe.timelimit_hour})

    # Remove a previous run, if it exists.
    if Path(workdir).exists():
        print(f'Removing existing directory: {{workdir}}/')
        task.rmtree()

    # Create directory, write inputs and link external files.
    print(f'Building task in directory: {{workdir}}/')
    task.build()
    task.make_links()

    # Run the calculation and wait for the result
    print('Running task...')
    task.start_and_wait()

    # Report calculation status
    status = task.check_status()
    print(f'Status: {{status}}')


if __name__ == "__main__":
    main()'''

    elif recipe.kind == "run_flow":
        footer = f'''def main():

    # Construct workdir from the file name
    workdir = Path(__file__).name.replace(".py", "").replace("run_", "flow_")

    # Initialize the flow object
    flow = {recipe.build_expr}
    flow = setup_manager(flow, mpi_procs=4, timelimit_hour={recipe.timelimit_hour})

    # Remove a previous run, if it exists.
    if Path(workdir).exists():
        print(f'Removing existing directory: {{workdir}}/')
        flow.rmtree()

    # Create directory, write inputs and link external files.
    print(f'Building flow in directory: {{workdir}}/')
    flow.build_and_pickle_dump()

    # Run each of the tasks sequentially and wait for the result.
    print('Running flow...')
    for work in flow:
        for task in work:
            task.start_and_wait()

            # Report calculation status
            name = task.name
            status = task.check_status()
            print(f'Status of task {{name}}: {{status}}')


if __name__ == "__main__":
    main()'''

    elif recipe.kind == "script":
        footer = recipe.body.strip("\n")

    else:
        raise ValueError(f"Unknown recipe kind: {recipe.kind!r}")

    parts = ["\n".join(header)] + chunks + [footer]
    return "\n\n\n".join(parts) + "\n"

# =========================================================================== #


def main():
    for recipe in RECIPES:
        out_path = EXAMPLES_DIR / recipe.fname
        out_path.write_text(render(recipe))
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
