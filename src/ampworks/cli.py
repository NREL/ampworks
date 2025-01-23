import argparse


def main():
    parser = argparse.ArgumentParser(description='CLI for ampworks')

    parser.add_argument(
        '--app',
        required=True,
        choices=['dQdV'],
        help='name of app to open',
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='enables debug mode',
    )

    args = parser.parse_args()

    if args.app.lower() == 'dqdv':
        from .dqdv.gui_files._gui import run
        run(args.debug)
    else:
        print("No valid argument provided.")
