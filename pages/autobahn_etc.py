import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

from src.figures.autobahn_figures import show_median_price_heatmap_per_region, plot_autobahn_premium_barchart, plot_border_stations, get_country_options

dash.register_page(__name__, path="/other-effects")

#for border stations country dropdown.
country_options = get_country_options()
default_country = country_options[0]["value"] if country_options else None


layout = dbc.Container([
    html.Div(id="other-effects-top"),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H1("Other Effects on Fuel Prices", className="text-center"),
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dbc.Alert([
                        
                        html.P(
                            """As we can see in the map below, the fuel prices in Germany differ from region to region and over time. 
                            This map plots the development of monthly median prices of a selected fuel type and year for each post code 'Leitregion'. 
                            On this page, we will have a look at the autobahn gas stations to see how much more expensive they are and if their prices have a different volatility compared to normal gas stations. 
                            After that, we will see if competition with other gas stations in the direct vicinity has an impact of the prices.
                            We also take a look into the German border regions and see if the prices in these regions differ from prices in comparable non-border regions.
                            At the end of this page, we'll test if extreme weather events such as storms influence the fuel prices."""
                        )
                        ],
                        color="secondary",
                        className="mb-3"
                    ),
                ])
            ])
        )
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Diesel median prices for the post code 'Leitregionen' over the months of 2025"),
                dbc.CardBody([
                    dcc.Graph(
                        id="diesel-median-region-map",
                        figure=show_median_price_heatmap_per_region(),
                        config={"responsive": True},
                        style={"height": "1000px", "width": "100%"}
                    )
                ])
            ]),
            width=6
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Leitregionen"),
                dbc.CardBody([
                    html.Img(
                        src=dash.get_asset_url("plz_leitregionen.png"),
                        style={
                            "width": "100%",
                            "height": "1000px",
                            "objectFit": "contain",
                        }
                    )
                ])
            ]),
            width=6
        )
    ], className="g-3"),

    html.Br(),
   
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Other Effects that affect the fuel prices")),
                dbc.CardBody([
                    html.Div([
                        html.Div(html.A("Autobahn gas stations", href="#autobahn-section")),
                        html.Div(html.A("Proximity to other stations", href="#proximity-section")),
                        html.Div(html.A("Border Region Differences", href="#border-section")),
                        html.Div(html.A("Extreme Weather", href="#weather-section")),
                    ], className="d-flex flex-column gap-2")
                ])
            ]),
            width=12
        )
    ]),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("How much more expensive are Autobahn gas stations really?", className="text-center"),
        ]),
        dbc.Col(
            html.A(
                dbc.Button("Back to top", color="primary", size="sm"),
                href="#other-effects-top"
            ),
            width=2,
            style={"display": "flex", "justifyContent": "flex-end"}
        )
        
    ], id="autobahn-section"),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Autobahn premium panel regression")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
The next part of the questions looks for the price differences between autobahn stations and regular stations. 

For that we use a matched panel regression that examines whether Autobahn stations have systematically higher fuel prices than nearby non-Autobahn stations. 

The model absorbs fixed regional and time effects. Additionaly, to mitigate brand effects, we categorize each station into brand, non-brand/free and unknown.

The models dependent variable is the daily station-level fuel price for a selected
fuel type and summary statistic. Letting $y_{i,t}$ denote the observed fuel
price of station $i$ on date $t$, the outcome in this analysis is one of

$$
y_{i,t} \in
\left\{
\text{diesel}_{i,t},
\text{e5}_{i,t},
\text{e10}_{i,t}
\right\}
$$

measured either as the daily **mean** or daily **median** price.

To make Autobahn and non-Autobahn stations geographically comparable, each
Autobahn station is matched with up to **5 nearest non-Autobahn stations**
within a maximum distance of **50 km**. This creates local comparison groups that reduce the bias from regional price differences.

The regression model from AbsorbingLS can be written in the general form

$$
y_i = x_i \beta + z_i \gamma + \epsilon_i
$$

where $y_i$ is the fuel price outcome, $x_i$ the regressor of
interest, and $z_i$ collects the fixed effects.

