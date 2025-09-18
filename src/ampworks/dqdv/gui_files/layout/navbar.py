import dash_bootstrap_components as dbc

from dash import html, Output, Input, State, clientside_callback

# Branding
PLOTLY_LOGO = 'https://images.plot.ly/logo/new-branding/plotly-logomark.png'

brand_logo = html.Div(
    [
        html.Img(src=PLOTLY_LOGO, height='30px'),
        html.P(children='Logo', className='mx-3 my-auto',
               style={'fontSize': '1.75em', 'fontWeight': 'bold'}),
    ],
    style={'height': '4em'},
    className='d-flex align-items-center',
)

# Buttons/switches
sidebar_btn = dbc.Button(
    id='sidebar-btn',
    class_name='nav-btn ms-3 me-2',
    children=html.I(className='fa fa-bars'),
)

theme_btn = dbc.Button(
    id='theme-btn',
    class_name='nav-btn',
    children=html.I(id='theme-btn-icon', className='fa fa-sun'),
)

theme_switch = html.Div(
    [
        html.I(className='fa fa-lg fa-moon'),
        dbc.Switch(id='theme-switch', value=True, class_name='ms-2'),
        html.I(className='fa fa-lg fa-sun'),
    ],
    className='d-flex justify-content-end align-items-center',
)

navbar_btn = dbc.Button(
    id='navbar-btn',
    class_name='nav-btn me-3',
    children=html.I(className='fa fa-ellipsis-vertical'),
)

# Page links
user_guide = dbc.NavLink(
    href='/',
    active='exact',
    children='User Guide',
)

dvq_analysis = dbc.NavLink(
    active='exact',
    href='/dqv-analysis',
    children='DVQ Analysis',
    class_name='nav-link-bottom',
)

navlinks = dbc.Nav(
    [
        user_guide,
        dvq_analysis,
    ],
)

# Full navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Stack(
                className='sm-only',
                direction='horizontal',
                children=[sidebar_btn, brand_logo],
            ),
            html.Div([brand_logo], className='lg-only ps-4 w-400px'),
            html.Div([theme_btn, navbar_btn], className='sm-only'),
            dbc.Collapse(
                navbar=True,
                is_open=False,
                children=navlinks,
                id='navlinks-collapse',
                class_name='navlinks-collapse mx-2',
            ),
            html.Div([theme_switch], className='lg-only ms-auto pe-4'),
        ],
        fluid=True,
        class_name='p-0 d-flex align-items-center',
    ),
    id='navbar',
    fixed='top',
    expand='xl',
    class_name='p-0 header',
)

# Toggle navbar when small
clientside_callback(
    """
    function toggleNavCollapse(nClick, isOpen) {
        return !isOpen;
    }
    """,
    Output('navlinks-collapse', 'is_open'),
    Input('navbar-btn', 'n_clicks'),
    State('navlinks-collapse', 'is_open'),
    prevent_initial_call=True,
)

# Change theme - switch (light vs. dark)
clientside_callback(
    """
    function themeSwitch(switchOn) {
        document.documentElement.setAttribute(
            "data-bs-theme", switchOn ? "light" : "dark",
        );
        return window.dash_clientside.no_update;
    }
    """,
    Output('theme-switch', 'id'),
    Input('theme-switch', 'value'),
)

# Change theme - button (light vs. dark)
clientside_callback(
    """
    function themeButton(click, themeSwitch) {
        return !themeSwitch;
    }
    """,
    Output('theme-switch', 'value'),
    Input('theme-btn', 'n_clicks'),
    State('theme-switch', 'value'),
    prevent_initial_call=True,
)
