# 1. From Task to Flow: Silicon band structure

## 1.1 Ground-state density as a single Task

    python run_si_gstate.py


## 1.2 Band structure calculation in a second, dependent Task

    python run_si_nscf.py
    python plot_ebands_1.py


## 1.3 Wrapping both Tasks in a Flow

### Build it, write it, run it

    python run_si_ebands.py
    python plot_ebands_2.py

### Build it now, Run it later

    rm -r flow_si_ebands/
    python make_si_ebands.py

    abirun.py flow_si_ebands/ scheduler

    python plot_ebands_2.py


