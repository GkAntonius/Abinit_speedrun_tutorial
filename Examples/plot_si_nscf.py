#!/usr/bin/env python
"""
Companion to `1-Task_to_flow.ipynb`, step 2 (plotting).

Plots the band structure from `task_si_nscf/`, the output of the two
manually-chained tasks in `run_si_gstate.py` + `run_si_nscf.py`. Compare
with `plot_si_ebands.py`, which plots the same physics from the `Flow`
version (`run_si_ebands.py`) instead.

Usage
-----
    python plot_si_nscf.py
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
    main()
