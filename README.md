# MCDC

A python-based neutron transport Monte Carlo code. The code runs in multigroup mode and has numerous output scores including: 
flux, current, higher order flux moments, and the Eddington tensor.

Input allows the user to adjust geometry, sources, and materials.

Output will be an hdf5 file with the selected tallies.

## Usage

MCDC can be easily installed on Windows, macOS, and Linux through pip with the following

	py -m pip install mcdc

After installation, users can run their own input files through the command line with

	py -m mcdc --input input.yaml --output ouput.h5

## Examples

Multiple example problems are included. These can be found with the command:

	py -m mcdc --examples

and run using

	py -m mcdc --example_name
	
## Input
An example input.yaml file is shown below

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

Input files must consist of the six main categories including: materials, surfaces, cells, sources, tallies, and number of histories.
Without all six of these inputs the software will fail to run.

### Materials
The materials class allows the user to manually input material cross sections by hand or through an input file. If the cross sections
are provided in the input file they must be input as an array seen in the example. A prompt fission multiplication factor must also be provided
if the user has input a fission cross section.

In the case of an input file the user would simply paste the path of their .npz file. For example:
	file_name: 'C:/Users/username/desktop/U235.npz'
The .npz file should consist of the same arrays as above but also enables the user to provide a decayed fission multiplication factor ('nu_d')
and additional matrices such as 'chi_p' and 'chi_d' if needed.

### Surfaces
Surfaces require only two inputs. The x position and the type of boundary. Boundary types currently only include 'vacuum' and 'transmission'.

### Cells
In order to simplify the input file the cells only require a material input. The cells are built in the order of the surfaces and assigned a material
number. In the case of the example above, C1 (cell 1) is built between S1 (surface 1) and S2, C2 between S2 and S3, and finally C3 between S3 and S4.
Then simply assigned a material number according to the order the materials were provided in. So C1 is filled with material 2, C2 with material 3, and
finally C3 with material 1. The material numbers are independent of the naming in the material class. So if M1 was actually name '235-U' it would still
be input as simply '1'.

### Sources
Each source takes in a required three inputs. X_position is provided as a vector with either a single point position ('[1.0]') or as
an area filled with the source as seen in the example. Probabilities should be provided for each source as a float. Finally the 
x direction can either be left blank to denote an isotropic source or a value can be provided between 1.0 and 0.0.

### Tallies
In the tallies category the user can select what exactly they want MC/DC to tally and output. The list of tallies includes:


Cell edge tallies: 'flux', 'current'

Cell face tallies: 'flux-face', 'current-face' 

Functional moment expansion: 'fet'

Eddington tensor: 'eddington'

### Number of histories
Input the number of histories to run for.

## Output plotting
And example plotting script for the example input file is shown below. The output.h5 file saves the average as well as the standard 
deviation of each selected tally.

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
	plt.xlabel(r'$x$, cm')
	plt.ylabel('Flux')
	plt.grid()
	plt.legend()
	plt.title(r'$\bar{\phi}_i$')
	plt.show()

## License

MCDC is released under the BSD 2-Clause license. See LICENSE for more details.