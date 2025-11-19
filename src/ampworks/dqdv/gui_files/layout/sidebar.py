import io
import base64

import dash
import numpy as np
import pandas as pd
import ampworks as amp
import dash_bootstrap_components as dbc

from dash import dcc, html, Output, Input, State

from ampworks.dqdv.gui_files.pages.figures import figure, placeholder_fig

fitter = amp.dqdv.DqdvFitter()
optimal_params = False


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
        accept='.csv,text/csv,application/csv',
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
    'xmin-bnd-neg': 0.1,
    'xmax-bnd-neg': 0.1,
    'xmin-bnd-pos': 0.1,
    'xmax-bnd-pos': 0.1,
    'grid-Nx': 11,
    'max-iter': 1e5,
    'xtol': 1e-8,
    'voltage': True,
    'dqdv': True,
    'dvdq': True,
}

optimize = html.Div([
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
        dbc.Col(dbc.Label('Grid Nx')),
        number_input('grid-Nx', 11, 51, 1, opt_data['grid-Nx']),
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

    id_style = 'ls-' + identifier
    id_width = 'lw-' + identifier
    id_color = 'clr-' + identifier

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
    markstyles = dict((v, v) for v in ['circle', 'square', 'diamond'])
    marksizes = dict((v, v) for v in [1, 2, 3, 4, 5])

    id_style = 'mk-' + identifier
    id_size = 'ms-' + identifier
    id_color = 'clr-' + identifier

    prop_label = dbc.Label(label, class_name='bold-label')

    horizontal_divider = html.Hr(className='m-0')

    linestyle = dbc.Row([
        dbc.Col(dbc.Label('Marker style')),
        dbc.Col(dbc.Select(markstyles, value=values[0], id=id_style), width=5),
    ], style={'width': '90%', 'margin': '5px auto'})

    linewidth = dbc.Row([
        dbc.Col(dbc.Label('Marker size')),
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


neg_style = ['solid', 2, '#1f77b4']
pos_style = ['solid', 2, '#d62728']
cell_style = ['circle', 2, '#c5c5c5']
model_style = ['solid', 2, '#000000']

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
    from ampworks.plotutils import focused_limits

    if not all(flags.values()):
        return placeholder_fig

    errs = fitter.err_terms(params)

    soc = errs['soc']

    volt_data = errs['volt_data']
    dqdv_data = errs['dqdv_data']
    dvdq_data = errs['dvdq_data']

    volt_fit = errs['volt_fit']
    dqdv_fit = errs['dqdv_fit']
    dvdq_fit = errs['dvdq_fit']

    volt_err = errs['volt_err']
    dqdv_err = errs['dqdv_err']
    dvdq_err = errs['dvdq_err']

    xn0, xn1, xp0, xp1 = params[:4]

    socp = (soc - xp0) / (xp1 - xp0)
    ocv_p = fitter._ocv_p(soc)

    socn = (soc - xn0) / (xn1 - xn0)
    ocv_n = fitter._ocv_n(soc)

    if new_data:

        for i in range(0, 3):
            figure.data[i].x = soc[::5] if i == 0 else soc[::3]

        for i in range(3, 6):
            figure.data[i].x = soc

        figure.data[0].y = volt_data[::5]
        figure.data[1].y = dqdv_data[::3]
        figure.data[2].y = dvdq_data[::3]

        # focus ylimits for dvdq
        ylims = focused_limits(np.hstack([dvdq_data, dvdq_fit]))
        figure.update_yaxes(
            row=2, col=2, range=ylims,
            autorangeoptions=dict(minallowed=ylims[0], maxallowed=ylims[1]),
        )

    figure.data[3].y = volt_fit
    figure.data[4].y = dqdv_fit
    figure.data[5].y = dvdq_fit

    figure.layout.annotations[0].text = f"MAPE={volt_err:.2e}%"
    figure.layout.annotations[1].text = f"MAPE={dqdv_err:.2e}%"
    figure.layout.annotations[2].text = f"MAPE={dvdq_err:.2e}%"

    figure.data[6].x = socp
    figure.data[6].y = ocv_p

    figure.data[7].x = socn
    figure.data[7].y = ocv_n

    return figure


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

        setattr(fitter, key, pd.read_csv(io.BytesIO(decoded)))
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
    Input('grid-btn', 'n_clicks'),
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

    options = {
        'xtol': opt_data['xtol'],
        'maxiter': opt_data['max-iter'],
        'bounds': [
            opt_data['xmin-bnd-neg'],
            opt_data['xmax-bnd-neg'],
            opt_data['xmin-bnd-pos'],
            opt_data['xmax-bnd-pos'],
        ],
    }

    cost_terms = []
    if opt_data['voltage']:
        cost_terms.append('voltage')
    if opt_data['dqdv']:
        cost_terms.append('dqdv')
    if opt_data['dvdq']:
        cost_terms.append('dvdq')

    fitter.cost_terms = cost_terms

    fit_result = {}
    if trigger == 'grid-btn' and _c and all(flags.values()):
        fit_result = fitter.grid_search(opt_data['grid-Nx'])
        params = fit_result['x']
    elif trigger == 'min-err-btn' and _m and all(flags.values()):
        x0 = np.array(neg_s + pos_s)
        fit_result = fitter.constrained_fit(x0, **options)
        params = fit_result['x']
    else:
        params = np.array(neg_s + pos_s)

    optimal_params = params.copy()

    if fit_result:
        x = np.round(fit_result['x'], 2)
        neg_s, pos_s = list(x[0:2]), list(x[2:4])

    return '', neg_s, pos_s, fit_result


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    Input('theme-switch', 'value'),
    State('flags', 'data'),
    prevent_initial_call=True,
)
def toggle_theme_switch(switch_on, flags):

    if not all(flags.values()):
        return placeholder_fig

    bg_color = 'white' if switch_on else '#F5F5F5'

    figure.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
    )

    return figure


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    [
        Input('mk-cell', 'value'),
        Input('ms-cell', 'value'),
        Input('clr-cell', 'value'),
    ],
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_cell_styles(mk, ms, clr, flags):

    for i in range(0, 3):
        figure.data[i].marker.symbol = mk
        figure.data[i].marker.size = 6 + 2*(int(ms) - 1)
        figure.data[i].marker.color = clr

    if not all(flags.values()):
        return placeholder_fig

    return figure


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    [
        Input('ls-model', 'value'),
        Input('lw-model', 'value'),
        Input('clr-model', 'value'),
    ],
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_model_styles(ls, lw, clr, flags):

    for i in range(3, 6):
        figure.data[i].line.dash = ls
        figure.data[i].line.width = int(lw)
        figure.data[i].line.color = clr

    if not all(flags.values()):
        return placeholder_fig

    return figure


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    [
        Input('ls-pos', 'value'),
        Input('lw-pos', 'value'),
        Input('clr-pos', 'value'),
    ],
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_pos_styles(ls, lw, clr, flags):

    figure.data[6].line.dash = ls
    figure.data[6].line.width = int(lw)
    figure.data[6].line.color = clr

    if not all(flags.values()):
        return placeholder_fig

    return figure


@dash.callback(
    Output('figure-div', 'figure', allow_duplicate=True),
    [
        Input('ls-neg', 'value'),
        Input('lw-neg', 'value'),
        Input('clr-neg', 'value'),
    ],
    State('flags', 'data'),
    prevent_initial_call=True,
)
def update_neg_styles(ls, lw, clr, flags):

    figure.data[7].line.dash = ls
    figure.data[7].line.width = int(lw)
    figure.data[7].line.color = clr

    if not all(flags.values()):
        return placeholder_fig

    return figure
