#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.1 (ecut convergence) --
plotting.

Calls `workshop_lib.plot_ecut_conv()` on `flow_gaas_convecut/`, the output
of `make_gaas_convecut.py`: fits/plots the ecut convergence with
`abipy.tools.plotting.ConvergenceAnalyzer` -- the same analysis shown
inline in the notebook -- and saves the figure to `Plots/`.

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


def plot_ecut_conv(workdir, figname="ecut_conv.png"):

    # Build the list of GSR.nc files
    gsr_files = []
    flow = flowtk.Flow.from_file(str(workdir))
    for work in flow:
        task = work[0]  # Select first task in work
        gsr_path = task.outdir.has_abiext('GSR')
        gsr_files.append(str(gsr_path))
    
    # Extract data
    ecut_Ha = []
    energy_per_atom_eV = []

    for gsr_file in gsr_files:

        gsr = abilab.abiopen(gsr_file)
        ecut_Ha.append(gsr.ecut)
        energy_per_atom_eV.append(gsr.energy_per_atom)

    # Plot results
    ca = ConvergenceAnalyzer.from_xy_label_vals("ecut (Ha)", ecut_Ha,
                                                "E/natom (eV)", energy_per_atom_eV, tols=1e-3)

    fig = ca.plot(savefig=str(figname), show=True, dpi=200)

    return fig


def main():
    workdir = SCRIPT_DIR / 'flow_gaas_convecut'

    # Make file name for figure
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '')
    figname = str(prefix) + '_convecut.png'

    plot_ecut_conv(workdir=str(workdir), figname=figname)

if __name__ == "__main__":
    main()
