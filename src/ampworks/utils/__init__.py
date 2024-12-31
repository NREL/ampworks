"""
TODO
----

"""

def alphanumeric_sort(unsorted_list: list[str]) -> list[str]:
    """
    TODO

    Parameters
    ----------
    unsorted_list : list[str]
        _description_

    Returns
    -------
    list[str]
        _description_
        
    """
    import re

    def convert(txt): return int(txt) if txt.isdigit() else txt
    def alphanum(key): return [convert(c) for c in re.split('([0-9]+)', key)]

    sorted_list = sorted(unsorted_list, key=alphanum)

    return sorted_list


class ProgressBar:
    """Progress bar"""

    __slots__ = ['width']

    def __init__(self, width: int = 50) -> None:
        """
        TODO

        Parameters
        ----------
        width : int, optional
            _description_, by default 50
            
        """
        self.width = width

    def update(self, percent) -> None:
        """
        TODO

        Parameters
        ----------
        percent : _type_
            _description_
            
        """
        import sys

        done = int(percent * self.width)
        wait = self.width - int(percent * self.width)

        bar = '[' + '#' * done + '-' * wait + ']'
        sys.stdout.write('\r' + f'Progress: {bar} {percent * 100:.2f}%')
        sys.stdout.flush()
