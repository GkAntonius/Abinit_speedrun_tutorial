#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.1 (k-point convergence) --
plotting.

Calls `workshop_lib.plot_kpt_conv()` on `flow_gaas_convkpt/`, the output
of `make_gaas_convkpt.py`: converts each k-mesh into an "inverse k-point
distance" (a rough, mesh-independent measure of density) and fits/plots
the convergence with `abipy.tools.plotting.ConvergenceAnalyzer` -- the
same analysis shown inline in the notebook -- saving the figure to
`Plots/`.

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


def plot_kpt_conv(workdir, figname="kpt_conv.png"):

    # Convert each k-mesh into an "inverse k-point distance" (a rough,
    # mesh-independent measure of density) so runs with different
    # kptrlatt can be compared on the same x-axis.
    k_recip_dist, ene_per_atom_eV = [], []

    with abilab.GsrRobot.from_dir(str(workdir)) as robot:
        for label, gsr in robot:
            ene_per_atom_eV.append(gsr.energy_per_atom)
            rprim = gsr.structure.lattice.matrix
            kptrlatt = gsr.kpoints.ksampling["kptrlatt"]
            R_latt = np.dot(kptrlatt, rprim)
            k_latt = 2 * np.pi * np.linalg.inv(R_latt)
            kmin = max(np.linalg.norm(k) for k in k_latt)
            k_recip_dist.append(1 / kmin)

    ca = ConvergenceAnalyzer.from_xy_label_vals(
        "Inverse k-point distance (Ang)", k_recip_dist,
        "E/natom (eV)", ene_per_atom_eV, tols=1e-3)

    fig = ca.plot(savefig=str(figname), show=True, dpi=200)

    return fig


def main():
    workdir = SCRIPT_DIR / 'flow_gaas_convkpt'

    # Make file name for figure
    plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '')
    figname = str(prefix) + '_convkpt.png'

    plot_kpt_conv(workdir=str(workdir), figname=figname)

if __name__ == "__main__":
    main()
