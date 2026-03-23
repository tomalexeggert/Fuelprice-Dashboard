from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "anomalies"

_df_monthly = pd.read_parquet(_DATA_DIR / "monthly_anomaly_rate_2021_2026.parquet")
_df_monthly["date"] = pd.to_datetime(_df_monthly[["year", "month"]].assign(day=1))

_HOURLY_YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
_df_hourly = {
    year: pd.read_parquet(_DATA_DIR / f"hourly_anomaly_rate_{year}.parquet")
    for year in _HOURLY_YEARS
}

_df_stations_map = pd.read_parquet(_DATA_DIR / "top_stations_map.parquet")


def plot_anomaly_rate_per_month() -> go.Figure:
    """Plot the monthly anomaly rate for E10 and diesel observations."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=_df_monthly["date"],
            y=_df_monthly["anomaly_rate"] * 100,
            mode="lines+markers",
            marker=dict(size=5),
            line=dict(width=2, color="steelblue"),
            hovertemplate="%{x|%Y-%m}<br>Rate: %{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="E10/Diesel Anomaly Rate per Month (2021-2026)",
        xaxis_title="Date",
        yaxis_title="Anomaly Rate (%)",
        hovermode="x unified",
        xaxis=dict(tickformat="%Y-%m", tickangle=45),
        template="plotly_white",
    )
    return fig


def plot_anomaly_rate_by_hour(year: int) -> go.Figure:
    """Plot hourly anomaly rates for the selected year."""
    df = _df_hourly[year]
    fig = go.Figure(
        go.Bar(
            x=df["hour"],
            y=df["anomaly_rate"] * 100,
            marker_color="steelblue",
            hovertemplate="Hour: %{x}<br>Anomaly Rate: %{y:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Anomaly Rate by Hour of Day ({year})",
        xaxis_title="Hour of Day",
        yaxis_title="Anomaly Rate (%)",
        xaxis=dict(tickmode="linear"),
        template="plotly_white",
    )
    return fig


def plot_top_stations_map(top_n: int = 100) -> go.Figure:
    """Plot the top stations by anomaly rate on a Germany map."""
    df = _df_stations_map.head(top_n)
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        size="anomaly_rate",
        color="anomaly_rate",
        hover_name="name",
        hover_data={"anomalies": True, "updates": True, "anomaly_rate": ":.3f"},
        size_max=18,
        zoom=5,
        center=dict(lat=51.5, lon=10.0),
        height=850,
        title=f"Top {top_n} Gas Stations by Anomaly Rate (2021-2026)",
        color_continuous_scale="Turbo",
        mapbox_style="open-street-map",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig
