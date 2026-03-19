import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

left_rq_items = [
    dbc.AccordionItem(
        title="RQ1: Intraday Patterns in Fuel Prices",
        children=html.Ul([
            html.Li("How fuel prices vary throughout the day (morning vs. evening patterns)"),
            html.Li("Differences between weekdays, weekends, and holidays"),
            html.Li("Typical daily price range (difference between daily minimum and maximum)"),
            html.Li("Identification of stations with unusually high price volatility"),
        ]),
    ),
    dbc.AccordionItem(
        title="RQ2: Speed of Fuel Price Adjustment to Oil Price Changes",
        children=html.Ul([
            html.Li("Do fuel prices react immediately or with a delay to oil price movements?"),
            html.Li("Correlation analysis between oil and fuel prices across different time lags"),
            html.Li("Regression models with lagged oil price variables"),
            html.Li("Asymmetry analysis: do prices increase faster than they decrease (\"rockets and feathers\" effect)?"),
        ]),
    ),
    dbc.AccordionItem(
        title="RQ3: Influence of special location factors on price differences and their stability",
        children=html.Ul([
            html.Li("Comparison of fuel prices in Germanys border regions"),
            html.Li("Differences in pricing and  volatility at Autobahn gas stations"),
        ]),
    ),
    dbc.AccordionItem(
        title="RQ4: Price Differences Between Brand and Non-Brand Gas Stations",
        children=html.Ul([
            html.Li("Are branded gas stations systematically more expensive than independent ones?"),
            html.Li("Controlling for confounding factors such as highway locations"),
            html.Li("Hypothesis testing to determine statistical significance of price differences"),
            html.Li("Analysis of regional variation in brand-related pricing effects"),
        ]),
    ),
]

right_rq_items = [
    dbc.AccordionItem(
        title="RQ5: Diesel vs. E10 Price Anomalies",
        children=html.Ul([
            html.Li("Frequency of anomalies where diesel prices exceed E10 prices"),
            html.Li("Identification of temporal patterns (e.g., during specific events or crises)"),
            html.Li("Exploration of possible causes (e.g., geopolitical events, supply shocks)"),
            html.Li("Creation of a dataset capturing when, where, and how long anomalies occur"),
            html.Li("Spatial analysis (e.g., mapping top anomaly locations, urban vs. rural differences)"),
        ]),
    ),
    dbc.AccordionItem(
        title="RQ6: Predicting the Optimal Weekly Refueling Time",
        children=html.Ul([
            html.Li("Identification of the cheapest time window to refuel within a week"),
            html.Li("Use of historical price patterns to generate actionable recommendations"),
            html.Li("Estimation of potential savings compared to worst-case refueling times"),
            html.Li("Development of a simple decision-support system for users"),
        ]),
    ),
    dbc.AccordionItem(
        title="RQ7: Impact of Proximity to other Stations on Fuel Prices",
        children=html.Ul([
            html.Li("Do areas with multiple nearby gas stations exhibit lower prices?"),
            html.Li("Analysis of price differences between clustered and isolated stations"),
            html.Li("Is commpetition really the only factor affecting the price of close Stations?"),
            html.Li("Identification of trends (e.g., increasing or decreasing proximity effects)"),
        ]),
    ),
    dbc.AccordionItem(
        title="RQ8: Impact of Extreme Weather Events on Fuel Prices",
        children=html.Ul([
            html.Li("Do extreme weather event such as storms influence the volatility of gas prices?"),
        ]),
    ),
]

layout = dbc.Container([
    html.Br(),

    dbc.Row([
        dbc.Col(
            html.H1(
                "Fuel Price Dashboard",
                style={
                    "textAlign": "center",
                    "fontWeight": "600",
                    "marginBottom": "20px"
                }
            ),
            width=12
        )
    ]),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("Introduction + Fun Facts", style={"textAlign": "center", "marginBottom": "20px"}),

                    html.P(
                        "Fuel prices in Germany affect a large share of the population, as many people rely on their cars for commuting and everyday life.",
                        style={"textAlign": "justify"}
                    ),

                    html.P(
                        "According to DESTATIS, the average person travels about 15.5 km per day by car. Recent geopolitical events have shown how quickly fuel prices can change.",
                        style={"textAlign": "justify"}
                    ),

                    html.P(
                        "We analyze fuel prices across Germany and investigate the key factors driving their variation.",
                        style={"textAlign": "justify"}
                    ),

                ]),
                style={
                    "maxWidth": "900px",
                    "margin": "0 auto",
                    "borderRadius": "15px",
                    "boxShadow": "0 4px 20px rgba(0,0,0,0.2)"
                }
            ),
            width=12
        )
    ]),
    html.Br(),
    dcc.Interval(
        id="counter-interval",
        interval=30,
        n_intervals=0,
        max_intervals=80,
    ),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Fuel Stations Total"),
            html.H2(id="stations-total", children="0"),
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Raw data Repo size"),
            html.H2(id="repo-size", children="0 GB"),
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("appr. Rows in our data"),
            html.H2(id="rows-total", children="0"),
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Price changes per day"),
            html.H2(id="price-changes", children="0"),
        ]), className="border-primary"), width=3),
    ]),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Our research questions", style={"textAlign": "center"}),
                ]),
                color="primary",
                inverse=True,
                style={
                    "width": "400px",
                    "margin": "0 auto",
                    "borderRadius": "15px"
                }
            ),
            width="auto"
        )
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dbc.Accordion(left_rq_items, start_collapsed=True)
                ),
            ),
            width=6
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dbc.Accordion(right_rq_items, start_collapsed=True)
                ),
            ),
            width=6
        )
    ])
], fluid=True)