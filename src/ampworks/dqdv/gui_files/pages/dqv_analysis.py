import dash
import numpy as np
import pandas as pd
from dash import dcc, html, Output, Input, State
from scipy._lib._util import _RichResult as RichResult

from ampworks.dqdv.gui_files.pages.figures import figure_div
from ampworks.dqdv.gui_files.pages.components import (
    sliders, optimize_btns, page_spinner, terminal, logging_btns, log_toast,
    download, logging_table,
)

dash.register_page(
    __name__,
    path='/dqv-analysis',
    title='DVQ Analysis',
    page_components=[
        figure_div,
        sliders,
        optimize_btns,
        page_spinner,
        terminal,
        logging_btns,
        log_toast,
        download,
        logging_table,
    ],
)

# Page layout
layout = html.Div()

# Callbacks
@dash.callback(
    Output('terminal-out', 'children'),
    Input('summary-store', 'data'),
)
def update_terminal(summary):
    if summary:
        summary['message'] = f"'{summary.get('message', 'Done searching.')}'"
        summary['success'] = summary.get('success', True)
        summary['x'] = np.round(summary['x'], 10)
        summary['niter'] = summary.get('niter')
        summary['x_map'] = summary.pop('x_map')
        result = RichResult(**summary)
    else:
        result = RichResult({
            'message': None,
            'success': None,
            'fun': None,
            'x': None,
            'nfev': None,
            'niter': None,
            'x_map': ['x0_neg', 'x100_neg', 'x0_pos', 'x100_pos', 'iR'],
        })

    return f"```python\n{result!r}\n```"


@dash.callback(
    Output('ag-grid', 'rowData'),
    Output('log-toast', 'is_open'),
    Output('log-toast', 'children'),
    Input('add-row-btn', 'n_clicks'),
    State('ag-grid', 'rowData'),
    State('summary-store', 'data'),
    State({'type': 'filename', 'index': 'cell'}, 'children'),
    prevent_initial_call=True,
)
def log_new_row(_, current_data, summary, filename):
    if not current_data:
        current_data = []

    if not summary:
        return current_data, dash.no_update, dash.no_update

    if 'iR' not in summary['x_map']:
        summary['x'] = np.hstack([summary['x'], 0.])
        summary['x_map'].append('iR')

    new_row = dict((k, v) for k, v in zip(summary['x_map'], summary['x']))
    new_row['fun'] = summary['fun']

    new_row['filename'] = filename.removesuffix('.csv')

    current_data.append(new_row)

    return current_data, True, filename + ' added to log.'


@dash.callback(
    Output('ag-grid', 'deleteSelectedRows'),
    Input('delete-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def selected(_):
    return True


@dash.callback(
    Output('download-csv', 'data'),
    Input('export-btn', 'n_clicks'),
    State('ag-grid', 'rowData'),
    State('ag-grid', 'columnDefs'),
    prevent_initial_call=True,
)
def export_to_csv(_, row_data, column_defs):
    if row_data:
        df = pd.DataFrame(row_data)
        ordered_cols = [c['field'] for c in column_defs]
        df = df[ordered_cols]
        return dcc.send_data_frame(df.to_csv, 'DVQ_Data.csv', index=False)
    else:
        return dash.no_update
