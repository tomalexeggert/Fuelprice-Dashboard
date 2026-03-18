import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.figures.station_figures import _FUEL_LABELS, plot_brand_vs_free_prices

dash.register_page(__name__, path="/stations")

layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col(html.H1("Brand gas stations vs. free gas stations", style={"textAlign": "center"}), width=12)
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
On this page you can see a comparison between branded gas stations and independent (free) gas stations
based on their average fuel prices over time.
The main purpose of the page is to allow users to explore long-term pricing differences between
the two station types across different fuel categories.
"""
                    )
                ])
            ])
        )
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                html.P("""
                In the following three plots, the mean fuel prices of brand gas stations and independent (free)
                gas stations are compared over time for three different fuel types: Diesel, E5, and E10.
                Each plot represents the average annual price from 2014 to 2025:
                """),
                )
            ]),
            width=10
        )
    ], justify="center"),
    html.Br(),
    
    dbc.Row([
        dbc.Col(dcc.Graph(figure=plot_brand_vs_free_prices()), width=11)
    ], justify="center"),
    html.Br(),
    
    dbc.Row([
        dbc.Col(
            dbc.Alert([
                html.P("""Across all three fuel types, the overall price trends follow a very similar pattern.
                A key observation across all three plots is that brand gas stations are consistently slightly more expensive than free gas stations.
                In every fuel category, the line representing brand stations lies marginally above the line representing free stations.
                Although the price differences are generally small, the pattern is consistent across Diesel, E5, and E10 throughout the entire time period.
                """)
            ], color="primary"),
            width=8
        )
    ], justify="center"),

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
    
    dbc.Card([
        dbc.CardHeader(html.H4("Brand Comparison")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Graph(id="brand-comparison-graph"), width=11)
            ], justify="center"),

            html.Br(),

            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.P(
                                "The line chart shows the development of mean annual Diesel prices for selected branded gas stations "
                                "compared to the average price of free (independent) stations between 2014 and 2025. Each line represents "
                                "one brand, enabling a direct comparison of price levels and trends over time. Using the legend on the right, "
                                "individual brands can be selected or deselected, allowing users to focus on specific brands and compare them "
                                "directly with each other as well as with the average price of free stations."
                            )
                        )
                    ),
                    width=5
                ),
                dbc.Col(
                    dbc.Alert(
                        html.P(
                            "The chart shows that while price differences between brands exist, all brands follow a very similar overall trend "
                            "driven by market-wide developments. ARAL consistently appears among the more expensive brands throughout the observed "
                            "period, whereas some other brands occasionally price closer to or slightly below the average level of free stations. "
                            "The most notable feature is the sharp price increase around 2022, which affects all brands in a similar way. Overall, "
                            "the relatively small gaps between the lines indicate that differences between brands are limited and that fuel pricing "
                            "is largely determined by broader market conditions rather than brand-specific strategies."
                        ),
                        color="primary"
                    ),
                    width=5
                ),
            ], justify="center"),
        ])
    ], className="mb-3"),

    html.Br(),
    
    dbc.Card([
        dbc.CardHeader(html.H4("Which brands should you avoid?")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.Graph(id="avg-premium-graph"), width=11)
            ], justify="center"),

            html.Br(),

            dbc.Row([
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.P(
                                "The bar chart displays the average price difference between individual branded gas stations "
                                "and the average price of free (independent) stations for Diesel. Each bar represents one brand, "
                                "with values measured in cents per liter. Positive values indicate that a brand charges higher prices "
                                "than the average free station, while negative values indicate lower prices. The brands are ordered by "
                                "their price difference, allowing for a clear comparison across all stations."
                            )
                        )
                    ),
                    width=5
                ),
                dbc.Col(
                    dbc.Alert(
                        html.P(
                            "The results show that most large brands tend to charge slightly higher prices than free gas stations. "
                            "ARAL exhibits the largest price premium, averaging around 3 cents per liter above the free station average. "
                            "Other major brands such as OMV, Shell, AGIP, and Esso also price above the market average, although the differences are smaller. "
                            "In contrast, several smaller brands, including OIL!, Star, and HEM, appear to offer slightly lower prices than free stations. "
                            "Overall, the differences remain relatively small, indicating that while branded stations are generally more expensive, "
                            "the fuel market remains highly competitive."
                        ),
                        color="primary"
                    ),
                    width=5
                ),
            ], justify="center"),
        ])
    ], className="mb-3"),
], fluid=True)
