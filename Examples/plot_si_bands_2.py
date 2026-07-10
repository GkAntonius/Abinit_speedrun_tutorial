#!/usr/bin/env python
"""
Companion to Section XXXXXX of the
workshop notebook.

Build an abinit calculation and run it.

Usage
-----
    python run_si_nscf.py
"""
from pathlib import Path

import abipy.abilab as abilab
import abipy.flowtk as flowtk
from abipy.abilab import Structure

import numpy as np
import matplotlib.pyplot as plt

# This script is meant to be copied -- together with the rest of this
# Tutorial/ directory -- into your own work directory. Data/Pseudos and
# Data/Structures are located relative to *this file*.
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Data"
PSEUDO_DIR = DATA_DIR / "Pseudos"
STRUCTURE_DIR = DATA_DIR / "Structures"

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
    main()
