import argparse


def main():
    parser = argparse.ArgumentParser(description='CLI for ampworks')

    parser.add_argument(
        '--debug',
        action='store_true',
        help='enables debug mode',
    )

    parser.add_argument(
        '--app',
        required=True,
        choices=['dQdV'],
        help='name of app to open',
    )

    args = parser.parse_args()

    if args.app.lower() == 'dqdv':
        from .dqdv.gui_files._gui import run
        run(debug=args.debug)
    else:
        print("No valid argument provided.")
