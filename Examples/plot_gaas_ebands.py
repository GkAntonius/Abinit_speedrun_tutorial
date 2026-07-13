#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.3 (band structure) --
plotting.

Calls `workshop_lib.plot_ebands()` on `flow_gaas_ebands/`, the output of
`make_gaas_ebands.py`: opens the second task of the first Work (the NSCF
run along the L-Gamma-X path), plots the band structure, and saves the
figure to `Plots/`.

Usage
-----
    python plot_gaas_ebands.py
"""
from pathlib import Path

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

    fig = ebands.plot(color='b', show=show)
    ax = fig.gca()
    ax.set_ylim(ylim)

    # Save figure file
    fig.savefig(str(figname), dpi=200)

    return fig


def main():
    workdir = SCRIPT_DIR / 'flow_gaas_ebands'
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '')
    figname = str(prefix) + '_ebands.png'

    fig = plot_ebands(workdir, figname, show=True)


if __name__ == "__main__":
    main()