In our application, this corresponds to

$$
y_{i,t}
=
\beta \cdot \text{autobahn}_i
+ \theta^\top \text{brand_category}_i
+ \alpha_m
+ \delta_t
+ \varepsilon_{i,t}
$$

where $\text{autobahn}_i$ is an indicator equal to 1 if station $i$ is
located on the Autobahn, $\text{brand_category}_i$ captures the station's
brand classification, $\alpha_m$ denotes match-set (regional) fixed effects, and
$\delta_t$ denotes date fixed effects.

$\beta$ is the coefficient of interest. It captures the average price
difference between Autobahn and non-Autobahn stations after controlling for
local geographic proximity through the matched sets, for common daily shocks
through date fixed effects, and for systematic brand differences through brand
controls.

The model is estimated separately for each year and for each combination of
fuel type (**diesel**, **e5**, **e10**) and price statistic (**mean**,
**median**). Standard errors are clustered at the **station level** to account
for serial dependence in repeated observations of the same station over time.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=11
        )
    ], justify="center"),
    html.Br(),

    dbc.Row([
        dbc.Col([
            html.H3("Autobahn Effect: Mean Results by Fuel Type", className="text-center"),
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Diesel", id="premium-btn-diesel", n_clicks=0, color="primary", style={"width": "150px"}),
                dbc.Button("E5", id="premium-btn-e5", n_clicks=0, color="primary", style={"width": "150px"}),
                dbc.Button("E10", id="premium-btn-e10", n_clicks=0, color="primary", style={"width": "150px"})
            ], size="lg"),
        ], width="auto")
    ], justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Mean Autobahn Premium"),
                    html.H1(id="autobahn-mean-coef"),
                    html.Small("Average coefficient across years")
                ])
            ]),
            width=4
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Mean 95% CI"),
                    html.H4(id="autobahn-mean-ci"),
                    html.Small("Average confidence interval (€/liter)")
                ])
            ]),
            width=4
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Significant Years"),
                    html.H1(id="autobahn-significance"),
                    html.Small("Years with p < 0.05")
                ])
            ]),
            width=4
        ),
    ], className="g-3"),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Autobahn premium over the years"),
                dbc.CardBody([
                    dcc.Graph(
                        id="autobahn-mean-trend",
                        config={"displayModeBar": False, "responsive": True},
                        style={"height": "400px", "width": "100%"}
                    )
                ])
            ]),
            width=12
        )
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id="autobahn-premium-development-barchart",
                        figure=plot_autobahn_premium_barchart(),
                        config={"responsive": True},
                        style={"height": "400px", "width": "100%"}
                    )
                ])

            ])
        ])
    ]),

    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Alert(
                [
                    html.H4("Main Insights"),
                    dcc.Markdown(r"""
The results show a **positive and statistically significant Autobahn premium for fuel prices in every year** from 2014 to 2026. The estimated coefficient rises from about **€0.04 per liter in 2014** to about **€0.29 per liter in 2026**, which suggests that fuel prices at Autobahn stations were consistently higher than at matched non-Autobahn stations and that this price gap increased substantially over time.

The increase is especially visible from **2018 onward**, with another strong rise after **2022**. Since the confidence intervals remain clearly above zero in all years, the estimated premium appears to be very robust across specifications and years.

The regression suggests that even after controlling for **local matching structure**, **date fixed effects**, and **brand-category differences**, Autobahn stations tend to charge a noticeable price premium relative to comparable nearby stations.

Possible explanations for this may include:
- **weaker competitive pressure on the Autobahn**, since around 93% of the Autobahn service stations are owned by the (formerly government-owned and now private) Tank & Rast GmbH
- auction-based **supply and distribution rights** that oil companies have to obtain could contribute to higher fuel prices 
- the sharp increase in the later years may also be related to the broader energy market disruptions following the **war in Ukraine** and generally higher operating and service costs

At the same time, these regressions identify a **systematic association**, not a definitive causal mechanism. The proposed explanations are therefore plausible interpretations of the observed premium, but they are **not directly tested by this model**.



                        """, 
                        mathjax=True)
                ],
                color="primary"
            ),
            width=8
        ),
    ], justify="center"),

    html.Br(),

    dbc.Row([
            dbc.Col([
                html.H3("Are the gas prices at Autobahn stations more volatile than the prices at normal gas stations?", className="text-center"),
            ]),
            dbc.Col(
                html.A(
                    dbc.Button("Back to top", color="primary", size="sm"),
                    href="#other-effects-top"
                ),
                width=2,
                style={"display": "flex", "justifyContent": "flex-end"}
            )
        ]),


    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Wilcoxon-Test")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
