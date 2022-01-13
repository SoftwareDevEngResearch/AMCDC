import numpy as np
import sys

# Get path to mcdc (not necessary if mcdc is installed)
sys.path.append('C:/Users/larse/Source/Repos/MCDC')

import mcdc

# =============================================================================
# Load initial data
# =============================================================================

data = np.load('C:/Users/larse/Source/Repos/MCDC/initial_data.npz')

# =============================================================================
# Set material
# =============================================================================

SigmaC = data['SigmaC']
SigmaS = data['SigmaS']
#SigmaF = data['SigmaF']
#nu     = data['nu']
SigmaF = np.array([[0.0]])
nu     = np.array([0])
M = mcdc.Material(SigmaC, SigmaS, SigmaF, nu)

# =============================================================================
# Set cells
# =============================================================================

# Set surfaces
# Set surfaces
S0 = mcdc.SurfacePlaneX(0.0, "vacuum")
S1 = mcdc.SurfacePlaneX(6.0, "vacuum")

# Set cells
C = mcdc.Cell([+S0, -S1], M)
cells = [C]

# =============================================================================
# Set sources
# =============================================================================

N_sources = data['N_sources']
input_src = data['Sources']
sources = []

# Direction distribution
dir = mcdc.DistPointIsotropic()

# Energy group distribution
g = mcdc.DistDelta(0)

# Time distribution
time = mcdc.DistDelta(0.0)

# Create the sources
for i in range(N_sources):
    posi = mcdc.DistPoint(mcdc.DistUniform(input_src[0,i],input_src[1,i]), mcdc.DistDelta(0.0), 
                             mcdc.DistDelta(0.0))
    Srci = mcdc.SourceSimple(posi,dir,g,time,prob=input_src[2,i])
    sources.append(Srci)

# =============================================================================
# Set filters and tallies
# =============================================================================

spatial_filter = mcdc.FilterPlaneX(np.linspace(0.0, 6.0, 61))

T = mcdc.Tally('tally', scores=['flux', 'flux-face', 'current', 'current-face'], 
               spatial_filter=spatial_filter)

tallies = [T]

# =============================================================================
# Set and run simulator
# =============================================================================

# Set speed
speeds = np.array([1.0])

# Set simulator
simulator = mcdc.Simulator(speeds, cells, sources, tallies=tallies, 
                           N_hist=10000)

# Set population control and census
simulator.set_pct(census_time=np.array([20.0]))

# Run
simulator.run()
