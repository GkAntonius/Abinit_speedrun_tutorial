#!/usr/bin/env python
"""
Generate the standalone `run_*.py` example scripts in this directory from
`../Notebooks/workshop_lib.py`.

Why generate rather than hand-write: each `run_*.py` is meant to be copied
by a student into their own work directory and run on its own, so it must
NOT `import workshop_lib`. But the notebook's analysis cells assume the
flows were built with *exactly* the same `AbinitInput`/`Flow` code as
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
    Recipe(
        fname="run_gaas_gstate.py",
        docstring="""\
Companion to Section 3 ("Ground-state total energy of GaAs") of the
workshop notebook.

Builds the same flow as `workshop_lib.build_gs_flow()` and writes it to
disk, so it can be launched and monitored from a terminal on the cluster
instead of blocking the notebook kernel with `flow.make_scheduler().start()`.

Usage
-----
    python run_gaas_gstate.py
    abirun.py flow_gaas_gstate scheduler   # ... then run it (repeat if interrupted)
    abirun.py flow_gaas_gstate status      # ... or just check progress
""",
        chunks=["gs_input", "build_gs_flow", "setup_manager"],
        entry_fn="build_gs_flow",
        needs_gaas_cif=True,
    ),
    Recipe(
        fname="run_gaas_convecut.py",
        docstring="""\
Companion to Section 4.1 ("ecut convergence") of the workshop notebook.

Builds the same flow as `workshop_lib.build_ecut_conv_flow()`: one SCF task
per value of `ecut`. After it completes, the notebook's `GsrRobot` /
`ConvergenceAnalyzer` cells collect the results into a convergence plot.

Usage
-----
    python run_gaas_convecut.py
    abirun.py flow_gaas_convecut scheduler
    abirun.py flow_gaas_convecut status
""",
        chunks=["gs_input", "build_ecut_conv_flow", "setup_manager"],
        entry_fn="build_ecut_conv_flow",
        needs_gaas_cif=True,
    ),
    Recipe(
        fname="run_gaas_convkpt.py",
        docstring="""\
Companion to Section 4.2 ("k-point convergence") of the workshop notebook.

Builds the same flow as `workshop_lib.build_kpt_conv_flow()`: one SCF task
per automatically-generated k-mesh density. After it completes, the
notebook's `GsrRobot` cell collects the results and plots energy per atom
against k-point density.

Usage
-----
    python run_gaas_convkpt.py
    abirun.py flow_gaas_convkpt scheduler
    abirun.py flow_gaas_convkpt status
""",
        chunks=["gs_input", "build_kpt_conv_flow", "setup_manager"],
        entry_fn="build_kpt_conv_flow",
        needs_gaas_cif=True,
    ),
    Recipe(
        fname="run_gaas_ebands.py",
        docstring="""\
Companion to Section 5 ("Band structures: GaAs vs Si") of the workshop
notebook, GaAs half.

Builds the same flow as `workshop_lib.build_gaas_ebands_flow()`: a
ground-state run on a homogeneous k-mesh followed by a non-self-consistent
run along the L-Gamma-X path. See also `run_si_ebands.py` for the silicon
comparison.

Usage
-----
    python run_gaas_ebands.py
    abirun.py flow_gaas_ebands scheduler
    abirun.py flow_gaas_ebands status
""",
        chunks=["_bandstructure_inputs", "build_gaas_ebands_flow", "setup_manager"],
        entry_fn="build_gaas_ebands_flow",
        needs_gaas_cif=True,
        needs_fcc_kpath=True,
    ),
    Recipe(
        fname="run_si_ebands.py",
        docstring="""\
Companion to Section 5 ("Band structures: GaAs vs Si") of the workshop
notebook, Si half.

Builds the same flow as `workshop_lib.build_si_ebands_flow()`: a
ground-state run on a homogeneous k-mesh followed by a non-self-consistent
run along the L-Gamma-X path, this time for silicon. See also
`run_gaas_ebands.py` for the GaAs run this is compared against -- GaAs has a
direct gap at Gamma, while silicon's fundamental gap is indirect.

Usage
-----
    python run_si_ebands.py
    abirun.py flow_si_ebands scheduler
    abirun.py flow_si_ebands status
""",
        chunks=["_bandstructure_inputs", "build_si_ebands_flow", "setup_manager"],
        entry_fn="build_si_ebands_flow",
        needs_si_cif=True,
        needs_fcc_kpath=True,
    ),
    Recipe(
        fname="run_gaas_eos.py",
        docstring="""\
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
    python run_gaas_eos.py
    abirun.py flow_gaas_eos scheduler
    abirun.py flow_gaas_eos status
""",
        chunks=["build_eos_flow", "setup_manager"],
        entry_fn="build_eos_flow",
        extra_imports="import numpy as np",
        needs_gaas_cif=True,
    ),
    Recipe(
        fname="run_gaas_phonons.py",
        docstring="""\
Companion to Section 7 ("Phonons from DFPT") of the workshop notebook.

Builds the same flow as `workshop_lib.build_phonon_flow()`: a ground-state
task producing the WFK file, followed by the symmetry-irreducible DFPT
atomic-perturbation tasks needed to assemble the dynamical matrix (and Born
effective charges) on a coarse q-mesh. This has more tasks than the other
example flows, so it is the best candidate for running in the background
with `nohup` (see below) rather than waiting on it in a foreground shell.

Usage
-----
    python run_gaas_phonons.py
    abirun.py flow_gaas_phonons scheduler   # repeat if interrupted
    abirun.py flow_gaas_phonons status       # check progress / list tasks

    nohup python run_gaas_phonons.py > log 2> err &   # ... run in the background
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
    # Set working directory (default is constructed from the script name)
    if not workdir:
        workdir = Path(__file__).name.replace(".py", "").replace("run_", "flow_")

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
