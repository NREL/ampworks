from __future__ import annotations

import pandas as pd
import plotly.express as px


def _is_notebook():
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell in ('ZMQInteractiveShell',)  # Jupyter Notebook or Lab
    except Exception:
        return False


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
        
    def interactive_xy_plot(self, x: str, y: str, tips: list[str]) -> None:
        
        fig = px.line(
            self, x=x, y=y, markers=True, 
            hover_data={col: True for col in tips},
        )
        
        fig.update_layout(dragmode='pan')
                
        config = {'scrollZoom': True}

        if _is_notebook():
            fig.show(config=config)
        else:
            fig.write_html('plot.html', auto_open=True, config=config)