import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/fuel-up")

layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(),
                    md=3,
                ),
                dbc.Col(
                    html.H1("When to fuel up?", className="text-center mb-0"),
                    md=6,
                ),
                dbc.Col(
                    dbc.Alert(
                        "Due to data size and performance constraints, this analysis is based on a reduced dataset covering only Northern Germany (postal codes starting with 1 and 2) and the month of February 2026.",
                        color="warning",
                        className="mb-0 py-2",
                    ),
                    md=3,
                ),
            ],
            className="align-items-center g-2",
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P(
                                    "This dashboard shows how far fuel prices are above the daily "
                                    "minimum depending on hour of day and weekday for Northern Germany "
                                    "(postal codes starting with 1 or 2), based on February 2026 "
                                    "price observations.",
                                    className="mb-0", style={"textAlign": "center"}
                                )
                            ]
                        ), color="primary", outline=True,
                    ),
                    width=10,
                )
            ], justify="center",
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Filters"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Label("Fuel type"),
                                                    dcc.Dropdown(
                                                        id="fuel-up-fuel-dropdown",
                                                        options=[
                                                            {"label": "Diesel", "value": "diesel"},
                                                            {"label": "E5", "value": "e5"},
                                                            {"label": "E10", "value": "e10"},
                                                        ],
                                                        value="diesel",
                                                        clearable=False,
                                                        style={"color": "black"},
                                                    ),
                                                ],
                                                md=3,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label("City"),
                                                    dbc.Input(
                                                        id="fuel-up-city-input",
                                                        type="text",
                                                        placeholder="e.g. hamburg",
                                                    ),
                                                ],
                                                md=3,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label("Brand"),
                                                    dbc.Input(
                                                        id="fuel-up-brand-input",
                                                        type="text",
                                                        placeholder="e.g. aral",
                                                    ),
                                                ],
                                                md=3,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Label("PLZ prefix"),
                                                    dbc.Input(
                                                        id="fuel-up-plz-input",
                                                        type="text",
                                                        placeholder="e.g. 20",
                                                    ),
                                                ],
                                                md=3,
                                            ),
                                        ],
                                        className="g-3",
                                    )
                                ]
                            ),
                        ]
                    ),
                    width=12,
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Average distance to daily minimum by hour"),
                            dbc.CardBody(dcc.Graph(id="fuel-up-hour-graph")),
                        ]
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Weekday \u00d7 Hour"),
                            dbc.CardBody(dcc.Graph(id="fuel-up-heatmap-graph")),
                        ]
                    ),
                    lg=6,
                ),
            ],
            className="g-3",
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Summary"), style={"textAlign": "center"}),
                            dbc.CardBody(html.Div(id="fuel-up-summary", style={"textAlign": "center"})),
                        ], color="primary", outline=True,
                    ),
                    width=6,
                )
            ], justify="center",
        ),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("How its calculated", style={"textAlign": "center"}),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
### Intraday Fuel Price Cycle (Normalized)

To make fuel prices comparable across different gas stations, prices are normalized relative to each station’s **daily minimum price**:

$$
P^{norm}_t = P_t - P^{min}_{station, day}
$$

where $P^{min}_{station, day}$ is the lowest observed price of a specific station on a given day.

This removes differences in absolute price levels between stations and focuses on **intra-day price dynamics**.

The normalized values are then averaged across all observations by **hour of the day** ($h$) and **weekday** ($d$):

$$
\bar{P}_{h,d} = \frac{1}{N_{h,d}} \sum P^{norm}_{h,d}
$$

The y-axis therefore represents the **average deviation from the daily minimum price** in ct/L.  
Higher values indicate less favorable (more expensive) times to refuel, while lower values indicate times closer to the daily price minimum.
                        """,
                        mathjax=True,
                    )
                ])
            ])
        ], width=7),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Post Code - (Leitregion)", style={"textAlign": "center"}),
                dbc.CardBody([
                    html.Img(
                        src=dash.get_asset_url("plz_leitregionen.png"),
                        style={
                            "width": "100%",
                            "height": "500px",
                            "objectFit": "contain",
                        }
                    )
                ])
            ])
        ], width=5)
    ]),
    html.Br(),
    html.Hr(),
    ],fluid=True,
)
