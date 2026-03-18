import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/competition")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H1("Other Effects on Fuel Prices", className="text-center"),
        ])
    ]),
        dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Other Effects that affect the fuel prices")),
                dbc.CardBody([
                    html.P(
                        "-Highway Gas Stations \n -Proximity to other stations \n -Regional based Differences \n -Extreme Weather",
                        style={"whiteSpace": "pre-line"})
                ])
            ]),
            width=12
        )
    ]),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("The increasing Price differences of Highway, to normal Stations", className="text-center"),
        ])
    ]),


    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("The effect of proximity to other stations on the average price", className="text-center"),
        ])
    ]),
    dbc.Row([  # Cluster Dropdown
        dbc.Col([
            html.Label("What clustering of the stations do you want to see?", className="text-center"),
            dcc.Dropdown(
                id="Cluster_Dropdown",
                options=[{"label": "Cluster 1", "value": 1}, {"label": "Cluster 2", "value": 2}],
                value=1,
                clearable=False,
                style={"color": "black"}
            )
        ], width=10),
    ], justify="center"),


    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("Regional based Differences", className="text-center"),
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("Extreme Weather conditions", className="text-center"),
        ])
    ]),
])