Now we perform a wilcoxon signed rank test to see wether the autobahn station prices differ from normal station prices in volatility.

For this test, we examine whether the **residual price volatility** differs between
**Autobahn stations** and their matched **non-Autobahn controls** after the
fixed effects on the price have been removed in the panel
regression above.

The input for the test is the set of regression residuals
$\hat{\varepsilon}_{i,t}$ saved from the panel regession model. These residuals
represent the part of station-level fuel prices that remains unexplained after
controlling for the Autobahn factor, brand effects, regional fixed
effects, and date fixed effects.

For each station $i$ in year $y$, volatility is summarized from the residual
series using one of two volatility measures. If the robust option is selected,
volatility is measured by the **median absolute deviation**

$$
\text{median-absolute-deviation}_{i,y}
=
\operatorname{median}_{t \in y}
\left|
\hat{\varepsilon}_{i,t}
-
\operatorname{median}_{s \in y}(\hat{\varepsilon}_{i,s})
\right|
$$

Alternatively, volatility can be measured by the **standard deviation**

$$
\text{SD}_{i,y}
=
\sqrt{
\frac{1}{n_{i,y}-1}
\sum_{t \in y}
\left(
\hat{\varepsilon}_{i,t}
-
\bar{\hat{\varepsilon}}_{i,y}
\right)^2
}
$$

where $n_{i,y}$ is the number of residual observations for station $i$ in year
$y$. We will only consider stations with at least **30 observations** for the
volatility comparison.

To obtain a matched comparison, the volatility of the Autobahn station in match
set $m$ is compared with the average volatility of its matched non-Autobahn
control stations. Letting $V^T_{m,y}$ denote the Autobahn-station volatility and
$\bar{V}^C_{m,y}$ the mean control volatility in the same match set and year, we
define the paired difference as

$$
d_{m,y} = V^T_{m,y} - \bar{V}^C_{m,y}
$$

We implemented a two sided test for paired samples. In the present application, this is appropriate
because volatility is compared **within matched sets**, so the comparison is
based on paired Autobahn-control differences rather than on two independent
samples.

Following the formal definition, the two-sided test evaluates
whether the distribution of the paired differences $d_{m,y}$ is symmetric about
zero. The null and alternative hypotheses can be written as

$$
H_0: d_{m,y} \text{ is symmetrically distributed around } 0
$$

$$
H_1: d_{m,y} \text{ is not symmetrically distributed around } 0
$$

For the test, the nonzero absolute differences $|d_{m,y}|$ are ranked, their
original signs are reattached, and the Wilcoxon statistic is constructed from
the signed ranks. In the two-sided case, the test statistic is

$$
T = \min(W^+, W^-)
$$

where $W^+$ is the sum of ranks associated with positive differences and $W^-$
is the sum of ranks associated with negative differences. In our function,
pairs with $d_{m,y} = 0$ are removed before the test, so only non-zero matched
differences contribute to the statistic.

