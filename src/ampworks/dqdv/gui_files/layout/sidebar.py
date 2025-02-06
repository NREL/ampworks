import io
import base64

import dash
import numpy as np
import pandas as pd
import ampworks as amp
import plotly.io as pio
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State
from dash_bootstrap_templates import load_figure_template

from ampworks.dqdv.gui_files.pages.figures import figure, placeholder_fig

fitter = amp.dqdv.Fitter()
optimal_params = False

load_figure_template(['bootstrap', 'bootstrap_dark'])


def file_upload(label, identifier):
    if identifier == 'neg':
        upload_label = dbc.Label(label, class_name='bold-label')
    else:
        upload_label = dbc.Label(label, class_name='bold-label mt-3')

    horizontal_divider = html.Hr(className='m-0')

    file_uploader = dcc.Upload(
        id={'type': 'upload', 'index': identifier},
        children=html.Div(
            [
                'Drag & Drop or ',
                html.A('Select File'),
            ],
            style={'textAlign': 'center'},
        ),
        multiple=False,
        className='upload-btn',
        className_active='upload-btn-active',
        className_reject='upload-btn-reject',
        accept='.csv, text/csv, application/csv',
        style={
            'width': '80%',
            'height': '3em',
            'lineHeight': '3em',
            'borderWidth': '1px',
            'borderRadius': '5px',
            'borderStyle': 'dashed',
            'margin': '10px auto 0',
        },
    )

    check_icon = html.I(className='fa fa-circle-check')

    filename_field = dbc.Stack(
        [
            html.Div(id={'type': 'filename', 'index': identifier}),
            html.Div(check_icon, className='ms-auto'),
        ],
        gap=3,
        direction='horizontal',
        id={'type': 'filename-row', 'index': identifier},
        style={
            'width': '80%',
            'display': 'none',
            'fontSize': '0.75em',
            'margin': '5px auto 0',
        }
    )

    upload_block = [
        upload_label,
        horizontal_divider,
        file_uploader,
        filename_field,
    ]

    return upload_block


upload = html.Div(
    [
        *file_upload('Negative Electrode', 'neg'),
        *file_upload('Positive Electrode', 'pos'),
        *file_upload('Full Cell', 'cell'),
    ],
    id='upload-menu',
)


def number_input(id, low, high, step, value, **kwargs):
    input = dbc.Input(
        min=low,
        max=high,
        step=step,
        value=value,
        type='number',
        placeholder=value,
        id={'type': 'opt', 'index': id},
        **kwargs,
    )

    return dbc.Col(input, width=5, class_name='m-0')


def switch_input(id, value):
    switch = dbc.Switch(
        value=value,
        id={'type': 'cost', 'index': id},
    )

    return dbc.Col(switch, width=4, class_name='m-0')


opt_data = {
    'smoothing': 10,
    'xmin-bnd-neg': 0.1,
    'xmax-bnd-neg': 0.1,
    'xmin-bnd-pos': 0.1,
    'xmax-bnd-pos': 0.1,
    'coarse-Nx': 11,
    'max-iter': 1e5,
    'xtol': 1e-9,
    'voltage': True,
    'dqdv': True,
    'dvdq': True,
}

