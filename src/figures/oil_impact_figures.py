from pathlib import Path
from typing import Literal
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np
from plotly import graph_objects as go

# Data root:
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DERIVED_DIR = PROJECT_ROOT / "data" / "national_daily_last"
StatType = Literal["mean", "median"]


def plot_national_fuel_prices_year(year: int, stat: StatType = "mean"):
    if stat not in ("mean", "median"):
        raise ValueError("stat must be 'mean' or 'median'")

    file_path = DEFAULT_DERIVED_DIR / f"national_daily_last_{year}.csv"
    df = pd.read_csv(file_path)

    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values("day")

    fuels = ["e5", "e10", "diesel"]
    value_cols = [f"{fuel}_{stat}_last" for fuel in fuels]

    df_long = df.melt(
        id_vars="day",
        value_vars=value_cols,
        var_name="fuel_type",
        value_name="price"
    )
    df_long["fuel_type"] = df_long["fuel_type"].str.replace(f"_{stat}_last", "", regex=False)

    fig = px.line(
        df_long,
        x="day",
        y="price",
        color="fuel_type",
        title=f"National fuel prices ({stat}) – {year}",
        labels={
            "day": "Day",
            "price": f"Price ({stat})",
            "fuel_type": "Fuel type"
        }
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Day",
        yaxis_title=f"Price ({stat})",
        legend_title="Fuel type"
    )

    return fig

def load_brent(start: str, end: str, interval: str = "1d",) -> pd.DataFrame: #get data from yfinance

    if interval not in ("1d", "1h"):
        raise ValueError("interval must be '1d' or '1h'")

    ticker = "BZ=F"  # Brent futures
    df = yf.Ticker(ticker).history(start=start, end=end, interval=interval)

    if df is None or df.empty:
        raise RuntimeError(
            f"No data returned for Brent ({ticker}) with start={start}, end={end}, interval={interval}. "
            "Yahoo may limit the lookback for intraday intervals (e.g., 1h)."
        )
    # Reset index to column; name may be 'Date' or 'Datetime' depending on interval
    df = df.reset_index()
    time_col = "Datetime" if "Datetime" in df.columns else "Date"
    out = df[[time_col, "Close"]].rename(columns={time_col: "time", "Close": "oil_close"})

    # Make timezone-naive
    out["time"] = pd.to_datetime(out["time"]).dt.tz_localize(None)
    # Sort
    out = out.sort_values("time").reset_index(drop=True)
    # ---------------------------------------------------
    # Load EUR/USD exchange rate
    # ---------------------------------------------------
    fx = yf.Ticker("EURUSD=X").history(start=start, end=end, interval=interval)
    if fx is None or fx.empty:
        raise RuntimeError("No FX data returned for EURUSD.")
    fx = fx.reset_index()
    fx_time_col = "Datetime" if "Datetime" in fx.columns else "Date"
    fx = fx[[fx_time_col, "Close"]].rename(
        columns={fx_time_col: "time", "Close": "eurusd"}
    )
    fx["time"] = pd.to_datetime(fx["time"]).dt.tz_localize(None)
    fx = fx.sort_values("time")
    # ---------------------------------------------------
    # Merge Brent and FX (robust for hourly data)
    # ---------------------------------------------------
    merged = pd.merge_asof(
        out.sort_values("time"),
        fx.sort_values("time"),
        on="time",
        direction="backward"
    )
    merged["eurusd"] = merged["eurusd"].ffill().bfill()
    # ---------------------------------------------------
    # Convert USD → EUR
    # ---------------------------------------------------
    merged["oil_close"] = merged["oil_close"] / merged["eurusd"]
    out = merged[["time", "oil_close"]]

    return out

def plot_ccf_oil_to_fuel(year: int, fuel_type: str, k_lag: int = 25):
    fuel_path = DEFAULT_DERIVED_DIR / f"national_daily_last_{year}.csv"
    fuel_d = pd.read_csv(fuel_path)

    fuel_d["day"] = pd.to_datetime(fuel_d["day"]).dt.date

    oil_d = load_brent(
        f"{year}-01-01",
        f"{year + 1}-01-01",
        interval="1d"
    )

    oil_d["day"] = pd.to_datetime(oil_d["time"]).dt.date
    oil_d = oil_d[["day", "oil_close"]]

    fuel_col = f"{fuel_type}_mean_last" if not fuel_type.endswith("_mean_last") else fuel_type
    fuel_d_small = fuel_d[["day", fuel_col]].copy()

    merged_fill = (
        fuel_d_small
        .merge(oil_d, on="day", how="left")
        .sort_values("day")
    )

    merged_fill["oil_close"] = merged_fill["oil_close"].ffill()
    merged_fill = (
        merged_fill
        .dropna(subset=["oil_close", fuel_col])
        .reset_index(drop=True)
    )

    df_corr = merged_fill.copy()
    df_corr["r_fuel"] = np.log(df_corr[fuel_col]).diff()
    df_corr["r_oil"] = np.log(df_corr["oil_close"]).diff()
    df_corr = (
        df_corr
        .dropna(subset=["r_fuel", "r_oil"])
        .reset_index(drop=True)
    )

    lags = pd.concat(
        [df_corr["r_oil"].shift(k) for k in range(k_lag + 1)],
        axis=1
    )
    lags.columns = [f"r_oil_lag{k}" for k in range(k_lag + 1)]

    df_corr = pd.concat([df_corr, lags], axis=1)

    lag_cols = lags.columns
    data_corr = df_corr.dropna(subset=list(lag_cols) + ["r_fuel"])

    corr_values = data_corr[lag_cols].corrwith(data_corr["r_fuel"])

    ccf_df = pd.DataFrame({
        "lag_days": np.arange(k_lag + 1),
        "corr": corr_values.to_numpy()
    })

    n = len(data_corr)
    conf = 1.96 / np.sqrt(n)

    fig = go.Figure()

    for lag, corr in zip(ccf_df["lag_days"], ccf_df["corr"]):
        fig.add_trace(go.Scatter(
            x=[lag, lag],
            y=[0, corr],
            mode="lines",
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=[lag],
            y=[corr],
            mode="markers",
            showlegend=False
        ))

    fig.add_hline(y=0)
    fig.add_hline(y=conf, line_dash="dash", annotation_text="95% CI")
    fig.add_hline(y=-conf, line_dash="dash")

    fig.update_layout(
        title=f"CCF Oil → {fuel_type.upper()} ({year})",
        xaxis_title="Lag (days)",
        yaxis_title="Correlation",
        template="plotly_white"
    )

    return fig

