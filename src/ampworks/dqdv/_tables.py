from __future__ import annotations
from typing import TYPE_CHECKING

import pandas as pd

from ampworks.utils import RichTable

if TYPE_CHECKING:  # pragma: no cover
    from ampworks.utils import RichResult


class DqdvFitTable(RichTable):
    _required_cols = [
        'Ah', 'xn0', 'xn0_std', 'xn1', 'xn1_std', 'xp0', 'xp0_std',
        'xp1', 'xp1_std', 'iR', 'iR_std', 'fun', 'success', 'message',
    ]

    def __init__(self, extra_cols: list[str] | None = None) -> None:

        if extra_cols is None:
            extra_cols = []

        data = {col: [] for col in self._required_cols + extra_cols}

        df = pd.DataFrame(data)

        super().__init__(df)

    def append(self, summary: RichResult, **extra_cols) -> None:
        row = {
            'Ah': summary.Ah,
            'fun': summary.fun,
            'success': summary.success,
            'message': summary.message,
        }

        # fill from x_map
        for idx, name in enumerate(summary.x_map):
            row[name] = summary.x[idx]
            row[name + '_std'] = summary.x_std[idx]

        # add in any extra columns
        for k in extra_cols.keys():
            if k not in self.df.columns:
                raise ValueError(
                    f"Column '{k}' does not exist in 'DqdvFitResult'. Extra"
                    " columns must be defined during initialization."
                )

            row[k] = extra_cols[k]

        # append the new row
        self.df.loc[len(self.df)] = row


class AgingTable(RichTable):
    _required_cols = [
        'Qn', 'Qn_std', 'Qp', 'Qp_std', 'LAMn', 'LAMn_std', 'LAMp', 'LAMp_std',
        'LLI', 'LLI_std',
    ]