optimize = html.Div([
    dbc.Label('Model Parameters', class_name='bold-label'),
    html.Hr(className='m-0'),
    dbc.Row([
        dbc.Col(dbc.Label('Smoothing')),
        number_input('smoothing', 3, 25, 1,
                     opt_data['smoothing'], debounce=True),
    ], style={'width': '90%', 'margin': '5px auto'}),

    dbc.Label('Negative Electrode', class_name='bold-label'),
    html.Hr(className='m-0'),
    dbc.Row([
        dbc.Col(dbc.Label('xmin bounds (+/-)')),
        number_input('xmin-bnd-neg', 1e-3, 1, 1e-3, opt_data['xmin-bnd-neg']),
    ], style={'width': '90%', 'margin': '5px auto'}),
    dbc.Row([
        dbc.Col(dbc.Label('xmax bounds (+/-)')),
        number_input('xmax-bnd-neg', 1e-3, 1, 1e-3, opt_data['xmax-bnd-neg']),
    ], style={'width': '90%', 'margin': '5px auto'}),

    dbc.Label('Positive Electrode', class_name='bold-label'),
    html.Hr(className='m-0'),
    dbc.Row([
        dbc.Col(dbc.Label('xmin bounds (+/-)')),
        number_input('xmin-bnd-pos', 1e-3, 1, 1e-3, opt_data['xmin-bnd-pos']),
    ], style={'width': '90%', 'margin': '5px auto'}),
    dbc.Row([
        dbc.Col(dbc.Label('xmax bounds (+/-)')),
        number_input('xmax-bnd-pos', 1e-3, 1, 1e-3, opt_data['xmax-bnd-pos']),
    ], style={'width': '90%', 'margin': '5px auto'}),

    dbc.Label('Fitting Parameters', class_name='bold-label'),
    html.Hr(className='m-0'),
    dbc.Row([
        dbc.Col(dbc.Label('Coarse Nx')),
        number_input('coarse-Nx', 11, 51, 1, opt_data['coarse-Nx']),
    ], style={'width': '90%', 'margin': '5px auto'}),
    dbc.Row([
        dbc.Col(dbc.Label('Max Iterations')),
        number_input('max-iter', 1e3, 1e6, 1, opt_data['max-iter']),
    ], style={'width': '90%', 'margin': '5px auto'}),
    dbc.Row([
        dbc.Col(dbc.Label('x Tolerance')),
        number_input('xtol', 1e-15, 1e-2, 'any', opt_data['xtol']),
    ], style={'width': '90%', 'margin': '5px auto'}),

    dbc.Label('Cost Terms', class_name='bold-label'),
    html.Hr(className='m-0'),
    dbc.Row([
        dbc.Col(dbc.Label('Voltage')),
        switch_input('voltage', opt_data['voltage']),
    ], style={'width': '90%', 'margin': '5px auto'}),
    dbc.Row([
        dbc.Col(dbc.Label('Differential SOC')),
        switch_input('dqdv', opt_data['dqdv']),
    ], style={'width': '90%', 'margin': '5px auto'}),
    dbc.Row([
        dbc.Col(dbc.Label('Differential Voltage')),
        switch_input('dvdq', opt_data['dvdq']),
    ], style={'width': '90%', 'margin': '5px auto'}),
],
    id='optimize-menu',
)


