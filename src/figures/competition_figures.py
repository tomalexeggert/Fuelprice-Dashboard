import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import polars as pl


def plot_clusters(data: pl.DataFrame, labels: list[int] | np.ndarray) -> go.Figure:
    """Plot clustered stations on a map and highlight DBSCAN noise points."""
    data = data.with_columns(pl.Series("cluster", labels))
    pdf = data.to_pandas()
    pdf["status"] = np.where(pdf["cluster"] == -1, "noise", "clustered")

    fig = px.scatter_mapbox(
        pdf,
        lat="latitude",
        lon="longitude",
        color="status",
        color_discrete_map={"noise": "red", "clustered": "green"},
        hover_name="uuid",
        zoom=2,
        center={"lat": 51.1657, "lon": 10.4515},
        height=1000,
    )

    fig.update_layout(
        showlegend=False,
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=51.1657, lon=10.4515),
            zoom=2,
            bounds=dict(west=5.5, east=15.5, south=47.0, north=55.2),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    # Increase marker size if you want to export high-resolution static images.
    # fig.update_traces(marker=dict(size=20))
    return fig


def plot_motorway_cluster_pies(
    clusters1: pl.DataFrame,
    clusters2: pl.DataFrame,
    motorway_df: pl.DataFrame,
) -> go.Figure:
    """Compare motorway stations assigned to clusters vs. noise for two runs."""
    mw1 = clusters1.join(motorway_df, left_on="uuid", right_on="uuid", how="inner")
    mw2 = clusters2.join(motorway_df, left_on="uuid", right_on="uuid", how="inner")

    clustered1 = mw1.filter(pl.col("cluster") != -1).height
    noise1 = mw1.filter(pl.col("cluster") == -1).height
    clustered2 = mw2.filter(pl.col("cluster") != -1).height
    noise2 = mw2.filter(pl.col("cluster") == -1).height

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=["Cluster", "Noise"],
            values=[clustered1, noise1],
            marker=dict(colors=["green", "red"]),
            textinfo="label+value",
            domain={"x": [0.0, 0.45], "y": [0, 1]},
            name="Cluster Set 1",
        )
    )
    fig.add_trace(
        go.Pie(
            labels=["Cluster", "Noise"],
            values=[clustered2, noise2],
            marker=dict(colors=["green", "red"]),
            textinfo="label+value",
            domain={"x": [0.55, 1.0], "y": [0, 1]},
            name="Cluster Set 2",
        )
    )
    fig.update_layout(
        title="Autobahn stations in clusters",
        annotations=[
            dict(
                text="Cluster Set 1",
                x=0.22,
                y=1.1,
                showarrow=False,
                font=dict(size=16),
            ),
            dict(
                text="Cluster Set 2",
                x=0.78,
                y=1.1,
                showarrow=False,
                font=dict(size=16),
            ),
        ],
    )
    return fig


def plot_price_difference_line(
    df: pd.DataFrame,
    cluster_name: str,
    fuel: str,
) -> go.Figure:
    """Plot mean and optional median daily price differences for one cluster."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["day"], y=df["mean_diff"], mode="lines", name="Mean"))

    if "median_diff" in df.columns:
        fig.add_trace(
            go.Scatter(x=df["day"], y=df["median_diff"], mode="lines", name="Median")
        )

    fig.update_layout(
        title=f"{fuel.upper()} - {cluster_name}",
        xaxis_title="Day",
        yaxis_title="EUR",
        template="plotly_white",
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
    )
    return fig


def plot_price_difference_boxplot(
    diff_df: pd.DataFrame,
    cluster_name: str,
    fuel: str,
) -> go.Figure:
    """Plot yearly boxplots of daily mean price differences for one cluster."""
    diff_df["day"] = pd.to_datetime(diff_df["day"])
    diff_df["year"] = diff_df["day"].dt.year

    fig = go.Figure()
    for year in sorted(diff_df["year"].unique()):
        fig.add_trace(
            go.Box(
                y=diff_df.loc[diff_df["year"] == year, "mean_diff"],
                name=str(year),
                marker_color="blue",
            )
        )

    fig.update_layout(
        showlegend=False,
        title=f"{fuel.upper()} - {cluster_name}",
        template="plotly_white",
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="black"),
    )
    return fig
