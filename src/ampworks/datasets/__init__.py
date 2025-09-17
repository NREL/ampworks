"""
TODO
----

"""

from __future__ import annotations
from typing import TYPE_CHECKING

import os
import shutil
import pathlib

if TYPE_CHECKING:  # pragma: no cover
    from ampworks import Dataset
 
__all__ = [
    'download_all',
    'list_datasets',
    'load_datasets',
]
    

def list_datasets() -> list[str]:
    resources = pathlib.Path(os.path.dirname(__file__), 'resources')
    return os.listdir(resources)


def download_all(path: str | None = None) -> None:
    
    resources = pathlib.Path(os.path.dirname(__file__), 'resources')
    
    path = pathlib.Path(path or '.').joinpath('ampworks_datasets')
    path.mkdir(parents=True, exist_ok=True)
    
    for name in list_datasets():
        orig = os.path.join(resources, name)
        new = os.path.join(path, name)
        
        shutil.copy(orig, new)


def load_datasets(*names: str) -> Dataset:
    from ampworks import read_csv
    
    available = list_datasets()
    resources = pathlib.Path(os.path.dirname(__file__), 'resources')
    
    datasets = []
    for name in names:
        
        if not name.endswith('.csv'):
            name += '.csv'
            
        if name not in available:
            raise ValueError(f"{name} is not an available dataset.")
        
        data = read_csv(resources.joinpath(name))
        
        datasets.append(data)
        
    if len(datasets) == 1:
        return datasets[0]
    
    return tuple(datasets)
            
            