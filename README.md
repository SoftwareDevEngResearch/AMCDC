# MCDC

A python-based neutron transport Monte Carlo code. The code runs in multigroup mode and has numerous output scores including: 
flux, current, higher order flux moments, and the Eddington tensor.

Input allows the user to adjust geometry, sources, and materials.

Output will be an hdf5 file with the selected tallies.

## Usage

MCDC can be easily installed on Windows, macOS, and Linux through pip.

On windows use:
	py -m pip install mcdc

macOS and Linux use:
	python -m pip install mcdc

After installation, users can run example problems through the command line or run using their own input files with

	mcdc --input input.py --output ouput.h5

## Examples

Multiple example problems are included to show the capability of the program. These can be found through 

	mcdc --examples

and run using

	mcdc --example_name

An example input file and output processing script is shown below
	
## Input
	materials:
	 M1:
	  file_name:
	  SigmaC: [[1.0]]
	  SigmaS: [[1.0]]
	  SigmaF:
	  nu_p:
	 M2:
	  file_name:
	  SigmaC: [[1.5]]
	  SigmaS: [[3.0]]
	  SigmaF:
	  nu_p:
	 M3:
	  file_name:
	  SigmaC: [[2.0]]
	  SigmaS: [[4.0]]
	  SigmaF: 
	  nu_p:
	surfaces:
	 S1:
	  x_position: 0.0
	  type: 'vacuum'
	 S2:
	  x_position: 2.0
	  type: 'transmission'
	 S3:
	  x_position: 4.0
	  type: 'transmission'
	 S4:
	  x_position: 6.0
	  type: 'vacuum'
	cells:
	 C1: 2
	 C2: 3
	 C3: 1
	sources:
	 Src_1:
	  x_position: [2.0,4.0]
	  probability: 1.0
	  direction:
	tallies:
	- 'flux'
	- 'current'
	- 'flux-face'
	- 'current-face'
	number_of_histories: 10000

## Output plotting
	with h5py.File('output.h5', 'r') as f:
		phi         = f['tally/flux/mean'][:]/dx
		phi_sd      = f['tally/flux/sdev'][:]/dx
		phi_face    = f['tally/flux-face/mean'][:]
		phi_face_sd = f['tally/flux-face/sdev'][:]
		J         = f['tally/current/mean'][:,0]/dx
		J_sd      = f['tally/current/sdev'][:,0]/dx
		J_face    = f['tally/current-face/mean'][:,0]
		J_face_sd = f['tally/current-face/sdev'][:,0]

	# Plot, flux tally
	plt.plot(x_mid,phi,'-b',label="MC")
	plt.fill_between(x_mid,phi-phi_sd,phi+phi_sd,alpha=0.2,color='b')
	plt.plot(x_mid,phi_ref,'--r',label="ref.")
	plt.xlabel(r'$x$, cm')
	plt.ylabel('Flux')
	plt.ylim([0.06,0.16])
	plt.grid()
	plt.legend()
	plt.title(r'$\bar{\phi}_i$')
	plt.show()

## License

MCDC is released under the BSD 2-Clause license. See LICENSE for more details.