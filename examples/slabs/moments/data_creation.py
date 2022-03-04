import numpy as np
import numpy.random as random

t = np.linspace(0, 1, 10)

# random cross sections, add up to total cross section
SigmaCi = random.random()
SigmaSi = random.random()
SigmaFi = random.random()
total = SigmaCi + SigmaSi + SigmaFi
    
SigmaC = np.array([SigmaCi/total])
SigmaS = np.array([[SigmaSi/total]])
SigmaF = np.array([[SigmaFi/total]])
nu = np.array([2 + random.random()])


# create sources
N_sources = random.randint(3,7)
Sources = np.zeros((3, N_sources))

# for i in range(M):
for j in range(N_sources):
    # random length
    length = .1 + 2 * random.random()
    Sources[0,j] = (6-length) * random.random()
    Sources[1,j] = Sources[0,j] + length
    # random probability
    Sources[2,j] = random.random()
    
# make probability a proportion    
Sources[2,:] = Sources[2,:] / np.sum(Sources[2,:])

np.savez('examples/slabs/moments/initial_data.npz', SigmaC=SigmaC, SigmaS=SigmaS, SigmaF=SigmaF, nu=nu, t=t, N_sources=N_sources, Sources=Sources)