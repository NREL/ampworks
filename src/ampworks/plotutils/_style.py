import plotly.graph_objects as go


PLOTLY_TEMPLATE = go.layout.Template(
    layout=dict(
        dragmode='pan',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial', size=12, color='#212529'),
        xaxis=dict(
            showline=True, linecolor='#212529', title_standoff=7,
            mirror='all', ticks='inside', tickcolor='#212529',
            minor=dict(
                ticklen=2,
                ticks='inside',
            ),
        ),
        yaxis=dict(
            showline=True, linecolor='#212529', title_standoff=7,
            mirror='all', ticks='inside', tickcolor='#212529',
            minor=dict(
                ticklen=2,
                ticks='inside',
            ),
        ),
        legend=dict(
            orientation='h',
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)',
            entrywidth=0.125, entrywidthmode='fraction',
            xanchor='center', x=0.5, yanchor='top', y=1.15,
        )
    )
)

PLOTLY_CONFIG = {
    'scrollZoom': True,
    'responsive': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
}