In our application, a **positive median difference** indicates that Autobahn
stations exhibit higher residual volatility than their matched non-Autobahn
controls in the same year. A **small p-value** suggests that the paired
volatility differences are not centered symmetrically around zero, which is
evidence of a systematic difference in residual volatility between the two
groups.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=11
        )
    ],justify="center"),
    
    html.Br(),

    html.Div(id="dummy-trigger", children="load", style={"display": "none"}),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Median Yearly Effect"),
                    html.H1(id="wilcoxon-median-effect"),
                    html.Small("Median of annual paired median differences")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Median p-value"),
                    html.H1(id="wilcoxon-p-value"),
                    html.Small("Median p-value")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Significant Years"),
                    html.H1(id="wilcoxon-significance"),
                    html.Small("Years with raw p < 0.05")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Positive-effect Years"),
                    html.H1(id="wilcoxon-direction"),
                    html.Small("Years with autobahn > non-autobahn volatility")
                ])
            ]),
            md=3
        ),
    ], className="g-3"),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Median volatility difference over the years"),
                dbc.CardBody([
                    dcc.Graph(
                        id="wilcoxon-lollipop-plot",
                        config={"displayModeBar": False, "responsive": True},
                        style={"height": "450px", "width": "100%"}
                    )
                ])
            ]),
            width=12
        )
    ]),

    html.Br(),
    
    dbc.Row([
        dbc.Col(
            dbc.Alert(
                [
                    html.H4("Main Insights"),
                    dcc.Markdown(r"""
The test results show that **Autobahn stations have statistically significant higher residual price volatility than matched non-Autobahn stations in every year** from 2014 to 2026. This is visible in the fact that the **median difference is positive in all years**, which means that the volatility measure based on the residuals is consistently larger for Autobahn stations than for their matched non-Autobahn control groups.

The effect is already present in the early years, but it becomes much stronger from **2022 to 2024**. In particular, the median volatility difference rises sharply in **2022** and remains clearly high in **2023** and **2024**. This suggests that Autobahn stations not only exhibit higher fuel prices on average, but also show more short-term price fluctuations that are not fully explained by the controls in the panel regression.

Because the test is based on the **residuals from the panel regression**, we can not not simply conclude that raw Autobahn prices fluctuate more, but rather that **the unexplained part of fuel price volatility** is larger at Autobahn stations even after controlling for match-set (regional) structure, date effects, and brand-category differences.

A plausible substantive interpretation (similar to the interpretation of the Autobahn premium) is that Autobahn stations may face a pricing environment with **weaker competitive pressure**, more rigid institutional structures (like the concession auctions), and potentially stronger exposure to market-wide shocks. The particularly large differences in **2022–2024** are consistent with the idea that periods of oil market disruption, such as the aftermath of the **war in Ukraine**, may have amplified this volatility gap. At the same time, these mechanisms are only possible explanations and are **not directly identified by the test itself**.

The later years should also be interpreted with some care, especially in 2026, since we only have the data for about 2 full months for far in this year.
                        """, 
                        mathjax=True)
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
        dbc.Col([
            html.H3("The effect of proximity to other stations on the average price", className="text-center"),
        ]),
        dbc.Col(
            html.A(
                dbc.Button("Back to top", color="primary", size="sm"),
                href="#other-effects-top"
            ),
            width=2,
            style={"display": "flex", "justifyContent": "flex-end"}
        )

    ], id="proximity-section"),
    html.Br(),
 html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Clustering of the Stations")),
                dbc.CardBody([
                    html.P("We use DBSCAN to cluster the stations based on their proximity to each other."),
                    html.P("We choose 2 Parameter sets, one with a smaller and one with a larger radius, to see the effect of proximity on the average price.")
                ])
            ]),
            #width=12
        )
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Cluster 1: Larger Radius (eps=2km, min_samples=4)", className="text-white"), class_name="bg-primary"),
                dbc.CardBody([
                    dcc.Graph(id="cluster_1_map")
                ])
            ]),
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Cluster 2: Smaller Radius (eps=0.2km, min_samples=2)", className="text-white"), class_name="bg-primary"),
                dbc.CardBody([
                    dcc.Graph(id="cluster_2_map")
                ])
            ])
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Cleaning the Dataset")),
                dbc.CardBody([
                    html.P("To avoid large data imbalances, we clean the data by removing all autobahn stations."),
                    html.P("In the chart below you can see the original share of autobahn stations for each cluster."),
                    html.Br(),
                    dcc.Graph(id="cluster_autobahn_share_pie"),
                ])
            ])
        ]),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Choose the fuel type to analyze")),
                dbc.ButtonGroup([
                    dbc.Button("Diesel", id="fuel-btn-diesel-competition", n_clicks=0, color="info", style={"width": "150px"}),
                    dbc.Button("E5", id="fuel-btn-e5-competition", n_clicks=0, color="info", style={"width": "150px"}),
                    dbc.Button("E10", id="fuel-btn-e10-competition", n_clicks=0, color="info", style={"width": "150px"})
                ], size="lg"),
            ])
        ], width="auto")
    ], justify="center"),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.CardGroup([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Markdown("""
### Visual Understanding: Price Difference

To simplify the analysis, we are plotting the **price difference** between clustered and unclustered stations:

* **Positive Numbers (+):** Clustered stations are **more expensive**.  
    *Example:* `0.30` means clustered stations cost **30 cents more** than unclustered ones.
* **Negative Numbers (-):** Clustered stations are **cheaper** than unclustered ones.

This allows for a quick assessment of whether proximity to other stations (clustering) correlates with a price premium or a discount.
                """)
                    ])
                ])  
            ])
        )
    ],),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Price Difference Cluster 1: Larger Radius", className="text-white"), class_name="bg-primary"),
                dbc.CardBody([
                    dcc.Graph(id="price_diff_cluster_1_line")
                ])
            ]),
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Price Difference Cluster 2: Smaller Radius", className="text-white"), class_name="bg-primary"),
                dbc.CardBody([
                    dcc.Graph(id="price_diff_cluster_2_line")
                ])
            ])
        ])
    ]), 
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.P("Because of the high oscillation, the graph is quite cluttered. \n To easier make out underlying trends we will now use a boxplot to visualize the price difference."),
                ])
            ])
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Price Difference Cluster 1: Larger Radius", className="text-white"), class_name="bg-primary"), 
                dbc.CardBody([
                    dcc.Graph(id="price_diff_cluster_1_boxplot")
                ])
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Price Difference Cluster 2: Smaller Radius", className="text-white"), class_name="bg-primary"), 
                dbc.CardBody([
                    dcc.Graph(id="price_diff_cluster_2_boxplot")
                ])
            ])
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        """
    ### Main Insight

    While no significant differences can be observed in the **first clustering approach**,  
    a **clear upward trend starting in 2023** becomes evident.

    This pattern is **not present to the same extent** in the first clustering,  
    which allows us to largely **rule out effects specific to urban areas**.

    Although a **higher station density** may indicate a more profitable environment,  
    this alone **does not sufficiently explain the sudden price increase from 2023 onward**.

    > **Conclusion:**  
    > At this stage, **no definitive explanation** for this behavior has been identified.
                        """
                    )
                ])
            ], color="primary"),
            width=8
        )
    ],justify="center"),
    html.Br(),
   

    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H3("Is fuel in border regions more/less expensive compared to non-border region stations?", className="text-center"),
        ]),
        dbc.Col(
            html.A(
                dbc.Button("Back to top", color="primary", size="sm"),
                href="#other-effects-top"
            ),
            width=2,
            style={"display": "flex", "justifyContent": "flex-end"}
        )
    ], id="border-section"),
    html.Br(),

    dbc.Row([dbc.Col([
        dbc.Card([
            dbc.CardHeader("""This map shows all border region stations (0-8km from next border) and the stations from the surrounding area (8-25km). 
                           In the following test, we grouped the gas stations by their nearest bordering country to get separate  results for each country neighbouring Germany."""),
       
            dbc.CardBody([
                dcc.Graph(
                    id="border-stations-map",
                    figure=plot_border_stations(),
                    config={"responsive": True},
                    style={"height": "1000px", "width": "100%"}
                )
            ])
        ]),
    ],width=10)],justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Two sided Mann-Whitney-U-Test")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
This test examines whether fuel prices at stations **close to the border** differ
from prices at stations in the **surrounding region**.

The analysis is based on station-level median prices. For each station, the fuel-specific
median price is first calculated either **within each year** or **across all years**.
This ensures that each station contributes one representative value to the comparison.

For a given neighbouring country, two independent groups are then compared:

- **Border group**: stations that are **up to 8km away** from the next border
- **Surrounding group**: stations that are **8-25km away** from the next border

The statistical test used is the **two-sided Mann–Whitney U test**. In general,
this test evaluates whether two independent samples come from the same distribution
without requiring a normality assumption.

Let $X_1, \dots, X_n$ denote the station-level median prices in the border region
and $Y_1, \dots, Y_m$ the station-level median prices in the surrounding region.
The null and alternative hypotheses are

$$
H_0: F_X = F_Y \qquad \text{vs.} \qquad H_1: F_X \neq F_Y
$$

where $F_X$ and $F_Y$ are the distribution functions of the two groups.

In addition to the test statistic and p-value, the method reports the group medians:

$$
\tilde{P}_{\text{border}}
\qquad \text{and} \qquad
\tilde{P}_{\text{surrounding}}
$$

and their difference

$$
\text{Price difference}
=
\tilde{P}_{\text{border}} - \tilde{P}_{\text{surrounding}}
$$

A negative value indicates that border stations are cheaper on average in median terms,
while a positive value indicates that border stations are more expensive.

The test is carried out both:

- **overall**, using station-level medians across all years, and
- **yearly**, using station-level medians within each year.

A result is marked as statistically significant if the p-value is below 0.05.
Only country-group comparisons with at least **5 stations in each region** are tested.

To mitigate distortions through expensive Autobahn stations, we filtered them out before the test.
We also wanted to prevent influences from different brand structures in the regions, but as you can see in the box below on the right, they were too similar to see an effect.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=11
        )
    ],justify="center"),
    
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Overall Median Difference"),
                    html.H1(id="overall-median-diff"),
                    html.Small("Median of country-level price differences")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Significant Countries"),
                    html.H1(id="overall-significance"),
                    html.Small("Countries with raw p < 0.05")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Positive-effect Countries"),
                    html.H1(id="overall-direction"),
                    html.Small("Countries with border > surrounding price")
                ])
            ]),
            md=3
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Brand Share"),
                    html.H1(id="overall-brand-share"),
                    html.Small("Border / surrounding branded stations")
                ])
            ]),
            md=3
        ),

                
    ], className="g-3", justify="center"),

    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Alert(
                [
                    html.H4("Main Insights"),
                    dcc.Markdown(r"""
The overall results suggest that fuel prices at border stations are **not uniformly lower**
than in the surrounding region. Instead, the pattern differs across neighbouring countries.

Across **all years combined**, statistically significant differences are found for
**France, Austria, the Netherlands, and Switzerland**. In all four cases, the estimated
price difference is **positive**, meaning that median prices at border stations are
slightly **higher** than in the surrounding region. The largest difference appears for
**Switzerland** with about **0.020 EUR/L**, while the other significant countries have lower differences.

A possible explanation for this could be, that **Austria** and **France** are classical european transit countries where major motorways cross through. 
For **Switzerland** and the **Netherlands** an explanation could be an inverted "fuel tourism" from these countries, because their fuel price level is much higher than in Germany. 

For **Denmark, Poland, Czechia, and Belgium**, the p-values are above 0.05, so there is
no statistically significant evidence of a systematic difference between border and
surrounding stations in the pooled comparison. In the case of **Czechia**, the estimated
difference is slightly **negative** (-0.010 EUR/L), which would indicate cheaper border
stations, but this difference is not statistically significant.

Because of the too small sample size, **Luxembourg** isn't considered in the test.

Overall, the results do **not** support a general conclusion that border stations are
cheaper. Where significant differences are found, they more often indicate **higher**
prices in the border region, although the estimated magnitudes are economically fairly small.

Note that we only calculated a test for diesel as an example. When performing the same test for e5 and e10, the results where pretty similar.
                        """, 
                        mathjax=True)
                ],
                color="primary"
            ),
            width=8
        ),
    ], justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Border vs. Surrounding Diesel Prices")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
