import sys
import argparse

parser = argparse.ArgumentParser(
    description='Command line interface for mcdc'
    )
group = parser.add_mutually_exclusive_group(required=True)

parser.add_argument('-i','--input', type=file_path, default=None,
                    help='Input file to run',
                    action='store'
                    )
parser.add_argument('-o', '--output', type=file_path, default=None,
                    help='Name of output file to return',
                    action='store'
                    )

group.add_argument('--examples',
                    help='List of example problems',
                    action='store_true'
                    )
group.add_argument('--uniform_source',
                    help='Uniform source example problem',
                    action='store_true'
                    )

args = parser.parse_args(sys.argv[1:])

if args.examples:
    print('Slabs: azurv1_pl, beam_source, eig_alpha, eig_k, moments, multi_source, uniform_source, uniform_source_move') 
    print('Infinite multigroup: SHEM-361_k, SHEM-361_td')
if args.uniform_source:
    sys.path.append('examples/slabs/uniform_source')
    import input
    import process