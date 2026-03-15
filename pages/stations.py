import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.figures.station_figures import _FUEL_LABELS

dash.register_page(__name__, path="/stations")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(html.H1("Station Comparison", style={"textAlign": "center"}), width=12)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Label("Fuel"),
            dcc.Dropdown(
                id="fuel-dropdown",
                options=[{"label": label, "value": col} for col, label in _FUEL_LABELS.items()],
                value="diesel_mean",
                clearable=False
            )
        ], width=12),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="brand-comparison-graph"), width=12)
    ]),
], fluid=True)
