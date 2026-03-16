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
            dbc.Card([
                dbc.CardHeader(html.H4("Observations of yearwise CCF Plot analysis")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
The CCF is different for every year, nevertheless it is possible to conclude, by looking at every year  
individually, that the **1st, 2nd and 3rd lag** are the most signifikant ones  
                        """
                    )
                ])
            ]),
            width=6
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
# NOW: Aggregaded data from 2014 to 2026:
### Cross-Correlation Analysis

To analyze how oil price changes relate to fuel prices, we again compute the cross-correlation function (CCF) between oil returns and fuel returns for lags $k = 0, \dots$,  
but now for all yeats combined (2014–2025) instead of only looking at one year individually.

So we again use:

$$\rho_k = \text{corr}(r_t^{fuel}, r_{t-k}^{oil})$$

where $r_t$ denotes the log-return of the respective price series.  

The resulting correlations are stored in a matrix with **years as rows** and **lags as columns**, which allows us to visualize the lag structure across years and to compute the average correlation.
                        """,
                        mathjax=True,
                    )
                ])
            ]),
            width=6
        )
    ]),
    html.Br(),
], fluid=True)
