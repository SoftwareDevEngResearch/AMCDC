import sys
import argparse

parser = argparse.ArgumentParser(
    description='command line'
    )
parser.add_argument('-e','examples',
                    help='Examples problems'
                    )
args = parser.parse_args(sys.argv[1:])