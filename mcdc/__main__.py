import sys

from mcdc.mcdc_input import mcdc_input

def main(args=None):
    if args is None:
        args = sys.argv[1:]
        mcdc_input(args)

if __name__ == '__main__':
    sys.exit(main())