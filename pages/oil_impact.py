import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from src.figures.anomaly_figures import plot_anomaly_rate_per_month, plot_top_stations_map

dash.register_page(__name__, path="/oil-impact")

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Jump to Section", className="py-2"),
                dbc.CardBody([
                    html.Div([
                        html.A(
                            dbc.Button(
                                "Aggregated Analysis",
                                color="primary",
                                className="mb-2 w-100"
                            ),
                            href="#aggregated-section"
                        ),
                        html.A(
                            dbc.Button(
                                "Asymmetry Test",
                                color="warning",
                                className="w-100"
                            ),
                            href="#asymmetry-section"
                        ),
                        html.A(
                            dbc.Button(
                                "Anomaly Analysis",
                                color="primary",
                                className="mt-2 w-100"
                            ),
                            href="#anomaly-section"
                        ),
                    ])
                ], className="py-2")
            ]),
            width=2
        ),
        dbc.Col(
            html.Div([
                html.H1(
                    "Oil Price Impact on Fuel Prices",
                    style={"textAlign": "center"}
                ),
                html.H4(
                    "(a yearwise overview)",
                    style={"textAlign": "center"}
                ),
            ]),
            width=8,
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flexDirection": "column"
            }
        ),
    ], align="center"),
    html.Br(),
    html.Br(),
    dbc.Row([ # Year Dropdown
        dbc.Col([
            html.Label("Year you want to analyze"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in range(2014, 2027)],
                value=2025,
                clearable=False,
                style={"color": "black"}
            )
        ], width=10),
        dbc.Col([
            dbc.Switch(
                id="show-oil-switch",
                label="Overlay Oil Price",
                value=False,
            )
        ], width=1)
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="national-fuel-prices-graph"),
            width=11
        )
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Explaining the CCF Plot and Log-Returns")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
### Using
Log-Return:
$$
r_t = \log(P_t) - \log(P_{t-1}) = \log\left(\frac{P_t}{P_{t-1}}\right)
$$
therefore we get approximate %-change (for smaller changes):
$$
r_t \approx \frac{P_t - P_{t-1}}{P_{t-1}}
$$
thus the process is now $\approx$ stationary.
Now you can use the Cross-Correlation-Function (CCF):
$$
\text{corr}(r_t^{fuel}, r_{t-k}^{oil})
$$
### Significance of Cross-Correlations
To determine whether a correlation is statistically significant we use an approximate **95\% confidence interval**.  
A lag $k$ is considered statistically significant if
$$
|\hat{\rho}_k| > \frac{1.96}{\sqrt{N}}
$$
In the CCF plot these thresholds appear as horizontal dashed lines.  
Any lag outside this band indicates a statistically significant relationship
between oil price changes and fuel price changes.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=12
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Diesel", className="bg-primary text-white"),
                dbc.CardBody([
                    dcc.Graph(id="diesel-ccf-graph-year")
                ])
            ]),
            width=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("E5", className="bg-primary text-white"),
                dbc.CardBody([
                    dcc.Graph(id="e5-ccf-graph-year")
                ])
            ]),
            width=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("E10", className="bg-primary text-white"),
                dbc.CardBody([
                    dcc.Graph(id="e10-ccf-graph-year")
                ])
            ]),
            width=4
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Alert(
                [
                    html.H4("Main Insight"),
                    html.P(
                        "Across all years, the first three lags show the strongest cross-correlations. "
                        "This suggests that fuel prices react to oil price changes within 1–3 days. "
                        "Nevertheless outlier can be observed, such as an insignificant lag at day 0 "
                        "or a significant one at day 8, but these are (here) viewed as noice, since the graphs overall show the consisten pattern."
                    )
                ],
                color="primary"
            ),
            width=8
        ),
    ], justify="center"),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col(
            html.H1("NOW: Combinded data from 2014 to 2026", style={"textAlign": "center"})
        )
    ], id="aggregated-section"),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Diesel", id="fuel-btn-diesel", n_clicks=0, color="primary", style={"width": "150px"}),
                dbc.Button("E5", id="fuel-btn-e5", n_clicks=0, color="primary", style={"width": "150px"}),
                dbc.Button("E10", id="fuel-btn-e10", n_clicks=0, color="primary", style={"width": "150px"})
            ], size="lg"),
        ], width="auto")
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.CardGroup([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Markdown(
                            r"""
    ### Cross-Correlation Analysis

    To analyze how oil price changes relate to fuel prices, we again compute the cross-correlation function (CCF) between oil returns and fuel returns for lags $k = 0, \dots$,  
    but now for all yeats combined (2014–2025) instead of only looking at one year individually.

    So we again use:

    $$\rho_k = \text{corr}(r_t^{fuel}, r_{t-k}^{oil})$$

    where $r_t$ denotes the log-return of the respective price series.  

                            """,
                            mathjax=True,
                        ),
                        html.Hr(),
                        dcc.Markdown(
                            r"""
### Lag Selection

The heatmap shows a consistent pattern across years with the strongest correlations occurring for lags $k = 1, 2, 3$.  
Beyond lag 3, the correlations become small and and therefore we choose a lag of 3 for our model.

Based on this, we select the maximum lag length of

$$K = 3$$

for our Regression model.
                            """,
                            mathjax=True,
                        )
                    ])
                ]),
                dbc.Card([
                    dbc.CardHeader("Cross-Correlation Analysis / Heatmap"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="ccf-heatmap-all",
                            )
                    ])
                ])
            ])
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
        ### Distributed Lag Model

        Using the selected lag structure, the relationship between oil and fuel returns is modeled as

        $$r_t^{fuel} = \alpha + \beta_0 r_t^{oil} + \beta_1 r_{t-1}^{oil} + \beta_2 r_{t-2}^{oil} + \beta_3 r_{t-3}^{oil} + \varepsilon_t$$

        where $r_t^{fuel}$ and $r_t^{oil}$ denote the log-returns of fuel and oil prices.  

        The coefficients $\beta_k$ measure the **pass-through**, i.e., the extent to which changes in oil prices are transmitted to fuel prices. In particular, $\beta_k$ captures how strongly an oil price change occurring $k$ days earlier affects the fuel price return today, thereby describing the delayed adjustment of fuel prices to oil price shocks.
                        """,
                        mathjax=True,
                    )
                ])
            ], className="border-primary")
        ], width=8)
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("R²"),
            html.H2(id="hac-r2"),
            dbc.Button("▼ Explanation", id="toggle-r2", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "R² measures the proportion of variation in fuel price returns explained by the included oil-return lags.",
                        className="mt-2 small"
                    ),
                    id="collapse-r2",
                    is_open=False
                )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("F-statistic"),
            html.H2(id="hac-fstat"),
            dbc.Button("▼ Explanation", id="toggle-fstat", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "The F-statistic tests whether all slope coefficients are jointly equal to zero.",
                        className="mt-2 small"
                    ),
                    id="collapse-fstat",
                    is_open=False
                )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Prob(F-statistic)"),
            html.H2(id="hac-fpval"),
            dbc.Button("▼ Explanation", id="toggle-fpval", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "This is the p-value of the overall F-test. A very small value indicates that the model is jointly significant.",
                        className="mt-2 small"
                    ),
                    id="collapse-fpval",
                    is_open=False
                )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Observations"),
            html.H2(id="hac-nobs"),
            dbc.Button("▼ Explanation", id="toggle-nobs", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "Observations gives the number of usable data points included in the regression after constructing returns and lags.",
                        className="mt-2 small"
                    ),
                    id="collapse-nobs",
                    is_open=False
                )
        ]), className="border-primary"), width=3),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("Intermediate Results", className="text-center")
        ], width=12)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            [
                dbc.Alert(
                    [
                        html.H5("Result 1 - Lag structure", className="alert-heading"),
                        html.P(
                            "Oil price changes transmit to fuel prices within a delay of roughly 1-3 days.",
                            className="mb-0",
                        ),
                    ],
                    color="primary",
                    className="w-100 flex-fill",
                ),
                dbc.Alert(
                    [
                        html.H5("Result 2 - Timing of the pass-through", className="alert-heading"),
                        html.P(
                            "The strongest pass-through occurs one day after the oil price change.",
                        ),
                        html.P(
                            "This suggests that fuel retailers adjust prices with a short delay.",
                            className="mb-0",
                        ),
                    ],
                    color="primary",
                    className="w-100 flex-fill mb-0",
                ),
            ],
            width=4,
            className="d-flex flex-column"
        ),
        dbc.Col(
            dbc.Alert(
                [
                    html.H5("Result 3 - Magnitude of the explained variation", className="alert-heading"),
                    html.P(
                        "The model explains around 10%-16% (depending on which fuel type you observe) "
                        "of the variation in fuel price returns.",
                    ),
                    html.P(
                        "While this may appear small at first, it is economically meaningful given that a "
                        "large share of retail fuel prices consists of fixed taxes and duties (roughly 60%), "
                        "which do not respond to oil price changes.",
                    ),
                    html.P(
                        "The regression therefore captures a substantial part of the variable component of fuel prices.",
                        className="mb-0",
                    ),
                ],
                color="primary",
                className="w-100 h-100 mb-0",
            ),
            width=4,
            className="d-flex"
        ),
        dbc.Col(
            dbc.Alert(
                [
                    html.H5("Result 4 - Stronger response for diesel", className="alert-heading"),
                    html.P(
                        "The estimated coefficients indicate that diesel prices react more strongly to oil "
                        "price changes than gasoline prices.",
                    ),
                    html.P(
                        "This pattern is also consistent with historical market observations.",
                    ),
                    html.P(
                        "Periods of supply disruptions or geopolitical shocks often amplify this effect.",
                    ),
                    html.P(
                        "For example, during the early phase of the Ukraine war and again during recent "
                        "Middle East tensions, diesel prices increased more strongly than gasoline prices, "
                        "sometimes even exceeding gasoline prices.",
                    ),
                    html.P(
                        "This phenomenon is analyzed in more detail in Research Question 5, which examines "
                        "structural differences between fuel types.",
                        className="mb-0",
                    ),
                ],
                color="primary",
                className="w-100 h-100 mb-0",
            ),
            width=4,
            className="d-flex"
        )
    ], className="align-items-stretch"),
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H1("Testing: Asymmetric pass-through of oil price changes", style={"textAlign": "center"}),
            html.P("Do Fuel Prices behave the same by rising and falling Oil Prices?", style={"textAlign": "center"})
        ])
    ], id="asymmetry-section"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("The math behind it", style={"textAlign": "center"})),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
In the previous section, we estimated a distributed lag model assuming that **oil price increases and decreases affect fuel prices symmetrically**.  
However, it might be interesting to quantify if there are asymmetries in the oil price fluctuations.

This refers, for example, to the observation that fuel prices tend to **increase rapidly when oil prices rise**, but **decrease more slowly when oil prices fall**.

To test this, oil price returns are seperated into **positive and negative components**:

$$
r^{oil,+}_t = \max(r^{oil}_t, 0), \qquad r^{oil,-}_t = \min(r^{oil}_t, 0)
$$

Lagged versions of both components are then included in the regression model:

$$
r_t^{fuel} = \alpha + \sum_{k=0}^{3} \beta_k^{+} r_{t-k}^{oil,+} + \sum_{k=0}^{3} \beta_k^{-} r_{t-k}^{oil,-} + \varepsilon_t
$$

This specification allows **positive and negative oil price changes to have different effects** on fuel price adjustments.

To formally test whether the responses differ, a **Hypothesis Test (Wald)** is conducted with the hypothesis being:

$$
H_0: \beta_k^{+} = \beta_k^{-} \quad \forall k \qquad \text{vs.} \qquad H_1: \beta_k^{+} \neq \beta_k^{-} \quad \text{for at least one } k \qquad \text{with} \qquad \alpha = 0.05
$$

Rejecting $H_0$ implies that **positive and negative oil price changes have statistically different effects on fuel prices**.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=10
        )
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("R²"),
            html.H2(id="hac-r2-asym"),
            dbc.Button("▼ Explanation", id="toggle-r2-asym", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "R² measures the proportion of variation in fuel price returns explained by the included oil-return lags.",
                        className="mt-2 small"
                    ),
                    id="collapse-r2-asym",
                    is_open=False
                )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("F-statistic"),
            html.H2(id="hac-fstat-asym"),
            dbc.Button("▼ Explanation", id="toggle-fstat-asym", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "The F-statistic tests whether all slope coefficients are jointly equal to zero.",
                        className="mt-2 small"
                    ),
                    id="collapse-fstat-asym",
                    is_open=False
                )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Prob(F-statistic)"),
            html.H2(id="hac-fpval-asym"),
            dbc.Button("▼ Explanation", id="toggle-fpval-asym", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "This is the p-value of the overall F-test. A very small value indicates that the model is jointly significant.",
                        className="mt-2 small"
                    ),
                    id="collapse-fpval-asym",
                    is_open=False
                )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Observations"),
            html.H2(id="hac-nobs-asym"),
            dbc.Button("▼ Explanation", id="toggle-nobs-asym", color="primary", className="p-0 mt-2"),
                dbc.Collapse(
                    html.Div(
                        "Observations gives the number of usable data points included in the regression after constructing returns and lags.",
                        className="mt-2 small"
                    ),
                    id="collapse-nobs-asym",
                    is_open=False
                )
        ]), className="border-primary"), width=3),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Wald F-statistic"),
                    html.H2(id="wald-f-asym")
                ]), className="border-primary"
            ),
            width=3
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Wald p-value"),
                    html.H2(id="wald-p-asym")
                ]), className="border-primary"
            ),
            width=3
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Conclusion"),
                    html.H2(id="wald-decision-asym")
                ]), className="border-primary"
            ),
            width=3
        ),
        dbc.Col(
            dbc.Alert(id="wald-interpretation-asym", color="primary"),
            width=3
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Positive vs. Negative Oil Price Effects by Lag"),
                    dbc.CardBody([
                        dcc.Graph(id="asym-lag-effects-graph")
                    ])
                ],
                className="w-100 h-100",
            ),
            width=4,
            className="d-flex"
        ),
        dbc.Col(
            dbc.Alert(
                dcc.Markdown(
                    """
