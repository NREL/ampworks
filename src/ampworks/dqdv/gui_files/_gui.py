import os
import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash_breakpoints import WindowBreakpoints
from dash import dcc, html, Output, Input, State
from dash_extensions.pages import setup_page_components

from ampworks.dqdv.gui_files.layout.navbar import navbar
from ampworks.dqdv.gui_files.layout.sidebar import sidebar

here = os.path.dirname(__file__)
pages_folder = os.path.join(here, 'pages')

dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/' \
    + 'dash-bootstrap-templates/dbc.min.css'

app = dash.Dash(
    __name__,
    use_pages=True,
    title='ampworks',
    pages_folder=pages_folder,
    external_stylesheets=[
        dbc_css,
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ],
)

breakpoints = WindowBreakpoints(
    id='breakpoints',
    widthBreakpointNames=['sm', 'lg'],
    widthBreakpointThresholdsPx=[1199],
)

dummy_block = html.Div(id='dummy-block', className='dummy-block')

main_page = html.Div(
    id='main-page',
    className='main-page mx-auto my-3',
    children=[dash.page_container, setup_page_components()],
)

dash_link = html.A(
    className='link',
    children='dash 2.18',
    href='https://dash.plotly.com/',
)

footer = html.Div(
    [
        html.Div('© Alliance for Sustainable Energy, LLC'),
        html.Div(['Created using ', dash_link], className='text-end'),
    ],
    id='footer',
    className='footer px-4',
)

grid_container = html.Div(
    id='grid-container',
    className='grid-container',
    children=[dummy_block, main_page, footer],
)

app.layout = html.Div(
    [
        dcc.Location(id='url'),
        breakpoints,
        navbar,
        sidebar,
        grid_container,
    ],
)

# Transform page on width breakpoint
app.clientside_callback(
    """
    function trasformPage(flag, width) {

        if (width < 1200) {
            return [false, false, {}, true, true, "Control Panel"];
        }

        sidebarStyle = {
            "top": "4em",
            "position": "fixed",
        };

        return [false, true, sidebarStyle, false, false, ""];
    }
    """,
    Output('navlinks-collapse', 'is_open', allow_duplicate=True),
    Output('sidebar', 'is_open', allow_duplicate=True),
    Output('sidebar', 'style'),
    Output('sidebar', 'backdrop'),
    Output('sidebar', 'close_button'),
    Output('sidebar', 'title'),
    Input('breakpoints', 'widthBreakpoint'),
    State('breakpoints', 'width'),
    prevent_initial_call=True,
)


def run(debug: bool = False) -> None:

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        webbrowser.open_new("http://127.0.0.1:8050/")

    app.run(
        debug=debug,
        dev_tools_silence_routes_logging=True,
    )
