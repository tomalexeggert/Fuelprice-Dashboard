import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/oil-impact")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(
            html.H1("Oil Price Impact", style={"textAlign": "center"}),
            width=12
        )
    ]),
    html.Br(),
    dbc.Row([ # Year Dropdown
        dbc.Col([
            html.Label("Year"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in range(2014, 2027)],
                value=2025,
                clearable=False
            )
        ], width=12),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="national-fuel-prices-graph"),
            width=12
        )
    ])
], fluid=True)