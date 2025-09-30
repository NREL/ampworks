from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover
    from ampworks.utils import RichResult


class DqdvResult:

    def __init__(self, extra_cols: dict[str, type] | None = None) -> None:

        base = {
            'Ah': float,
            'xn0': float,
            'xn0_std': float,
            'xn1': float,
            'xn1_std': float,
            'xp0': float,
            'xp0_std': float,
            'xp1': float,
            'xp1_std': float,
            'iR': float,
            'iR_std': float,
            'fun': float,
            'success': bool,
            'message': str,
        }

        if extra_cols is not None:
            if not isinstance(extra_cols, dict):
                raise TypeError("'extra_cols' must be a dict[str, type].")
            for k, v in extra_cols.items():
                if not isinstance(k, str):
                    raise TypeError("'extra_cols' keys must be str.")
                if not isinstance(v, type):
                    raise TypeError("'extra_cols' values must be a type.")

            base.update(extra_cols)

        self._df = pd.DataFrame(
            {k: pd.Series(dtype=v) for k, v in base.items()},
        )

    def __getitem__(self, key):
        return self.df[key]

    def __getattr__(self, name):
        if name in self.df.columns:
            return self.df[name]
        raise AttributeError(name)

    def __repr__(self) -> str:
        return repr(self.df)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def append(self, summary: RichResult, **extra) -> None:
        row = {
            'Ah': summary.get('Ah', None),
            'fun': summary.fun,
            'success': summary.success,
            'message': summary.message,
        }

        # fill from x_map
        for idx, name in enumerate(summary.x_map):
            row[name] = summary.x[idx]
            row[name + '_std'] = summary.x_std[idx]

        # add in any extra columns
        for k in extra.keys():
            if k not in self.df.columns:
                raise ValueError(
                    f"Column '{k}' does not exist in 'DqdvResult'. Extra"
                    " columns must be defined during initialization."
                )

            row[k] = extra[k]

        # append the new row
        self.df.loc[len(self.df)] = row