def line_properties(label, identifier, values):
    linestyles = dict((v, v) for v in ['solid', 'dash', 'dot'])
    linewidths = dict((v, v) for v in [1, 2, 3, 4, 5])

    id_style = {'type': 'line-style', 'index': identifier}
    id_width = {'type': 'line-width', 'index': identifier}
    id_color = {'type': 'line-color', 'index': identifier}

    prop_label = dbc.Label(label, class_name='bold-label')

    horizontal_divider = html.Hr(className='m-0')

    linestyle = dbc.Row([
        dbc.Col(dbc.Label('Line style')),
        dbc.Col(dbc.Select(linestyles, value=values[0], id=id_style), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    linewidth = dbc.Row([
        dbc.Col(dbc.Label('Line width')),
        dbc.Col(dbc.Select(linewidths, value=values[1], id=id_width), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    linecolor = dbc.Row([
        dbc.Col(dbc.Label('Color')),
        dbc.Col(dbc.Input(type='color', value=values[2], id=id_color), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    props_block = [
        prop_label,
        horizontal_divider,
        linestyle,
        linewidth,
        linecolor,
    ]

    return props_block


def marker_properties(label, identifier, values):
    markstyles = dict((v, v) for v in ['o', 'x', '^', '+'])
    marksizes = dict((v, v) for v in [5, 10, 15, 20, 25])

    id_style = {'type': 'mark-style', 'index': identifier}
    id_size = {'type': 'mark-size', 'index': identifier}
    id_color = {'type': 'mark-color', 'index': identifier}

    prop_label = dbc.Label(label, class_name='bold-label')

    horizontal_divider = html.Hr(className='m-0')

    linestyle = dbc.Row([
        dbc.Col(dbc.Label('Marker style')),
        dbc.Col(dbc.Select(markstyles, value=values[0], id=id_style), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    linewidth = dbc.Row([
        dbc.Col(dbc.Label('Line width')),
        dbc.Col(dbc.Select(marksizes, value=values[1], id=id_size), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    linecolor = dbc.Row([
        dbc.Col(dbc.Label('Color')),
        dbc.Col(dbc.Input(type='color', value=values[2], id=id_color), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    props_block = [
        prop_label,
        horizontal_divider,
        linestyle,
        linewidth,
        linecolor,
    ]

    return props_block


neg_style = ['solid', 2, '#dc3912']
pos_style = ['solid', 2, '#3366cc']
cell_style = ['o', 10, '#990099']
model_style = ['solid', 2, '#999999']

fig_menu = html.Div(
    [
        *line_properties('Negative Electrode', 'neg', neg_style),
        *line_properties('Positive Electrode', 'pos', pos_style),
        *marker_properties('Full Cell', 'cell', cell_style),
        *line_properties('Model Fits', 'model', model_style),
    ],
    id='figure-menu',
)

up_icon = html.Div(
    [
        html.I(className='fa fa-file-import sidebar-icon'),
        html.P('Upload Data', className='m-0'),
    ],
    className='d-flex align-items-center',
)

opt_icon = html.Div(
    [
        html.I(className='fa fa-gears sidebar-icon'),
        html.P('Optimization Settings', className='m-0'),
    ],
    className='d-flex align-items-center',
)

fig_icon = html.Div(
    [
        html.I(className='fa fa-chart-line sidebar-icon'),
        html.P('Figure Options', className='m-0'),
    ],
    className='d-flex align-items-center',
)

accordion = dbc.Accordion(
    [
        dbc.AccordionItem(upload, title=up_icon, class_name='sidebar'),
        dbc.AccordionItem(optimize, title=opt_icon, class_name='sidebar'),
        dbc.AccordionItem(fig_menu, title=fig_icon, class_name='sidebar'),
    ],
    flush=True,
    class_name='accordion',
    style={'width': '100%'},
)

opt_store = dcc.Store(
    data=opt_data,
    id='opt-store',
)

flags = dcc.Store(
    id='flags',
    data={'neg': False, 'pos': False, 'cell': False},
)

summary_store = dcc.Store(
    data={},
    id='summary-store',
)

sidebar = dbc.Offcanvas(
    id='sidebar',
    scrollable=True,
    class_name='sidebar',
    children=[opt_store, flags, summary_store, accordion],
)

# Toggle sidebar for small screens
dash.clientside_callback(
    """
    function toggleSidebar(nClick, isOpen) {
        return !isOpen;
    }
    """,
    Output('sidebar', 'is_open', allow_duplicate=True),
    Input('sidebar-btn', 'n_clicks'),
    State('sidebar', 'is_open'),
    prevent_initial_call=True,
)

# Reset optimization values to placeholder on blur if invalid
dash.clientside_callback(
    """
    function(blur, value, min, max, placeholder) {
        if (value >= min && value <= max) {
            return value;
        }

        return placeholder;
    }
    """,
    Output({'type': 'opt', 'index': dash.MATCH}, 'value'),
    Input({'type': 'opt', 'index': dash.MATCH}, 'n_blur'),
    State({'type': 'opt', 'index': dash.MATCH}, 'value'),
    State({'type': 'opt', 'index': dash.MATCH}, 'min'),
    State({'type': 'opt', 'index': dash.MATCH}, 'max'),
    State({'type': 'opt', 'index': dash.MATCH}, 'placeholder'),
    prevent_initial_call=True,
)

# Sync optimization input changes to dcc.Store
dash.clientside_callback(
    """
    function(values, data) {
        const triggered = dash_clientside.callback_context.triggered;
        const id = triggered[0].prop_id.split(".")[0];
        const idx = JSON.parse(id).index;

        data[idx] = triggered[0].value;

        return data;
    }
    """,
    Output('opt-store', 'data', allow_duplicate=True),
    Input({'type': 'opt', 'index': dash.ALL}, 'value'),
    State('opt-store', 'data'),
    prevent_initial_call=True,
)

# Ensure at least one cost switch is always active
dash.clientside_callback(
    """
    function(switchValues, data) {
        const triggered = dash_clientside.callback_context.triggered;
        const id = triggered[0].prop_id.split(".")[0];
        const idx = JSON.parse(id).index;

        data[idx] = triggered[0].value;

        const enabledCount = switchValues.filter(v => v).length;
        const switchStates = switchValues.map(v => enabledCount === 1 && v);

        return [data, switchStates];
    }
    """,
    Output('opt-store', 'data', allow_duplicate=True),
    Output({'type': 'cost', 'index': dash.ALL}, 'disabled'),
    Input({'type': 'cost', 'index': dash.ALL}, 'value'),
    State('opt-store', 'data'),
    prevent_initial_call=True,
)

# Support functions
def make_figure(params, flags, new_data=False):

    if new_data and all(flags.values()):
        output = fitter.err_terms(params, full_output=True)

        x = output['soc']
        xm = output['soc_mid']

        y1d = output['V_dat']
        y2d = output['dqdv_dat']
        y3d = output['dvdq_dat']

        y1f = output['V_fit']
        y2f = output['dqdv_fit']
        y3f = output['dvdq_fit']

        figure.data = ()

        mk = {}  # dict(color='#990099', size=10, symbol='circle')
        ln = {}  # dict(color='#999999', width=2, dash='solid')

        dat = dict(mode='markers', name='Full Cell',
                   showlegend=False, marker=mk)
        fit = dict(mode='lines', name='Model', showlegend=False, line=ln)

        figure.add_trace(go.Scatter(x=x, y=y1d, **dat), row=1, col=1)
        figure.add_trace(go.Scatter(x=xm, y=y2d, **dat), row=1, col=2)
        figure.add_trace(go.Scatter(x=xm, y=y3d, **dat), row=1, col=3)

        figure.add_trace(go.Scatter(x=x, y=y1f, **fit), row=1, col=1)
        figure.add_trace(go.Scatter(x=xm, y=y2f, **fit), row=1, col=2)
        figure.add_trace(go.Scatter(x=xm, y=y3f, **fit), row=1, col=3)

    elif all(flags.values()):
        output = fitter.err_terms(params, full_output=True)

        figure.data[3].y = output['V_fit']
        figure.data[4].y = output['dqdv_fit']
        figure.data[5].y = output['dvdq_fit']

    if all(flags.values()):
        return figure
    else:
        return placeholder_fig


UPLOAD_IDS = ['neg', 'pos', 'cell']


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    Output('flags', 'data', allow_duplicate=True),
    Input({'type': 'upload', 'index': dash.ALL}, 'contents'),
    State('neg-slider', 'value'),
    State('pos-slider', 'value'),
    State('flags', 'data'),
    prevent_initial_call=True,
)
def upload_data(contents_list, neg_s, pos_s, flags):
    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    key = eval(trigger)['index']

    contents = contents_list[UPLOAD_IDS.index(key)]

    if contents is not None:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        setattr(fitter, 'df_' + key, pd.read_csv(io.BytesIO(decoded)))
        flags[key] = True

    params = np.array(neg_s + pos_s)

    figure = make_figure(params, flags, new_data=True)

    return figure, flags


@dash.callback(
    Output({'type': 'filename', 'index': dash.MATCH}, 'children'),
    Output({'type': 'filename-row', 'index': dash.MATCH}, 'style'),
    Input({'type': 'upload', 'index': dash.MATCH}, 'filename'),
    State({'type': 'filename-row', 'index': dash.MATCH}, 'style'),
    prevent_initial_call=True,
)
def show_filename(filename, style):
    new_style = {**style, 'display': 'flex'}
    return f"{filename}", new_style


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    Input({'type': 'opt', 'index': 'smoothing'}, 'value'),
    State('neg-slider', 'value'),
    State('pos-slider', 'value'),
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_on_smoothing(smoothing, neg_s, pos_s, flags):
    fitter.smoothing = smoothing
    params = np.array(neg_s + pos_s)
    figure = make_figure(params, flags)
    return figure


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    Output('neg-slider-label', 'children', allow_duplicate=True),
    Output('pos-slider-label', 'children', allow_duplicate=True),
    Input('neg-slider', 'value'),
    Input('pos-slider', 'value'),
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_on_slider(neg_s, pos_s, flags):
    global optimal_params

    params = np.array(neg_s + pos_s)
    if isinstance(optimal_params, np.ndarray):
        figure = make_figure(optimal_params, flags)
    else:
        figure = make_figure(params, flags)

    neg_label = f"Negative Electrode: [{neg_s[0]:.2f}, {neg_s[1]:.2f}]"
    pos_label = f"Positive Electrode: [{pos_s[0]:.2f}, {pos_s[1]:.2f}]"

    optimal_params = False

    return figure, neg_label, pos_label


@dash.callback(
    Output('spinner-div', 'children', allow_duplicate=True),
    Output('neg-slider', 'value', allow_duplicate=True),
    Output('pos-slider', 'value', allow_duplicate=True),
    Output('summary-store', 'data'),
    Input('coarse-btn', 'n_clicks'),
    Input('min-err-btn', 'n_clicks'),
    State('neg-slider', 'value'),
    State('pos-slider', 'value'),
    State('opt-store', 'data'),
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_on_button(_c, _m, neg_s, pos_s, opt_data, flags):
    global optimal_params

    trigger = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    fitter.xtol = opt_data['xtol']
    fitter.maxiter = opt_data['max-iter']
    fitter.smoothing = opt_data['smoothing']
    fitter.bounds = [
        opt_data['xmin-bnd-neg'],
        opt_data['xmax-bnd-neg'],
        opt_data['xmin-bnd-pos'],
        opt_data['xmax-bnd-pos'],
    ]

    cost_terms = []
    if opt_data['voltage']:
        cost_terms.append('voltage')
    if opt_data['dqdv']:
        cost_terms.append('dqdv')
    if opt_data['dvdq']:
        cost_terms.append('dvdq')

    fitter.cost_terms = cost_terms

    summary = {}
    if trigger == 'coarse-btn' and _c and all(flags.values()):
        summary = fitter.coarse_search(opt_data['coarse-Nx'])
        params = summary['x']
    elif trigger == 'min-err-btn' and all(flags.values()):
        x0 = np.array(neg_s + pos_s)
        summary = fitter.constrained_fit(x0)
        params = summary['x']
    else:
        params = np.array(neg_s + pos_s)

    optimal_params = params.copy()

    if summary:
        neg_s[0] = round(summary['x'][0], 2)
        neg_s[1] = round(summary['x'][1], 2)

        pos_s[0] = round(summary['x'][2], 2)
        pos_s[1] = round(summary['x'][3], 2)

    return '', neg_s, pos_s, summary


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    Input('theme-switch', 'value'),
    State('flags', 'data'),
    prevent_initial_call=True,
)
def toggle_theme_switch(switch_on, flags):
    if switch_on:
        border_color = '#212529'
        template = pio.templates['bootstrap']
    else:
        border_color = '#DEE2E6'
        template = pio.templates['bootstrap_dark']

    figure.update_layout(template=template)
    
    for i in range(3):
        figure.update_xaxes(
            row=1, col=i+1,
            linecolor=border_color, tickcolor=border_color,
        )
        figure.update_yaxes(
            row=1, col=i+1,
            linecolor=border_color, tickcolor=border_color,
        )

    if all(flags.values()):
        return figure
    else:
        return placeholder_fig
