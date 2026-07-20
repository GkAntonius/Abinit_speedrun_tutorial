# ----------------------------------------------------------------------------
# Environment setup for Abinit speedrun tutorial on cemdi cluster reservation.
# ----------------------------------------------------------------------------

# Setup default openmpi 
export OMP_NUM_THREADS=1

# Use shared modules directory
module use /project/def-sponsor00/shared/modules

# Load abinit and python environment for abipy
module load abinit/10.8.2
module load python/3.12.4
module load abipy/1.0.0

