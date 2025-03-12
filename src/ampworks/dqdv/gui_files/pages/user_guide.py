import dash
from dash import html

dash.register_page(__name__, path='/', title='User Guide')

layout = html.Div(
    "This is the User Guide.",
)