In the following boxplot, you can see the yearly price distributions for a selected country and some of the yearly test results.
Also, some of the aggregated results for the yearly Mann-Whitney-U-Test are displayed.
For some countries, you can see slight different distributions, while other look pretty much the same. 


                        """
                    )
                ])
            ])
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Label("Select country", className="fw-bold mb-2"),
            dcc.Dropdown(
                id="border-country-dropdown",
                options=country_options,
                value=default_country,
                clearable=False,
                placeholder="Choose a country",
                style={
                    "color": "black",
                    "backgroundColor": "white"
                }
            ),
        ], md=4),
    ], className="mb-4", justify="center"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Price Difference"),
                    html.H1(id="country-price-diff"),
                    html.Small("Median border - surrounding price")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("p-value"),
                    html.H1(id="country-p-value"),
                    html.Small("Wilcoxon test result for selected country")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Significant"),
                    html.H1(id="country-significant"),
                    html.Small("Whether p < 0.05")
                ])
            ]),
            md=3
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H5("Stations"),
                    html.H1(id="country-stations"),
                    html.Small("Border / surrounding stations")
                ])
            ]),
            md=3
        ),
    ], className="g-3 mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="border-price-difference-plot"),

                ])
            ])
        ])
    ]),

    html.Br(),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.H3("What impact do extreme weather conditions have on the fuel price volatility?", className="text-center"),
        ]),
        dbc.Col(
            html.A(
                dbc.Button("Back to top", color="primary", size="sm"),
                href="#other-effects-top"
            ),
            width=2,
            style={"display": "flex", "justifyContent": "flex-end"}
        )
    ],id="weather-section"),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
Before testing a possible influence of **extreme weather events**, we had to define what conditions we will consider as "extreme weather". 
The open-meteo api provides a number of codes that describe specific weather conditions. We decided to consider the following weather events as **"extreme"**: 
heavy drizzle, freezing drizzle, heavy rain, freezing rain, snow, heavy snow, heavy showers, thunderstorm, light thunderstorm with hail, thunderstorm with hail.
Furthermore, we used the german post code **"Leitregionen"**  to split up all the gas stations into regions with similar weather conditions.

To get an overview over these weathercodes. Below you can see a plot that shows the weathercodes over the time of a year for the Leitregion 24 (Kiel/north-east Schleswig-Holstein).

                        """
                    )
                ])
            ])
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Label("Select year", className="fw-bold mb-2"),
            dcc.Dropdown(
                id="weather-year-dropdown",
                options=[{"label": str(year), "value": year} for year in range(2014, 2027)],
                value=2025,
                clearable=False,
                placeholder="Choose a year"
            ),
        ], md=4),
    ], className="mb-4", justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="yearly-weather-codes-plot")
                ])
            ])
        ])
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("Fixed-Effects Panel Regression for extreme weather influence")),
                dbc.CardBody([
                    dcc.Markdown(
                        r"""
As we can see in this example, there are not that many extreme weather events that could influence the price volatility. 
In the following section we will test wether these extreme events have an impact on the price volatility anyways.

For the panel regression we have calculated the **median price** (hourly) for each region. For practical reasons, we calculated for each regions its geographical centre and then retrieved the weather data for these coordinates.

This regression examines whether **extreme weather events** are associated with
higher **price volatility** in a panel setting.

The dependent variable is a rolling mean absolute deviation (MAD) of price
changes. Letting $\Delta P_t = P_t - P_{t-1}$, the volatility measure is

$$
\text{MAD}_t = \frac{1}{w} \sum_{j=0}^{w-1}
\left| \Delta P_{t-j} - \overline{\Delta P}_t \right|
$$

where $w$ is the rolling window length and $\overline{\Delta P}_t$ is the
rolling mean of price changes within that window.

The regression model from AbsorbingLS can be written in the general form

$$
y_i = x_i \beta + z_i \gamma + \epsilon_i
$$

where $y_i$ is the volatility measure, $x_i$ is the regressor of interest, and $z_i$ collects the fixed effects.

In our application, this corresponds to

$$
\text{volatility}_{r,t}
=
\beta \cdot \text{extreme\_weather}_{r,t}
+ \alpha_r
+ \delta_d
+ \eta_h
+ \varepsilon_{r,t}
$$

where $\alpha_r$ denotes region fixed effects, $\delta_d$ date fixed effects,
and $\eta_h$ hour fixed effects.

$\beta$ is our coefficient of interest, which captures the association
between extreme weather events and fuel price volatility after controlling for region,
date, and hour effects. Standard errors are clustered at the region level.

Please note that this regression only tests the diesel median. Since the results for all were insignificant and very small, we decided to only show this one example.
                        """,
                        mathjax=True,
                    ),
                ])
            ]),
            width=11
        )
    ],justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Alert(
        id="weather-regression-headline",
        color="secondary",
        className="mb-4"
    ),
                ])
            ])
        ],width=9)
    ],justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Effect Estimate"),
            html.H2(id="weather-effect-estimate"),
            dbc.Button("▼ Explanation", id="toggle-effect", color="primary", className="p-0 mt-2"),
            dbc.Collapse(
                html.Div(
                    "This is the estimated change in volatility associated with extreme weather. Values close to zero indicate only a very small estimated effect.",
                    className="mt-2 small"
                ),
                id="collapse-effect",
                is_open=False
            )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("p-value"),
            html.H2(id="weather-p-value"),
            dbc.Button("▼ Explanation", id="toggle-pvalue", color="primary", className="p-0 mt-2"),
            dbc.Collapse(
                html.Div(
                    "The p-value shows how compatible the estimate is with no effect. Large values indicate weak evidence against the null hypothesis.",
                    className="mt-2 small"
                ),
                id="collapse-pvalue",
                is_open=False
            )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("95% CI"),
            html.H2(id="weather-confidence-interval"),
            dbc.Button("▼ Explanation", id="toggle-ci", color="primary", className="p-0 mt-2"),
            dbc.Collapse(
                html.Div(
                    "This is the plausible range for the true effect. If zero lies inside the interval, the effect is not statistically distinguishable from zero at the 5% level.",
                    className="mt-2 small"
                ),
                id="collapse-ci",
                is_open=False
            )
        ]), className="border-primary"), width=3),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Observations"),
            html.H2(id="weather-observations"),
            dbc.Button("▼ Explanation", id="toggle-obs", color="primary", className="p-0 mt-2"),
            dbc.Collapse(
                html.Div(
                    "This gives the number of observations used in the regression. Larger samples usually lead to more precise estimates.",
                    className="mt-2 small"
                ),
                id="collapse-obs",
                is_open=False
            )
        ]), className="border-primary"), width=3),
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("R²"),
            html.H2(id="weather-r2"),
            dbc.Button("▼ Explanation", id="toggle-r2-weather", color="primary", className="p-0 mt-2"),
            dbc.Collapse(
                html.Div(
                    "R² measures how much of the variation in volatility is explained by the model overall. It does not tell you whether the extreme-weather coefficient itself is significant.",
                    className="mt-2 small"
                ),
                id="collapse-r2-weather",
                is_open=False
            )
        ]), className="border-primary"), width=4)
    ], justify="center"),

    html.Br(),
    
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Alert(
                [
                    html.H4("Main Insights"),
                    dcc.Markdown(r"""
The coefficient on **extreme_weather** is negative but statistically
insignificant ($\hat{\beta} = -2.426 \times 10^{-5}$, $p = 0.594 >> 0.05$). 

This indicates that, after controlling for region, date, and hour fixed effects, the
analysis does not find evidence of a systematic association between extreme
weather events and the rolling mean absulute deviation of price volatility.

The estimated effect is very small in magnitude, and the confidence interval
includes both negative and positive values, suggesting that the true effect may
be close to zero.
                        """, 
                        mathjax=True)
                ],
                color="primary"
            ),
            width=6
        ),
    ], justify="center"),

    html.Br(),

    dbc.Row([
        dbc.Col(
            html.A(
                dbc.Button("Back to top", color="primary", outline=True, size="sm"),
                href="#other-effects-top"
            ),
            className="text-end"
        )
    ]),
    html.Br(),

    html.Br(),
    html.Hr(),
],
fluid=True)