#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.1 (ecut convergence) --
plotting.

Calls `workshop_lib.plot_ecut_conv()` on `flow_gaas_convecut/`, the output
of `make_gaas_convecut.py`: fits/plots the ecut convergence with
`abipy.tools.plotting.ConvergenceAnalyzer` -- the same analysis shown
inline in the notebook -- and saves the figure to `Plots/`. `get_gsr_files()`
(shared with `plot_gaas_convkpt.py`) collects the `GSR.nc` path of the
last task of each Work in the flow.

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


def get_gsr_files(workdir):
    """Build the list of GSR.nc files from the last task of each work"""
    gsr_files = []
    flow = flowtk.Flow.from_file(str(workdir))
    for work in flow:
        task = work[-1]  # Select last task in work
        gsr_path = task.outdir.has_abiext('GSR')
        gsr_files.append(str(gsr_path))
    return gsr_files


def plot_ecut_conv(workdir, figname, show=True):
    """
    Extract energy per atom from a convergence flow and plot against 'ecut'.
    """
    gsr_files = get_gsr_files(workdir)

    ecut_Ha, E_at_eV = [], []
    for gsr_file in gsr_files:

        gsr = abilab.abiopen(gsr_file)
        ecut_Ha.append(gsr.ecut)
        E_at_eV.append(gsr.energy_per_atom)

    # Plot results
    ca = ConvergenceAnalyzer.from_xy_label_vals("ecut (Ha)", ecut_Ha,
                                                "E/natom (eV)", E_at_eV,
                                                tols=1e-3)

    fig = ca.plot(show=show)
    if figname:
        fig.savefig(str(figname), dpi=200)

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
