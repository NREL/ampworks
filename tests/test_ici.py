import pytest
import numpy as np
import pandas as pd
import ampworks as amp


def test_extract_params_missing_columns():

    data = amp.Dataset({'Seconds': [], 'Volts': []})  # missing 'Amps'
    with pytest.raises(ValueError):
        _ = amp.ici.extract_params(data, radius=1.8e-6)


def test_extract_params_charge_discharge():

    data = amp.datasets.load_datasets('ici_discharge')

    data['Amps'].iloc[0] = +1  # inject opposite sign
    with pytest.raises(ValueError):
        _ = amp.ici.extract_params(data, radius=1.8e-6)


def test_extract_params_basic():

    # test with charge data
    data = amp.datasets.load_datasets('ici_charge')

    params = amp.ici.extract_params(data, radius=1.8e-6)

    assert isinstance(params, pd.DataFrame)
    assert {'SOC', 'Ds', 'Eeq'}.issubset(params.columns)

    assert params.shape[0] >= 100
    assert params.notna().values.all()
    assert params['SOC'].is_monotonic_increasing

    assert np.all((params['SOC'] >= 0) & (params['SOC'] <= 1))
    assert np.all((params['Ds'] < 4e-15) & (params['Ds'] > 1e-16))
    assert np.all((params['Eeq'] >= 3.0) & (params['Eeq'] <= 4.1))

    # test with discharge data, with return_all=True
    data = amp.datasets.load_datasets('ici_discharge')

    params, stats = amp.ici.extract_params(data, radius=1.8e-6, return_all=True)

    assert isinstance(params, pd.DataFrame)
    assert {'SOC', 'Ds', 'Eeq'}.issubset(params.columns)

    assert isinstance(stats, pd.DataFrame)
    assert stats.shape[0] == params.shape[0]

    assert params.shape[0] >= 100
    assert params.notna().values.all()
    assert params['SOC'].is_monotonic_increasing

    assert np.all((params['SOC'] >= 0) & (params['SOC'] <= 1))
    assert np.all((params['Ds'] < 4e-15) & (params['Ds'] > 1e-16))
    assert np.all((params['Eeq'] >= 3.0) & (params['Eeq'] <= 4.1))


def test_extract_params_truncate_last_step():

    data = amp.datasets.load_datasets('ici_discharge')

    data['State'] = 'R'
    data.loc[data['Amps'] > 0, 'State'] = 'C'
    data.loc[data['Amps'] < 0, 'State'] = 'D'

    rest = (data['State'] != 'R') & (data['State'].shift(fill_value='R') == 'R')
    data['Rest'] = rest.cumsum()

    # get first 5 discharge/rest steps, then remove last rest
    subset = data[data['Rest'] <= 5]
    last_rest = subset[(subset['Rest'] == 5) & (subset['State'] == 'R')]
    subset = subset.drop(last_rest.index)

    params = amp.ici.extract_params(subset, radius=1.8e-6)

    assert params.shape[0] == 4  # one less than 5 b/c incomplete step cut off
    assert params.notna().values.all()  # shouldn't have NaN for complete steps


def test_extract_params_partial_rest():

    data = amp.datasets.load_datasets('ici_discharge')

    data['State'] = 'R'
    data.loc[data['Amps'] > 0, 'State'] = 'C'
    data.loc[data['Amps'] < 0, 'State'] = 'D'

    rest = (data['State'] != 'R') & (data['State'].shift(fill_value='R') == 'R')
    data['Rest'] = rest.cumsum()

    # get first 5 discharge/rest steps, then make last rest only one point long
    subset = data[data['Rest'] <= 5]
    last_rest = subset[(subset['Rest'] == 5) & (subset['State'] == 'R')]
    subset = subset.drop(last_rest[:-1].index)

    assert subset['State'].iloc[-2] != 'R'
    assert subset['State'].iloc[-1] == 'R'

    params = amp.ici.extract_params(subset, radius=1.8e-6)

    assert params.shape[0] == 5

    # first row (lowest SOC b/c discharge) should have NaN b/c incomplete rest
    assert params['SOC'].is_monotonic_increasing
    assert np.isnan(params['Eeq'].iloc[0])
    assert np.isnan(params['Ds'].iloc[0])

    # remaining rows should not have any NaN
    assert params[1:].notna().values.all()