### Results of the asymmetry analysis

The hypothesis test rejects the null hypothesis of symmetric transmission, indicating that **positive and negative oil price changes lead to different adjustment patterns in fuel prices**.

The figure above visualizes the lagged coefficients for oil price increases and decreases. Interestingly, the adjustment pattern does not follow a simple structure across all lags. While differences between the responses are visible, the strongest effects occur with a short delay rather than immediately (already seen before).

From an economic perspective, one might expect fuel prices to **increase rapidly when oil prices rise but decrease more slowly when oil prices fall**, since retailers may try to maintain higher margins when costs decline.

However, the estimated lag structure suggests a more complex dynamic adjustment process, where the timing and magnitude of the response differ across lags rather than showing a simple immediate asymmetry.
                    """
                ),
                color="primary",
                className="w-100 h-100 mb-0",
            ),
            width=4,
            className="d-flex"
        )
    ], justify="center", className="align-items-stretch"),
    html.Br(),
    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.H1("When and why is Diesel more expensive than E10", style={"textAlign": "center"}),
        ])
    ], id="anomaly-section"),
    html.Br(),

    dbc.Row([
        dbc.Col(
            dcc.Graph(figure=plot_anomaly_rate_per_month(), style={"height": "400px"}),
            width=6
        ),
        dbc.Col([
            html.Label("Year you want to analyze"),
            dcc.Dropdown(
                id="year-dropdown-hourly",
                options=[{"label": str(y), "value": y} for y in range(2021, 2027)],
                value=2024,
                clearable=False,
                style={"color": "black"}
            ),
            dcc.Graph(id="anomaly-rate-by-hour-graph", style={"height": "340px"}),
        ], width=6),
    ]),
    html.Br(),

        dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Explanation")),
                dbc.CardBody([
                    html.P(
                    """
                    The first plot shows the monthly anomaly rate from 2021 to 2026, where anomalies are defined as situations in which diesel prices are greater than or equal to E10 prices. We start in 2021 because before that it was really uncommon for Diesel to be more expensive than E10 (~2-4%). A sharp increase can be observed in 2022, where the anomaly rate rises to extremely high levels, in some months approaching 100%. After this peak, the anomaly rate drops significantly in 2023 and remains relatively low, with only smaller temporary increases in later periods."),
                    The second plot illustrates the anomaly rate by hour of the day for 2022. The anomaly rate remains consistently high throughout all hours, with only minor fluctuations. This indicates that the phenomenon is not tied to specific times of day
                    The third plot displays the top 100 gas stations with the highest anomaly rates on a map. The stations are not evenly distributed but appear to be geographically clustered, with a noticeable concentration in Eastern Germany
                    """
                           ),
                    dbc.Alert([
                        html.H4("Analysis"),
                        html.P(
                        """
                        The strong spike in anomaly rates during 2022 and the start of a similar spike in 2026 aligns with the period of sharply increasing global oil prices. As previously established, diesel prices react more strongly to oil price changes than gasoline prices. This amplified response led to diesel prices exceeding E10 prices much more frequently, which explains the dramatic increase in anomalies during this period
                        The hourly distribution of 2022 confirms that this effect is structural rather than behavioral. Since anomaly rates remain around 80%" across all hours of the day, the phenomenon cannot be attributed to intra-day pricing strategies or timing of price updates. Instead, it reflects a persistent shift in relative price levels driven by external market conditions
                        The geographic clustering of high-anomaly stations suggests that regional factors also play a role. Differences in supply infrastructure, competition intensity, and regional demand—particularly for diesel—may have amplified the effect in certain areas, especially in Eastern Germany
                        Overall, the results indicate that the anomalies are a direct consequence of diesel's stronger sensitivity to oil price shocks. The 2022 energy crisis did not only increase prices in general but also created a structural imbalance between fuel types, which became visible through the sharp rise in anomaly rates.
                        """
                        ),
                    ], color="primary"),
                ]),
            ]),
            width=6
        ),
        dbc.Col(
            dcc.Graph(figure=plot_top_stations_map()),
            width=6
        ),
    ]),
    html.Br(),
    html.Br(),
], fluid=True)
