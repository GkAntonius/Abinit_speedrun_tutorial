from pathlib import Path
from abipy import abilab

workdir = Path(__file__).parent / 'task_mgo_anaddb'
out_anaddb_path = workdir / 'outdata' / 'out_anaddb.nc'
phbst_path = workdir / 'outdata' / 'out_PHBST.nc'

plotdir = Path('Plots') ; plotdir.mkdir(exist_ok=True)
prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '.png')

with abilab.abiopen(str(phbst_path)) as phbst_file:

        phbands = phbst_file.phbands
        #phbands.read_non_anal_from_file(str(out_anaddb_path))

        units = "mev"                                                           
        kwargs = dict(dpi=300)
        #fig = phbands.qpoints.plot(show=False) ; fig.savefig(plot_dir / 'BZ.png', **kwargs)
        #fig = phbands.plot_with_phdos(phdos, units=units, show=False) ; fig.savefig(plot_dir / 'phbs_dos.png', **kwargs)
        #fig = phdos_file.plot_pjdos_type(units=units, show=False) ; fig.savefig(plot_dir / 'phbs_pjdos.png', **kwargs)
        #fig = phbands.plot_colored_matched(units=units, show=True) ; fig.savefig(plot_dir / 'phbs_colored.png', **kwargs)
        #fig = phdos.plot_harmonic_thermo(tstart=5, tstop=300, num=50, units="eV", formula_units=1, quantities="all", show=False) ; fig.savefig(plot_dir / 'phonon_harmonic_thermo.png', **kwargs)
        #fig = phdos.plot(units=units, show=False) ; fig.savefig(plot_dir / 'phdos.png', **kwargs)
        #fig = phbands.plot_fatbands(units=units, phdos_file=phdos_file, show=False) ; fig.savefig(plot_dir / 'phbs_fatbands.png', **kwargs)
        fig = phbands.plot(units=units, color='b', show=False)
        ax = fig.gca()
        ax.set_ylim(0, 80)
        fig.savefig(str(prefix) + '_bands.png' , **kwargs)
