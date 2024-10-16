def alphanumeric_sort(unsorted_list: list[str]) -> list[str]:
    import re

    convert = lambda txt: int(txt) if txt.isdigit() else txt
    alphanum = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

    sorted_list = sorted(unsorted_list, key=alphanum)

    return sorted_list


class ProgressBar:

    __slots__ = ['width']

    def __init__(self, width: int = 50) -> None:
        self.width = width

    def update(self, percent) -> None:
        import sys

        done = int(percent * self.width)
        wait = self.width - int(percent * self.width)

        bar = '[' + '#' * done + '-' * wait + ']'
        sys.stdout.write('\r' + f'Progress: {bar} {percent * 100:.2f}%')
        sys.stdout.flush()
