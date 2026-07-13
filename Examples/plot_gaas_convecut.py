from pathlib import Path

import abipy.abilab
import abipy.flowtk
from abipy.tools.plotting import ConvergenceAnalyzer

# Get flow directory
workdir = Path(__file__).parent / 'flow_gaas_convecut'
print(workdir)

# Make file name for figure
plotdir = Path('Plots'); plotdir.mkdir(exist_ok=True)
prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py','')
figname = str(prefix) + '_convecut.png'
print(figname)

# Extract results
ecut_Ha = []
energy_per_atom_eV = []

flow = abipy.flowtk.Flow.from_file(str(workdir))

for work in flow:
    # Select task in work
    task = work[0]

    gsr_path = task.outdir.has_abiext('GSR')
    print(gsr_path)

    gsr = abipy.abilab.abiopen(gsr_path)
    ecut_Ha.append(gsr.ecut)
    energy_per_atom_eV.append(gsr.energy_per_atom)

# Plot results
ca = ConvergenceAnalyzer.from_xy_label_vals("ecut (Ha)", ecut_Ha,
                                            "E/natom (eV)", energy_per_atom_eV, tols=1e-3)

fig = ca.plot(savefig=str(figname), show=True, dpi=200)
