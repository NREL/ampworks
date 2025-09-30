from __future__ import annotations

import pandas as pd


# Define expected headers and their aliases
def format_alias(names: str, units: str) -> str:

    aliases = units.copy()  # units only

    for n in names:
        aliases.append(f"{n}")  # name only

        for u in units:
            aliases.append(f"{n}.{u}")  # name.units

    return aliases


t_names = ['t', 'time', 'testtime']
t_units = ['s', 'sec', 'seconds', 'min', 'minutes', 'h', 'hrs', 'hours']

v_names = ['voltage', 'potential', 'ecell']
v_units = ['v', 'volts']

i_names = ['i', 'amperage', 'current']
i_units = ['a', 'amps', 'ma', 'milliamps']

q_names = ['capacity']
q_units = ['ah', 'ahr', 'amphr', 'mah', 'mahr', 'mamphr']

e_names = ['energy']
e_units = ['wh', 'whr', 'watthr']

HEADER_ALIASES = {
    'Seconds': format_alias(t_names, t_units),
    'Volts': format_alias(v_names, v_units),
    'Amps': format_alias(i_names, i_units),

    'Cycle': ['cycle', 'cyc', 'cyclec', 'cyclep', 'cycleindex', 'cyclenumber'],
    'Step': ['step', 'ns', 'stepindex'],
    'State': ['state', 'md'],

    'Ah': format_alias(q_names, q_units),
    'Wh': format_alias(e_names, e_units),

    'DateTime': ['datetime', 'dpttime'],
}


# Remove unnecessary characters from header strings
def strip_chars(string: str) -> str:
    transmap = str.maketrans('(/', '..', ' _-#<>)')
    return string.lower().translate(transmap)


# Matches input headers with aliases of the standard headers
def header_matches(headers: list[str], target_aliases: list[str]) -> bool:
    headers = [strip_chars(h) for h in headers]

    checks = {}
    for k in target_aliases:
        if any(alias in headers for alias in HEADER_ALIASES[k]):
            checks[k] = True
        else:
            checks[k] = False

    return all(checks.values())


# Standardizes the column header names and the data units
def standardize_headers(data):
    from ampworks import Dataset

    df = Dataset()

    UNIT_FACTORS = {
        'Amps': [
            ('ma', 0.001),
            ('mamps', 0.001),
            ('milliamps', 0.001),
        ],
        'Ah': [
            ('mah', 0.001),
            ('mahr', 0.001),
            ('mamphr', 0.001),
        ],
        'Seconds': [
            ('min', 60.),
            ('mins', 60.),
            ('minute', 60.),
            ('minutes', 60.),
            ('h', 3600.),
            ('hr', 3600.),
            ('hrs', 3600.),
            ('hour', 3600.),
            ('hours', 3600.),
        ]
    }

    # Match as-imported headers with standardized headers
    for std_header in HEADER_ALIASES.keys():
        for h1 in data.columns:
            h2 = strip_chars(h1)
            if h2 not in HEADER_ALIASES[std_header]:
                continue

            # Standardize units
            normalize = 1
            for key, factor in UNIT_FACTORS.get(std_header, []):
                if key in h2:
                    normalize = factor
                    break

            # Standardize headers
            df[std_header] = data[h1]*normalize

    # Create 'State' data if not present
    if ('State' not in df.columns) and ('Amps' in df.columns):
        df['Amps'] = df['Amps'].astype(float)

        df['State'] = 'R'
        df.loc[df['Amps'] > 0, 'State'] = 'C'
        df.loc[df['Amps'] < 0, 'State'] = 'D'

    # Guarantee sign 'Amps' sign convention (+ charge, - discharge)
    if 'State' in df.columns:
        df['Amps'] = df['Amps'].astype(float)

        sign = df['State'].map({'R': 0., 'C': +1, 'D': -1}).fillna(1)
        df['Amps'] = sign*df['Amps'].abs()

    # Create 'Ah' and 'Wh' from separate charge and discharge columns
    if any(h not in df.columns for h in ['Ah', 'Wh']):
        Q_headers = ['charge' + h for h in HEADER_ALIASES['Ah']]
        E_headers = ['charge' + h for h in HEADER_ALIASES['Wh']]
        for h1 in data.columns:
            h2 = strip_chars(h1)
            if h2 in Q_headers:
                df['Ah'] = data[h1]
                discharge_Ah = data[h1.replace('Charge', 'Discharge')]
                df.loc[df['State'] == 'D', 'Ah'] = discharge_Ah
            if h2 in E_headers:
                df['Wh'] = data[h1]
                discharge_Wh = data[h1.replace('Charge', 'Discharge')]
                df.loc[df['State'] == 'D', 'Wh'] = discharge_Wh

    # Final data typing and check to see which headers may still be missing
    for std_header in HEADER_ALIASES.keys():
        if std_header in df.columns:
            if std_header in ['DateTime', 'State']:
                df[std_header] = df[std_header].astype(str)
            elif std_header in ['Cycle', 'Step']:
                df[std_header] = df[std_header].astype(int)
            else:
                df[std_header] = df[std_header].replace('#', '', regex=True)
                df[std_header] = df[std_header].replace(',', '', regex=True)
                df[std_header] = df[std_header].astype(float)
        else:
            print(f"No valid headers found for '{std_header}' data")

    return df


def read_table(filepath):
    """Read tab-delimited file."""

    REQUIRED_HEADERS = ['Seconds', 'Amps', 'Volts']

    datafile = open(filepath, encoding='latin1')

    for idx, line in enumerate(datafile):

        if header_matches(line.rstrip('\n').split('\t'), REQUIRED_HEADERS):
            df = pd.read_csv(filepath, sep='\t', skiprows=idx,
                             encoding_errors='ignore')

            return standardize_headers(df)

    print(f"No valid headers found in {filepath}")


def read_excel(filepath):
    """Read excel file."""

    REQUIRED_HEADERS = ['Seconds', 'Amps', 'Volts']

    workbook = pd.ExcelFile(filepath)
    for sheet in workbook.sheet_names:
        preview = workbook.parse(sheet, header=None, nrows=20, dtype=str)

        # Find header row
        header_row = None
        for idx, row in preview.iterrows():
            if header_matches(row.values.astype(str), REQUIRED_HEADERS):
                header_row = idx
                break

        if header_row is not None:
            df = workbook.parse(sheet, header=header_row)

            return standardize_headers(df)

    print(f"No valid headers found in any sheet of {filepath}")


def read_csv(filepath):
    """Read csv file."""

    REQUIRED_HEADERS = ['Seconds', 'Amps', 'Volts']

    datafile = open(filepath, encoding='latin1')

    for idx, line in enumerate(datafile):

        if header_matches(line.rstrip('\n').split(','), REQUIRED_HEADERS):
            df = pd.read_csv(filepath, sep=',', skiprows=idx, engine='pyarrow',
                             encoding_errors='ignore')

            return standardize_headers(df)

    print(f"No valid headers found in {filepath}")
