import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.figures.station_figures import _FUEL_LABELS, plot_brand_vs_free_prices

dash.register_page(__name__, path="/stations")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(html.H1("Station Comparison", style={"textAlign": "center"}), width=12)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.RadioItems(
                id="fuel-buttons",
                options=[{"label": label, "value": col} for col, label in _FUEL_LABELS.items()],
                value="diesel_mean",
                inline=True,
                input_class_name="btn-check",
                label_class_name="btn btn-outline-primary",
                label_checked_class_name="active",
            )
        ], width=12, class_name="d-flex justify-content-center"),
    ]),
    html.Br(),

    html.P("Mean fuel prices: Brand vs. Free gas stations"),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=plot_brand_vs_free_prices()), width=11)
    ], justify="center"),

    html.Br(),
    
    html.P("A comparison of selected brands with the mean Price of Diesel, E10 or E5 over the years 2014-2025"),
    dbc.Row([
        dbc.Col(dcc.Graph(id="brand-comparison-graph"), width=11)
    ], justify="center"),
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
You can see that ARAL is the most expensive brand gas station consistently over the years.
In addition, some brands are actually cheaper than the average free gas stations.
In the following Plot you'll see how much the price difference actually is:
"""
                    )
                ])
            ])
        )
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(html.H1("How much more expensive are the brands?", style={"textAlign": "center"}), width=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="avg-premium-graph"), width=11)
    ], justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
You can see that Aral, the biggest brand in germany (=most gas stations), is in average 3 cents more expensive than
the average price of free gas stations. Interesting to see that some brands (e.g. OIL!, Star, HEM) are actually cheaper than
the average free gas station.
"""
                    )
                ])
            ])
        )
    ]),
], fluid=True)
