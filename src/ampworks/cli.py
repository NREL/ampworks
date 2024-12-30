import argparse
from .dqdv import run_gui

def main():
    parser = argparse.ArgumentParser(description='CLI for ampworks')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dqdv', action='store_true', help='Opens the dQdV GUI')
    group.add_argument('--gitt', action='store_true', help='Opens the GITT GUI')

    args = parser.parse_args()

    if args.dqdv:
        run_gui()
    else:
        print("No valid argument provided.")
