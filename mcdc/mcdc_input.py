import sys
import argparse

import numpy as np
import sys
import yaml

# Get path to mcdc (not necessary if mcdc is installed)
sys.path.append('../')

import mcdc

def input_parser(inputs,output):
    # ============================================================================  
    # Set materials
    # =============================================================================
    M = []
    for i in range(len(inputs['materials'])):
        material = inputs['materials'][list(inputs['materials'])[i]]
        if material['file_name'] != None: # check if there is a cross section input file
            with np.load(material['file_name']) as data:
                SigmaC = data['SigmaC']
                SigmaS = data['SigmaS']
                SigmaF = data['SigmaF']
                nu_p   = data['nu_p']
                nu_d   = data['nu_d']
                chi_p  = data['chi_p']
                chi_d  = data['chi_d']
                G      = data['G']
                # Build mcdc material
                M.append(mcdc.Material(capture=SigmaC, scatter=SigmaS, fission=SigmaF, nu_p=nu_p,
                              chi_p=chi_p, nu_d=nu_d, chi_d=chi_d))
                continue
        # Get XS
        SigmaF = np.array(material['SigmaF'])
        SigmaC = np.array(material['SigmaC'])
        SigmaS = np.array(material['SigmaS'])

        # Build material with XS
        if SigmaC != None:
            mat = mcdc.Material(capture=SigmaC)
        elif SigmaC == None:
            print('No cross section for SigmaC')
            sys.exit()
        if SigmaS != None:
            mat = mcdc.Material(capture=SigmaC, scatter=SigmaS)
        if SigmaF != None:
            nu_p = np.array(material['nu_p'])
            mat = mcdc.Material(capture=SigmaC, scatter=SigmaS, fission=SigmaF, nu_p=nu_p)

        M.append(mat)

    # =============================================================================
    # Set cells
    # =============================================================================
    # Initialize x bounds
    x1 = 10**100
    x2 = -10**100
    # Set surfaces
    S = []
    for i in range(len(inputs['surfaces'])):
        surface = inputs['surfaces'][list(inputs['surfaces'])[i]]
        S.append(mcdc.SurfacePlaneX(surface['x_position'], surface['type']))

        # Get x bounds
        if surface['x_position'] > x2:
            x2 = surface['x_position']
        if surface['x_position'] < x1:
            x1 = surface['x_position']

    # Set cells
    cells = []
    for i in range(len(inputs['cells'])):
        cell = inputs['cells'][list(inputs['cells'])[i]]
        cells.append(mcdc.Cell([+S[i], -S[i+1]], M[cell-1]))

    # =============================================================================
    # Set source
    # =============================================================================

    sources = []
    for i in range(len(inputs['sources'])):
        source = inputs['sources'][list(inputs['sources'])[i]]

        # Position distribution, only x currently
        if len(source['x_position']) == 1:
            pos = mcdc.DistPoint(mcdc.DistDelta(source['x_position'][0]), mcdc.DistDelta(0.0), 
                                        mcdc.DistDelta(0.0))
        elif len(source['x_position']) == 2:
            pos = mcdc.DistPoint(mcdc.DistUniform(source['x_position'][0],source['x_position'][1]), mcdc.DistDelta(0.0), 
                                        mcdc.DistDelta(0.0))
        else:
            print('Please provide valid source position')
            sys.exit()

        # Direction distribution between 0.0 and 1.0, only x currently
        
        if source['direction'] == None:
            dir = mcdc.DistPointIsotropic()
        elif 0.0 <= source['direction'] <= 1.0:
            dir = mcdc.DistPoint(mcdc.DistDelta(source['direction']), mcdc.DistDelta(0.0), 
                                    mcdc.DistDelta(0.0))
        else:
            print('Please provide valid source direction')
            sys.exit()

        # Energy group distribution
        g = mcdc.DistDelta(0)

        # Time distribution
        time = mcdc.DistDelta(0.0)

        # Probability
        if isinstance(source['probability'], float) or isinstance(source['probability'], int):
            prob = source['probability']
        else:
            print('Please provide valid source probability')
            sys.exit()

        # Create the source
        Src = mcdc.SourceSimple(pos,dir,g,time,prob)
        sources.append(Src)

    # =============================================================================
    # Set filters and tallies
    # =============================================================================

    # Set spatial filter using x1 and x2 found from surfaces
    space = int((x2 - x1) * 10 + 1)
    spatial_filter = mcdc.FilterPlaneX(np.linspace(x1, x2, space))

    # Set tallies
    T = mcdc.Tally('tally', scores=inputs['tallies'], 
                   spatial_filter=spatial_filter)

    tallies = [T]

    # =============================================================================
    # Set and run simulator
    # =============================================================================
    N_hist = inputs['number_of_histories']

    # Set simulator
    simulator = mcdc.Simulator(cells=cells, sources=sources, tallies=tallies, 
                               N_hist=N_hist, output=output)

    # Run
    simulator.run()


def mcdc_input(argv):
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

    args = parser.parse_args(sys.argv[1:])

    if args.examples:
        print('beam_source, eig_alpha, eig_k, multi_source, uniform_source,') 
    if args.uniform_source:
        from mcdc.examples.slabs.uniform_source import input
        from mcdc.examples.slabs.uniform_source import process
    if args.multi_source:
        from mcdc.examples.slabs.multi_source import input
        from mcdc.examples.slabs.multi_source import process
    if args.beam_source:
        from mcdc.examples.slabs.beam_source import input
        from mcdc.examples.slabs.beam_source import process
    if args.eig_alpha:
        from mcdc.examples.slabs.eig_alpha import input
        from mcdc.examples.slabs.eig_alpha import process
    if args.eig_k:
        from mcdc.examples.slabs.eig_k  import input
        from mcdc.examples.slabs.eig_k import process

    if args.input:
        with open(args.input, 'r') as f:
            inputs = yaml.safe_load(f)
        if args.output:
            output = args.output
            input_parser(inputs,output)
        else:
            input_parser(inputs, None)