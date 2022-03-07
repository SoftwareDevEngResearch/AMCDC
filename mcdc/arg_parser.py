import sys
import argparse

parser = argparse.ArgumentParser(
    description='Command line interface for mcdc'
    )
group = parser.add_mutually_exclusive_group()

parser.add_argument('-i','--input',
                    help='Input file to run',
                    action='store'
                    )
parser.add_argument('-o', '--output',
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
group.add_argument('--multi_source',
                    help='Multi source example problem',
                    action='store_true'
                    )
group.add_argument('--azurv1_pl',
                    help='Azurv1 example problem',
                    action='store_true'
                    )
group.add_argument('--beam_source',
                    help='Beam source example problem',
                    action='store_true'
                    )
group.add_argument('--eig_alpha',
                    help='Alpha eigenvalue example problem',
                    action='store_true'
                    )
group.add_argument('--eig_k',
                    help='K eigenvalue example problem',
                    action='store_true'
                    )
group.add_argument('--moments',
                    help='Functional expansion moments example problem',
                    action='store_true'
                    )
group.add_argument('--uniform_source_move',
                    help='Moving uniform source example problem',
                    action='store_true'
                    )
group.add_argument('--SHEM_k',
                    help='Infinite multigroup k example problem',
                    action='store_true'
                    )
group.add_argument('--SHEM_td',
                    help='Infinite multigroup td example problem',
                    action='store_true'
                    )

args = parser.parse_args(sys.argv[1:])

if args.examples:
    print('Slabs: azurv1_pl, beam_source, eig_alpha, eig_k, moments, multi_source, uniform_source, uniform_source_move') 
    print('Infinite multigroup: SHEM_k, SHEM_td')
if args.uniform_source:
    sys.path.append('examples/slabs/uniform_source')
    import input
    import process
if args.multi_source:
    sys.path.append('examples/slabs/multi_source')
    import input
    import process
if args.azurv1_pl:
    sys.path.append('examples/slabs/azurv1_pl')
    import input
    import process
if args.beam_source:
    sys.path.append('examples/slabs/beam_source')
    import input
    import process
if args.eig_alpha:
    sys.path.append('examples/slabs/eig_alpha')
    import input
    import process
if args.eig_k:
    sys.path.append('examples/slabs/eig_k')
    import input
    import process
if args.moments:
    sys.path.append('examples/slabs/moments')
    import input
    import process
if args.uniform_source_move:
    sys.path.append('examples/slabs/uniform_source_move')
    import input
    import process
if args.SHEM_k:
    sys.path.append('examples/infinite_multigroup/SHEM-361_k')
    import input
    import process
if args.SHEM_td:
    sys.path.append('examples/infinite_multigroup/SHEM-361_td')
    import input
    import process