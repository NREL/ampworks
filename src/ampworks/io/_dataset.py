from __future__ import annotations

import pandas as pd
import plotly.express as px


class Dataset(pd.DataFrame):

    @property
    def _constructor(self) -> Dataset:
        return Dataset

    @classmethod
    def from_csv(cls, filepath):
        from ampworks.io._from import read_csv
        return read_csv(filepath)

    @classmethod
    def from_excel(cls, filepath):
        from ampworks.io._from import read_excel
        return read_excel(filepath)

    @classmethod
    def from_table(cls, filepath):
        from ampworks.io._from import read_table
        return read_table(filepath)

    def downsample(self, column: str, *, n: int = None, frac: int = None,
                   resolution: float = None, inplace: bool = False,
                   ignore_index: bool = False) -> Dataset:

        if sum(x is not None for x in [n, frac, resolution]) != 1:
            raise ValueError("Specify exactly one of: n, frac, resolution")

        df = self.copy()

        if n is not None:
            step = max(1, len(df) // n)
            mask = [i % step == 0 for i in range(len(df))]

        elif frac is not None:
            step = int(1 / frac)
            mask = [i % step == 0 for i in range(len(df))]

        elif resolution is not None:
            mask = [True]  # always keep the first row
            last_val = df[column].iloc[0]
            for val in df[column].iloc[1:]:
                if val - last_val >= resolution:
                    mask.append(True)
                    last_val = val
                else:
                    mask.append(False)

        result = df[mask]

        if ignore_index:
            result = result.reset_index(drop=True)

        if inplace:
            self.__init__(result)
        else:
            return result

    def interactive_xy_plot(self, x: str, y: str, tips: list[str],
                            save: str = None) -> None:

        from ampworks import _in_notebook

        fig = px.line(
            self, x=x, y=y, markers=True,
            hover_data={col: True for col in tips},
        )

        fig.update_layout(dragmode='pan')

        config = {'scrollZoom': True}

        in_nb = _in_notebook()
        auto_open = True if not in_nb else False

        if save or not in_nb:

            path = save if save is not None else 'plot.html'
            if not path.endswith('.html'):
                path += '.html'

            fig.write_html(path, auto_open=auto_open, config=config)

        if in_nb:
            fig.show(config=config)
