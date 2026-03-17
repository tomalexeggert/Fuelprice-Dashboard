from pathlib import Path
from typing import Literal
import pandas as pd
import plotly.express as px
import yfinance as yf
import numpy as np
from plotly import graph_objects as go
import statsmodels.api as sm

# Data root:
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DERIVED_DIR = PROJECT_ROOT / "data" / "national_daily_last"
StatType = Literal["mean", "median"]

def plot_national_fuel_prices_year(
    year: int,
    stat: StatType = "mean",
    show_oil: bool = False
):
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

    if show_oil:
        oil_df = load_brent(
            start=f"{year}-01-01",
            end=f"{year+1}-01-01",
            interval="1d"
        )

        oil_df["day"] = pd.to_datetime(oil_df["time"]).dt.normalize()
        oil_df = oil_df.sort_values("day")

        fig.add_trace(
            go.Scatter(
                x=oil_df["day"],
                y=oil_df["oil_close"],
                mode="lines",
                name="Brent oil (EUR)",
                yaxis="y2",
                line=dict(
                          color="black",
                          width=3
                )
            )
        )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Day",
        yaxis_title=f"Price ({stat})",
        legend_title="Fuel type"
    )

    if show_oil:
        fig.update_layout(
            yaxis2=dict(
                title="Oil (EUR)",
                overlaying="y",
                side="right",
                showgrid=False
            )
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

def plot_ccf_heatmap_oil(fuel_type: str):
    years = range(2014, 2026)

    ccf_all = []
    for y in years:
        corr = compute_ccf_year(y, fuel_type=fuel_type, K_LAG=10)
        ccf_all.append(corr)

    ccf_all = pd.DataFrame(ccf_all)
    ccf_all.index = years

    max_abs = np.abs(ccf_all.to_numpy()).max()

    fig = px.imshow(
        ccf_all,
        color_continuous_scale="RdBu_r",
        zmin=-max_abs,
        zmax=max_abs,
        aspect="auto",
        text_auto=".2f",
        labels={
            "x": "Lag",
            "y": "Year",
            "color": "Correlation"
        },
        title=f"CCF Oil → {fuel_type.split('_')[0].upper()} by Year"
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig



# --------------------------------------------



def load_merge_year(year: int, fuel_type: str, interval: str = "1d") -> pd.DataFrame:
    """
    Load one year of national fuel data + Brent oil, merge on day, forward-fill oil.
    Returns columns: day, fuel_price, oil_close
    """
    oil = load_brent(f"{year}-01-01", f"{year+1}-01-01", interval=interval)
    fuel_path = DEFAULT_DERIVED_DIR / f"national_daily_last_{year}.csv"
    fuel = pd.read_csv(fuel_path)

    oil["day"] = pd.to_datetime(oil["time"]).dt.normalize()
    oil = oil[["day", "oil_close"]]

    fuel["day"] = pd.to_datetime(fuel["day"]).dt.date
    oil["day"] = pd.to_datetime(oil["day"]).dt.tz_localize(None).dt.date

    fuel = fuel[["day", fuel_type]].rename(columns={fuel_type: "fuel_price"})

    merged = fuel.merge(oil, on="day", how="left").sort_values("day")
    merged["oil_close"] = merged["oil_close"].ffill()
    merged = merged.dropna(subset=["fuel_price", "oil_close"]).reset_index(drop=True)

    return merged

def add_returns_and_lags(df: pd.DataFrame, K_LAG: int) -> pd.DataFrame:
    """
    Add log-returns r_fuel, r_oil and lag columns r_oil_lag0..K_LAG.
    Drops NaNs created by diff/shift.
    Expects columns: fuel_price, oil_close
    """
    out = df.copy()

    out["r_fuel"] = np.log(out["fuel_price"]).diff()
    out["r_oil"]  = np.log(out["oil_close"]).diff()

    out = out.dropna(subset=["r_fuel", "r_oil"]).reset_index(drop=True)

    lags = pd.concat([out["r_oil"].shift(k) for k in range(K_LAG + 1)], axis=1)
    lags.columns = [f"r_oil_lag{k}" for k in range(K_LAG + 1)]

    out = pd.concat([out, lags], axis=1)

    lag_cols = list(lags.columns)
    out = out.dropna(subset=lag_cols + ["r_fuel"]).reset_index(drop=True)

    return out

def compute_ccf_from_prepared(prep: pd.DataFrame, K_LAG: int) -> pd.Series:
    """
    Compute CCF = corr(r_fuel_t, r_oil_{t-k}) for k=0..K_LAG from prepared dataframe.
    Expects columns r_fuel and r_oil_lag0..K_LAG.
    """
    lag_cols = [f"r_oil_lag{k}" for k in range(K_LAG + 1)]
    return prep[lag_cols].corrwith(prep["r_fuel"])

def compute_ccf_year(year: int, fuel_type: str = "e5_mean_last", K_LAG: int = 50) -> pd.Series:
    merged = load_merge_year(year, fuel_type=fuel_type, interval="1d")
    prep = add_returns_and_lags(merged, K_LAG=K_LAG)
    corr = compute_ccf_from_prepared(prep, K_LAG=K_LAG)
    corr.index = [f"lag{k}" for k in range(K_LAG + 1)]  # optional
    return corr

def fit_hac_model_all_years(fuel_type: str, K: int = 3):
    years = range(2014, 2026)

    parts = []
    for y in years:
        merged = load_merge_year(y, fuel_type=fuel_type, interval="1d")
        prep = add_returns_and_lags(merged, K_LAG=K)
        prep = prep.copy()
        prep["year"] = y
        parts.append(prep)

    df_all = (
        pd.concat(parts, ignore_index=True)
        .sort_values("day")
        .reset_index(drop=True)
    )

    data_model = df_all[["day", "year", "r_fuel"] + [f"r_oil_lag{k}" for k in range(K + 1)]].dropna()

    X = data_model[[f"r_oil_lag{k}" for k in range(K + 1)]]
    X = sm.add_constant(X)
    y = data_model["r_fuel"]

    ols = sm.OLS(y, X).fit()
    ols_hac = ols.get_robustcov_results(cov_type="HAC", maxlags=7)

    results = {
        "r2": ols.rsquared,
        "f_stat": ols.fvalue,
        "f_pval": ols.f_pvalue,
        "nobs": int(ols.nobs),
        "params": ols_hac.params,
        "bse": ols_hac.bse,
        "tvalues": ols_hac.tvalues,
        "pvalues": ols_hac.pvalues,
        "conf_int": ols_hac.conf_int(),
        "variables": X.columns.tolist(),
    }

    return results

def fit_asym_hac_model_all_years(fuel_type: str, K: int = 3):
    years = range(2014, 2026)

    parts = []
    for y in years:
        merged = load_merge_year(y, fuel_type=fuel_type, interval="1d")
        prep = add_returns_and_lags(merged, K_LAG=K)
        prep = prep.copy()
        prep["year"] = y
        parts.append(prep)

    df_all = (
        pd.concat(parts, ignore_index=True)
        .sort_values("day")
        .reset_index(drop=True)
    )

    data_model = df_all[["day", "year", "r_fuel"] + [f"r_oil_lag{k}" for k in range(K + 1)]].dropna()

    df_asym = data_model.copy()

    for k in range(K + 1):
        col = f"r_oil_lag{k}"
        df_asym[f"r_oil_pos_lag{k}"] = df_asym[col].clip(lower=0)
        df_asym[f"r_oil_neg_lag{k}"] = df_asym[col].clip(upper=0)

    pos_cols = [f"r_oil_pos_lag{k}" for k in range(K + 1)]
    neg_cols = [f"r_oil_neg_lag{k}" for k in range(K + 1)]

    df_asym = df_asym.dropna(subset=["r_fuel"] + pos_cols + neg_cols).reset_index(drop=True)

    X = df_asym[pos_cols + neg_cols]
    X = sm.add_constant(X)
    y = df_asym["r_fuel"]

    ols = sm.OLS(y, X).fit()
    ols_hac = ols.get_robustcov_results(cov_type="HAC", maxlags=14)

    names = list(X.columns)
    p = len(names)

    R = np.zeros((K + 1, p))
    for k in range(K + 1):
        R[k, names.index(f"r_oil_pos_lag{k}")] = 1
        R[k, names.index(f"r_oil_neg_lag{k}")] = -1

    wald = ols_hac.wald_test(R, scalar=True)

    results = {
        "r2": ols.rsquared,
        "f_stat": ols.fvalue,
        "f_pval": ols.f_pvalue,
        "nobs": int(ols.nobs),
        "params": ols_hac.params,
        "bse": ols_hac.bse,
        "tvalues": ols_hac.tvalues,
        "pvalues": ols_hac.pvalues,
        "conf_int": ols_hac.conf_int(),
        "variables": X.columns.tolist(),
        "wald_f": float(wald.statistic),
        "wald_pval": float(wald.pvalue),
        "wald_df_num": int(wald.df_num),
        "wald_df_denom": float(wald.df_denom),
    }

    return results

def plot_asym_lag_effects(fuel_type: str, K: int = 3):
    res = fit_asym_hac_model_all_years(fuel_type=fuel_type, K=K)

    pos_cols = [f"r_oil_pos_lag{k}" for k in range(K + 1)]
    neg_cols = [f"r_oil_neg_lag{k}" for k in range(K + 1)]

    names = res["variables"]
    params = dict(zip(names, res["params"]))
    bse = dict(zip(names, res["bse"]))

    beta_pos = np.array([params[c] for c in pos_cols])
    beta_neg = np.array([params[c] for c in neg_cols])

    se_pos = np.array([bse[c] for c in pos_cols])
    se_neg = np.array([bse[c] for c in neg_cols])

    lags = np.arange(K + 1)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=lags,
            y=beta_pos,
            mode="lines+markers",
            name="Oil increase",
            error_y=dict(
                type="data",
                array=1.96 * se_pos,
                visible=True
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=lags,
            y=beta_neg,
            mode="lines+markers",
            name="Oil decrease",
            error_y=dict(
                type="data",
                array=1.96 * se_neg,
                visible=True
            )
        )
    )

    fig.add_hline(y=0)

    fig.update_layout(
        template="plotly_white",
        title="Asymmetric Distributed Lag Effects",
        xaxis_title="Lag (days)",
        yaxis_title="Coefficient",
        xaxis=dict(
            tickmode="array",
            tickvals=list(lags)
        )
    )

    return fig