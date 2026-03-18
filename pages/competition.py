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
            #width=12
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
            ], color="primary")
        )
    ]),
    html.Br(),
    html.Hr(),


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
], fluid=True)
