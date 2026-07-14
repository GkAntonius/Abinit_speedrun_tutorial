#!/usr/bin/env python
"""
Companion to `3-Relaxation.ipynb` -- plotting.

Calls `workshop_lib.plot_relax()` on `flow_aln_relax/`, the output of
`make_aln_relax.py`: opens the last task of the first Work (the relaxation
task), plots the relaxation trajectory (`HistFile.plot()`: lattice
parameters, angles, volume, pressure, forces and energy vs. step), and
saves the figure to `Plots/`.

Usage
-----
    python plot_aln_relax.py
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


def plot_relax(workdir, figname, show=True):
    """Plot max forces through relaxation steps."""
    flow = flowtk.Flow.from_file(workdir)
    task = flow[0][-1]  # Select the second task of the first work.
    hist_path = task.outdir.has_abiext('HIST')  # Retrieve output GSR file of this task.

    # Open history file
    hist = abilab.abiopen(str(hist_path))

    # Plot forces vs steps
    fig = hist.plot()

    # Save figure
    if figname:
        fig.savefig(str(figname), dpi=200)

    return fig


def main():
    workdir = SCRIPT_DIR / 'flow_aln_relax'
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    figname = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '.png')

    fig = plot_relax(workdir, figname, show=True)


if __name__ == "__main__":
    main()
