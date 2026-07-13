#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.1 (ecut convergence) --
plotting.

Opens `flow_gaas_convecut/`, the output of `make_gaas_convecut.py`, and
fits/plots the ecut convergence with
`abipy.tools.plotting.ConvergenceAnalyzer` -- the same analysis shown
inline in the notebook, saved here to `Plots/gaas_convecut_convecut.png`.

Usage
-----
    python plot_gaas_convecut.py
"""
from pathlib import Path

from abipy.tools.plotting import ConvergenceAnalyzer

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
    # Get flow directory
    workdir = SCRIPT_DIR / 'flow_gaas_convecut'
    print(workdir)

    # Make file name for figure
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '')
    figname = str(prefix) + '_convecut.png'
    print(figname)

    # Extract results and save plot.
    fig = plot_ecut_conv(workdir, figname)

if __name__ == "__main__":
    main()
