import time

import pytest
import numpy as np
import ampworks as amp


def test_alphanumeric_sort():

    unsorted = [
        'apple3',
        'banana12',
        'grape10',
        'orange2',
        'pear7',
        'kiwi5',
        'date1',
        '10apple',
        '2banana',
        '100grape',
    ]

    sorted_list = [
        '2banana',
        '10apple',
        '100grape',
        'apple3',
        'banana12',
        'date1',
        'grape10',
        'kiwi5',
        'orange2',
        'pear7',
    ]

    sorted_test = amp.utils.alphanum_sort(unsorted)
    assert sorted_test == sorted_list

    sorted_list.reverse()

    reversed_test = amp.utils.alphanum_sort(unsorted, reverse=True)
    assert reversed_test == sorted_list
    assert reversed_test != sorted_test


def test_progbar_initialization():

    with pytest.raises(ValueError, match='conflicting'):
        _ = amp.utils.ProgressBar(iterable=[1, 2, 3], manual=True)

    with pytest.raises(ValueError, match='cannot be None'):
        _ = amp.utils.ProgressBar(iterable=None, manual=False)

    bar = amp.utils.ProgressBar(iterable=[1, 2, 3])
    assert bar._manual is False
    assert bar.total == 3

    bar = amp.utils.ProgressBar(manual=True)
    assert bar._manual is True
    assert bar.total == 1


def test_iterable_progbar():
    iterable = range(10)

    bar = amp.utils.ProgressBar(iterable)
    for i in bar:
        pass

    assert bar._manual is False


def test_manual_progbar():

    bar = amp.utils.ProgressBar(manual=True)
    for i in range(10):
        bar.set_progress(0.1*(i+1))

    assert bar._manual is True
    assert bar._iter == 10

    bar.reset()
    assert bar._iter == 0


def test_RichResult():

    result = amp.utils.RichResult()
    assert result._order_keys == []
    assert repr(result) == 'RichResult()'

    class NewResult(amp.utils.RichResult):
        pass

    result = NewResult()
    assert repr(result) == 'NewResult()'

    class OrderedResult(amp.utils.RichResult):
        _order_keys = ['first', 'second',]

    new = NewResult(second=None, first=None)
    ordered = OrderedResult(second=None, first=None)
    assert new.__dict__ == ordered.__dict__
    assert repr(new) != repr(ordered)


def test_format_float_10():
    from ampworks.utils._rich_result import _format_float_10

    assert _format_float_10(np.inf) == '       inf'
    assert _format_float_10(-np.inf) == '      -inf'
    assert _format_float_10(np.nan) == '       nan'

    assert _format_float_10(0.123456789) == ' 1.235e-01'
    assert _format_float_10(1.234567890) == ' 1.235e+00'
    assert _format_float_10(1234.567890) == ' 1.235e+03'


def test_timer():

    with pytest.raises(ValueError):
        timer = amp.utils.Timer(units='fake')

    def f():
        time.sleep(1e-3)
        return 0.

    with amp.utils.Timer('success') as timer:
        _ = f()

    assert timer.name == 'success'
    assert timer.elapsed_time >= 0.
    assert timer._converter['s'](3600.) == 3600.
    assert timer._converter['min'](3600.) == 60.
    assert timer._converter['h'](3600.) == 1.
