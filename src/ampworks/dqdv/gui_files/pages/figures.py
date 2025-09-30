import plotly.graph_objs as go

from dash import dcc
from plotly.subplots import make_subplots

placeholder_fig = go.Figure()

placeholder_fig.update_layout(
    uirevision='constant',
    plot_bgcolor='lightgrey',
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    paper_bgcolor='rgba(0, 0, 0, 0)',
    margin=dict(l=20, r=20, t=20, b=20),
)

placeholder_fig.add_annotation(
    align='center', showarrow=False,
    font=dict(size=20, color='black'),
    text='Upload data to populate figure',
    xref='paper', yref='paper', x=0.5, y=0.5,
)

figure = make_subplots(1, 3)

figure.update_layout(
    uirevision='constant',
    font=dict(color='#212529'),
    margin=dict(l=20, r=20, t=20, b=60),
    plot_bgcolor='white', paper_bgcolor='white',
)

y_labels = ['Voltage [V]', 'dsoc/dV [1/V]', 'dV/dsoc [V]']

for i in range(3):
    figure.update_xaxes(
        row=1, col=i+1, showgrid=False,
        ticks='inside', tickcolor='#212529',
        mirror='allticks', title_text='SOC [-]',
        showline=True, linewidth=1, linecolor='#212529',
    )
    figure.update_yaxes(
        row=1, col=i+1, showgrid=False,
        ticks='inside', tickcolor='#212529',
        mirror='allticks', title_text=y_labels[i],
        showline=True, linewidth=1, linecolor='#212529',
    )

figure_div = dcc.Graph(
    id='figure-div',
    responsive=True,
    figure=placeholder_fig,
    style={'height': '370px', 'width': '100%'},
    config={
        'scrollZoom': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    },
)
