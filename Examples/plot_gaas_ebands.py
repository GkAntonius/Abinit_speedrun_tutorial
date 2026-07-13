#!/usr/bin/env python
"""
Companion to `1-Task_to_flow.ipynb`, step 3 (plotting).

Plots the band structure from `flow_si_ebands/`, the output of the `Flow`
version of the same calculation (`run_si_ebands.py`). Compare with
`plot_si_bands_1.py`, which plots the same physics from the two
manually-chained tasks instead.

Usage
-----
    python plot_si_bands_2.py
"""
from pathlib import Path

import numpy as np

import matplotlib.pyplot as plt

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


def plot_ebands(workdir, figname, ylim=(-2,2), show=True):
    flow = flowtk.Flow.from_file(workdir)     # Open flow object.
    task = flow[0][1]                         # Select the second task of the first work.
    gsr_path = task.outdir.has_abiext('GSR')  # Retrieve output GSR file of this task.

    # Extract results
    gsr = abilab.abiopen(str(gsr_path))
    ebands = gsr.ebands

    fig = ebands.plot(color='b', show=False)
    ax = fig.gca()
    ax.set_ylim(ylim)

    # Save figure file
    fig.savefig(str(figname), dpi=200)

    # Display the figure
    if show:
        plt.show()

    return fig


def main():
    workdir = SCRIPT_DIR / 'flow_gaas_ebands' 
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '')
    figname = str(prefix) + '_ebands.png'

    fig = plot_ebands(workdir, figname, show=True)


if __name__ == "__main__":
    main()
