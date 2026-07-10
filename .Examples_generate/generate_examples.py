#!/usr/bin/env python
"""
Generate the standalone `run_*.py` / `make_*.py` example scripts in this
directory from `../Notebooks/workshop_lib.py`.

Naming convention: `run_gaas_gstate.py` (used in `1-Task_to_flow.ipynb`) is
a `run_*` script -- simple enough to build and launch live, in one sitting.
Everything under `2-Existing_flows.ipynb` (convergence, band structures,
phonons) is a `make_*` script instead: these flows take longer, so they
were already run ahead of time for the tutorial, and the notebooks mostly
analyze their (pre-existing) results -- `make_*` here means "this is how
that flow was constructed", not "run this now".

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

    `gaas_structure()`/`si_structure()` calls are inlined as
    `Structure.from_file(str(GAAS_CIF))`/`...(str(SI_CIF))` (so the
    generated script doesn't need those two helpers), and a `workdir="flow_
    ..."` default, if present, is stripped so the caller must always pass
    `workdir` explicitly.
    """
    text = inspect.getsource(getattr(wlib, name)).rstrip("\n")
    text = text.replace("gaas_structure()", "Structure.from_file(str(GAAS_CIF))")
    text = text.replace("si_structure()", "Structure.from_file(str(SI_CIF))")
    text = WORKDIR_DEFAULT_RE.sub("workdir", text, count=1)
    return text


class Recipe:
    def __init__(self, fname, docstring, chunks, entry_fn,
                 extra_imports="", needs_gaas_cif=False, needs_si_cif=False,
                 needs_fcc_kpath=False):
        self.fname = fname
        self.docstring = docstring
        self.chunks = chunks
        self.entry_fn = entry_fn
        self.extra_imports = extra_imports
        self.needs_gaas_cif = needs_gaas_cif
        self.needs_si_cif = needs_si_cif
        self.needs_fcc_kpath = needs_fcc_kpath


RECIPES = [
    # `1-Task_to_flow.ipynb` is built directly from the hand-written
    # run_si_gstate.py / run_si_nscf.py / run_si_ebands.py (Task -> Flow
    # progression for Si) -- those are NOT generated from workshop_lib.py,
    # so there is no recipe for them here.
    Recipe(
        fname="make_gaas_convecut.py",
        docstring="""\
Companion to `2.1-Convergence_study.ipynb` (ecut convergence).

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
        fname="make_gaas_convkpt.py",
        docstring="""\
Companion to `2.1-Convergence_study.ipynb` (k-point convergence).

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
Companion to `2.3-BandStructure.ipynb`.

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
        fname="make_gaas_phonons.py",
        docstring="""\
Companion to `2.4-Phonons.ipynb`.

Builds the same flow as `workshop_lib.build_phonon_flow()`: a ground-state
task producing the WFK file, followed by the symmetry-irreducible DFPT
atomic-perturbation tasks needed to assemble the dynamical matrix (and Born
effective charges) on a coarse q-mesh. This flow was already run ahead of
time for the tutorial -- it has more tasks than the others, so it's the
best candidate for actually running yourself with `nohup` (see below)
rather than waiting on it in a foreground shell.

Usage
-----
    python make_gaas_phonons.py
    abirun.py flow_gaas_phonons scheduler   # repeat if interrupted
    abirun.py flow_gaas_phonons status       # check progress / list tasks

    nohup python make_gaas_phonons.py > log 2> err &   # ... run in the background
""",
        chunks=["build_phonon_flow", "setup_manager"],
        entry_fn="build_phonon_flow",
        needs_gaas_cif=True,
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
    if recipe.needs_fcc_kpath:
        header.append(f"FCC_KPATH = {wlib.FCC_KPATH!r}")

    chunks = [src(name) for name in recipe.chunks]

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

    parts = ["\n".join(header)] + chunks + [footer]
    return "\n\n\n".join(parts) + "\n"


def main():
    for recipe in RECIPES:
        out_path = EXAMPLES_DIR / recipe.fname
        out_path.write_text(render(recipe))
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
