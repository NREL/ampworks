import dash
from dash import dcc, html, Output, Input, State

dash.register_page(__name__, path='/', title='User Guide')

layout = html.Div(
    "This is the User Guide.",
)