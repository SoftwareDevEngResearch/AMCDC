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

Example input and processing files can be viewed with

	mcdc --example_name_input
	mcdc --example_name_process

## License

MCDC is released under the BSD 2-Clause license. See LICENSE for more details.