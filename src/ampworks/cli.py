import argparse
from .dqdv.gui_files._gui import run

def main():
    parser = argparse.ArgumentParser(description='CLI for ampworks')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dqdv', action='store_true', help='Opens the dQdV GUI')
    group.add_argument('--gitt', action='store_true', help='Opens the GITT GUI')
    
    parser.add_argument('--debug', action='store_true',
                        help='Runs a GUI in debug mode')

    args = parser.parse_args()

    if args.dqdv:
        run(args.debug)
    else:
        print("No valid argument provided.")
