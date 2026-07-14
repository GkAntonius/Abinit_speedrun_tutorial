#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.1 (k-point convergence) --
plotting.

Calls `workshop_lib.plot_kpt_conv()` on `flow_gaas_convkpt/`, the output
of `make_gaas_convkpt.py`: converts each k-mesh into an "inverse k-point
distance" (a rough, mesh-independent measure of density) and fits/plots
the convergence with `abipy.tools.plotting.ConvergenceAnalyzer` -- the
same analysis shown inline in the notebook -- saving the figure to
`Plots/`. `get_gsr_files()` (shared with `plot_gaas_convecut.py`) collects
the `GSR.nc` path of the last task of each Work in the flow.

Usage
-----
    python plot_gaas_convkpt.py
"""
from pathlib import Path

import numpy as np

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


def plot_kpt_conv(workdir, figname, show=True):
    """
    Extract energy and k-point grids, and plot against inverse k-points distance.
    """
    k_dist_inv, E_at_eV = [], []

    for gsr_file in get_gsr_files(workdir):

            gsr = abilab.abiopen(gsr_file)

            E_at_eV.append(gsr.energy_per_atom)

            # Compute inverse k-points distance
            rprim = gsr.structure.lattice.matrix
            kptrlatt = gsr.kpoints.ksampling["kptrlatt"]
            R_latt = np.dot(kptrlatt, rprim)
            k_latt = 2 * np.pi * np.linalg.inv(R_latt)
            kmin = max(np.linalg.norm(k) for k in k_latt)
            k_dist_inv.append(1 / kmin)

    ca = ConvergenceAnalyzer.from_xy_label_vals(
        "Inverse k-point distance (Ang)", k_dist_inv,
        "E/natom (eV)", E_at_eV, tols=1e-3)

    fig = ca.plot(show=show)

    if figname:
        fig.savefig(str(figname), dpi=200)

    return fig


def main():
    workdir = SCRIPT_DIR / 'flow_gaas_convkpt'

    # Make file name for figure
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    figname = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '.png')

    plot_kpt_conv(workdir=str(workdir), figname=figname)

if __name__ == "__main__":
    main()
