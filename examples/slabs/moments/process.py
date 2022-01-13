import numpy as np
import matplotlib.pyplot as plt
import h5py
from scipy.integrate import quad


# =============================================================================
# Reference solution
# =============================================================================

# Load grids
with h5py.File('output.h5', 'r') as f:
    x = f['tally/spatial_grid'][:]
dx    = (x[1]-x[0])
x_mid = 0.5*(x[:-1]+x[1:])

# =============================================================================
# Plot results
# =============================================================================

# Results
with h5py.File('output.h5', 'r') as f:
    phi         = f['tally/flux/mean'][:]/dx
    phi_sd      = f['tally/flux/sdev'][:]/dx
    phi_face    = f['tally/flux-face/mean'][:]
    phi_face_sd = f['tally/flux-face/sdev'][:]
    J         = f['tally/current/mean'][:,0]/dx
    J_sd      = f['tally/current/sdev'][:,0]/dx
    J_face    = f['tally/current-face/mean'][:,0]
    J_face_sd = f['tally/current-face/sdev'][:,0]

# Plot
plt.plot(x_mid,phi,'-b',label="MC")
plt.fill_between(x_mid,phi-phi_sd,phi+phi_sd,alpha=0.2,color='b')
plt.xlabel(r'$x$, cm')
plt.ylabel('Flux')
plt.grid()
plt.legend()
plt.title(r'$\bar{\phi}_i$')
plt.show()

plt.plot(x[:],phi_face,'-b',label="MC")
plt.fill_between(x[:],phi_face-phi_face_sd,phi_face+phi_face_sd,alpha=0.2,color='b')
plt.xlabel(r'$x$, cm')
plt.ylabel('Flux')
plt.grid()
plt.legend()
plt.title(r'$\phi(x)$')
plt.show()

# Solution
plt.plot(x_mid,J,'-b',label="MC")
plt.fill_between(x_mid,J-J_sd,J+J_sd,alpha=0.2,color='b')
plt.xlabel(r'$x$, cm')
plt.ylabel('Current')
plt.grid()
plt.legend()
plt.title(r'$\bar{J}_i$')
plt.show()

plt.plot(x[:],J_face,'-b',label="MC")
plt.fill_between(x[:],J_face-J_face_sd,J_face+J_face_sd,alpha=0.2,color='b')
plt.xlabel(r'$x$, cm')
plt.ylabel('Current')
plt.grid()
plt.legend()
plt.title(r'$J(x)$')
plt.show()
