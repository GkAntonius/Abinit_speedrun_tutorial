from pathlib import Path
from abipy import abilab

import sys

ddb_path = 'flow_mgo_phonons/w1/outdata/out_DDB'
workdir = __file__.replace('run_', 'task_').replace('.py', '')

nqsmall = 10; ndivsm = 40; asr = 2; chneut = 1; dipdip = 1; dos_method = "tetra"; lo_to_splitting = "automatic"
                               
with abilab.abiopen(str(ddb_path)) as ddb:

        phbst_file, phdos_file = ddb.anaget_phbst_and_phdos_files(
            nqsmall=10,
            ndivsm=40,
            asr=2,
            chneut=1,
            dipdip=1,
            dos_method='tetra',
            lo_to_splitting='automatic',
            workdir=str(workdir),
            verbose=True,
            mpi_procs=1)
