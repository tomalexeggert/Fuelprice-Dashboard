from pathlib import Path
from typing import Literal
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re


# Data root:
PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUTOBAHN_DIR = PROJECT_ROOT / r'data' / r'autobahn'
BORDER_DIR = PROJECT_ROOT / r'data' / r'border_stations'
WEATHER_DIR = PROJECT_ROOT / r'data' / r'weather_influence'
StatType = Literal["mean", "median"]

def show_median_price_heatmap_per_region():
    '''
    This function plots a map that dynamically projects the monthly median prices of diesel for 2025 for all post code Leitregionen. 
    i: int year, string fuel_type
    o: px.scatter_map fig
    '''
    
    monthly_median_prices = AUTOBAHN_DIR / r'rq3_regional_median_prices_for_map.parquet'

    display_df = pl.read_parquet(monthly_median_prices)

    #get min and max price for an constant colorscale over the year.
    min_price = display_df["diesel_median_price"].min()
    max_price = display_df["diesel_median_price"].max()

    #create scatterplot.
    fig = px.scatter_map(
        display_df,
        lat = "avg_lat",
        lon = "avg_lng",
        color = "diesel_median_price",
        center = {"lat": 51.16, "lon": 10.45}, #geographical centre of Germany.
        animation_frame = "month",
        hover_name = "region",
        #title = "Comparision of the median diesel price in year 2025",
        labels = {"diesel_median_price": "Price (€)", "month": "Month"},
        range_color = [min_price, max_price],
        color_continuous_scale = "RdYlBu_r"
    )

    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10),
                      map=dict(
                        style="open-street-map",
                        center=dict(lat=51.1657, lon=10.4515),
                        zoom=2,
                        bounds=dict(
                            west=4.5,
                            east=16.5,
                            south=47.0,
                            north=55.2
                        )),
                      height=800,
                      autosize=True
    )
    fig.update_traces(marker = dict(size = 15, opacity = 1))

    return fig

def plot_border_stations():
    '''
    Plots a map with all border stations (red) and surrounding stations (blue).
    i: None
    o: px.scatter_map fig
    '''
    border_stations_file = BORDER_DIR / r'lower_border_stations.csv'

    border_stations = pd.read_csv(border_stations_file)
    
    fig = px.scatter_map(border_stations,
                    lat = "latitude",
                    lon= "longitude",
                    color = "border_region",
                    hover_name = "neighbour_country",
                    hover_data = "neighbour_country",
                    center = {"lat": 51.16, "lon": 10.45},
                    zoom = 2,
                    map_style = "open-street-map",
                    title = "Border and surrounding stations in germany")

    fig.update_layout(margin = {"r":0,"t":0,"l":0,"b":0},
                        map=dict(
                            style="open-street-map",
                            center=dict(lat=51.1657, lon=10.4515),
                            zoom=2,
                            bounds=dict(
                                west=4.5,
                                east=16.5,
                                south=47.0,
                                north=55.2
                            )),
                            height=800,
                            autosize=True
        )
    fig.update_traces(marker = dict(size = 15, opacity = 1))

    return fig

def show_border_price_difference(country:str):
    '''
    This function plots a boxplot with the distributions of the median fuel prices of diesel over time for a selected country. 
    For each year a box for the border region stations and a box for the surrounding region stations is plottet.
    i: string country
    o: go.Figure fig
    '''

    price_diff_path = BORDER_DIR / r'rq3_median_border_distributions.parquet'
    
    yearly_df = pl.read_parquet(price_diff_path)
   

    #filter and collect data for country.
    plot_df = pd.DataFrame((yearly_df.filter(
        (pl.col("neighbour_country") == country)
        ).select(["border_region", "diesel_median_price", "year"]).to_dicts()))
    plot_df["year"] = pd.to_datetime(plot_df["year"].astype(int).astype(str), format="%Y")
    #check if data is available.
    if plot_df.empty:
        print(f"no data found for {country}!")
        return
    


    fig = go.Figure()

    #the following part was written with the help of chatgpt.
    #create subplot for border and surrounding regions.
    for label, color in [("Border (0-8km)", "lightblue"), ("Surrounding (8-25km)", "violet")]:
        df = plot_df[plot_df["border_region"] == label]

        fig.add_trace(go.Box(
            x = df["year"],
            y = df["diesel_median_price"],
            name = label,
            marker_color = color
        ))
    
    fig.update_layout(
        title = f"Yearly distribution of median diesel prices: border vs. surrounding-region stations ({country})",
        xaxis_title = "Year",
        yaxis_title = "Median price (€/liter)",
        boxmode = "group"
    )
    fig.update_xaxes(tickformat="%Y", dtick="M12")
    
    return fig
   
def plot_yearly_autobahn_premium_line(fuel_type:str, statistic:str="mean"):
    '''
    This method plots a line of the autobahn premium for a selected fuel type with surrounding confidence intervall over the years.
    i: string fuel_type, string statistic
    o: go.Figure fig
    '''
    summary_path = AUTOBAHN_DIR / r'rq3_panel_summary.csv'
    
    yearly_df = pd.read_csv(summary_path)

    #filter for selected statistic and fuel type and format year column.
    yearly_df = yearly_df[
        (yearly_df["statistic"] == statistic) &
        (yearly_df["fuel_type"] == fuel_type)
    ].copy()

    yearly_df["year"] = pd.to_datetime(
        yearly_df["year"].astype(int).astype(str),
        format="%Y"
    )

    fig = go.Figure()

    #define color maps for each fuel type.
    fill_color_map = {
        "diesel": "rgba(0,176,246,0.2)",
        "e5": "rgba(0,100,80,0.2)",
        "e10": "rgba(231,107,243,0.2)"
    }
    line_color_map = {
        "diesel": "rgba(255,255,255,0)",
        "e5": "rgba(255,255,255,0)",
        "e10": "rgba(255,255,255,0)"
    }
    color_map = {
        "diesel": "rgb(0,176,246)",
        "e5": "rgb(0,100,80)",
        "e10": "rgb(231,107,243)"
    }

    #sort values for selected fuel type.
    df_sub = yearly_df.sort_values("year")

    #format the x and y values into desired format.
    x_vals = df_sub["year"].to_list()
    x_rev = x_vals[::-1]

    y_upper = df_sub["ci_high"].to_list()
    y_lower = df_sub["ci_low"].to_list()[::-1]

    y_line = df_sub["autobahn_coef"].to_list()

    #create custom data for the hoverinfo.
    custom_data = list(zip(
        df_sub["year"].dt.year,
        df_sub["autobahn_coef"],
        df_sub["ci_high"],
        df_sub["ci_low"]
    ))

    #plot confidence intervall.
    fig.add_trace(go.Scatter(
        x=x_vals + x_rev,
        y=y_upper + y_lower,
        fill="toself",
        fillcolor=fill_color_map[fuel_type],
        line_color=line_color_map[fuel_type],
        name=fuel_type,
        showlegend=False,
        hoverinfo="skip"
    ))
    
    #plot autobahn premium line.
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_line,
        mode="lines+markers",
        line_color=color_map[fuel_type],
        showlegend=False,
        name=fuel_type,
        customdata=custom_data,
        hovertemplate=(
            "Year: %{customdata[0]}<br>"
            "Autobahn-Premium: %{customdata[1]:.3f} €/liter<br>"
            "Upper confidence bound: %{customdata[2]:.3f} €/liter<br>"
            "Lower confidence bound: %{customdata[3]:.3f} €/liter<br>"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        xaxis_title="year",
        yaxis_title="estimated autobahn premium (€/liter)",
        template="plotly_white",
        title=f"{fuel_type} price autobahnpremium with 95% confidence interval over the years",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    fig.update_xaxes(tickformat="%Y", dtick="M12")
    
    return fig


def plot_autobahn_premium_barchart(statistic:str="mean"):
    '''
    This function plots a bar chart where each bar represents one fuel type Autobahn premium in a year. 
    So for each year, we have three separate bars. The price statistic is "mean" by default, but can also be changed to "median" if wanted. 
    i: string statistic
    o: go.Figure fig 
    '''

    summary_path = AUTOBAHN_DIR / r'rq3_panel_summary.csv'

    yearly_df = pd.read_csv(summary_path)

    #filter & preprocessing.
    yearly_df = yearly_df[yearly_df["statistic"] == statistic]
    yearly_df["year"] = pd.to_datetime(yearly_df["year"].astype(int).astype(str), format="%Y")

    fig= go.Figure()

    #using the same colormap as in the lineplot.
    color_map = {
         "diesel": "rgb(0,176,246)",
        "e5": "rgb(0,100,80)",
        "e10": "rgb(231,107,243)"
    }

    #create a df with the values for each fuel type.
    y_diesel = yearly_df[yearly_df["fuel_type"] == "diesel"]
    y_e5 = yearly_df[yearly_df["fuel_type"] == "e5"]
    y_e10 = yearly_df[yearly_df["fuel_type"] == "e10"]


    #create separate bars for each fuel type.
    fig.add_trace(go.Bar(
        x = yearly_df["year"].dt.year,
        y = y_diesel["autobahn_coef"],
        name = "diesel",
        marker_color = color_map["diesel"],
        hovertemplate=(
                "Year: %{x}<br>"
                "Fuel: diesel<br>"
                "Autobahn premium: %{y:.3f} €/liter<br>"
                "<extra></extra>"
            )
    ))
    fig.add_trace(go.Bar(
        x = yearly_df["year"].dt.year,
        y = y_e5["autobahn_coef"],
        name = "e5",
        marker_color = color_map["e5"],
        hovertemplate=(
                "Year: %{x}<br>"
                "Fuel: e5<br>"
                "Autobahn premium: %{y:.3f} €/liter<br>"
                "<extra></extra>"
            )
    ))
    fig.add_trace(go.Bar(
        x = yearly_df["year"].dt.year,
        y = y_e10["autobahn_coef"],
        name = "e10",
        marker_color = color_map["e10"],
        hovertemplate=(
                "Year: %{x}<br>"
                "Fuel: e10<br>"
                "Autobahn premium: %{y:.3f} €/liter<br>"
                "<extra></extra>"
            )

    ))

    fig.update_layout(
        title = dict(text = "Development of the autobahn premium from 2014-2026"),
        xaxis_tickfont_size = 14,
        yaxis = dict(
            title = dict(
                text = "autobahn premium (€/liter)",
                font = dict(size = 16)
            )
        ),
        legend = dict(
            x = 0,
            y = 1.0,
            bgcolor = "rgba(255, 255, 255, 0)",
            bordercolor = "rgba(255, 255, 255, 0)"
        ),
        template = "plotly_white",
        barmode = "group",
        bargap = .15,
        bargroupgap = .1 
    )

    return fig

def plot_wilcoxon_results_loolipop():
    '''
    Plots a lollipop plot for the median volatility difference of autobahn station prices and non autobahn station prices. 
    The difference is positive, when the autobahn volatility is higher than the non autobahn volatility.
    i: None
    o: go.Figure fig
    '''
    wilcoxon_df = load_wilcoxon_results()

    # Build one single trace for all stems using None separators.
    #this part was written with the help of chatgpt.
    x_stems = []
    y_stems = []
    wilcoxon_df["year"] = pd.to_datetime(wilcoxon_df["year"].astype(int).astype(str), format="%Y")

    for _, row in wilcoxon_df.iterrows():
        x_stems.extend([row["year"], row["year"], None])
        y_stems.extend([0, row["median_difference"], None])

    fig = go.Figure()

    # create the vertical lines to the points.
    fig.add_trace(
        go.Scatter(
            x=x_stems,
            y=y_stems,
            mode="lines",
            line=dict(width=2),
            showlegend=False,
            hoverinfo="skip"
        )
    )

    custom_data = list(zip(
        wilcoxon_df["year"].dt.year,
        wilcoxon_df["median_difference"]
    ))

    # create the lollipop heads.
    fig.add_trace(
        go.Scatter(
            x=wilcoxon_df["year"],
            y=wilcoxon_df["median_difference"],
            mode="markers",
            marker=dict(size=12),
            name="median volatility difference",
            customdata=custom_data,
            hovertemplate=(
                "Year: %{customdata[0]}<br>"
                "Median volatility difference: %{customdata[1]:.4f} €/liter<br>"
                "<extra></extra>"
            )

        )
    )

    fig.update_layout(
        title="Autobahn vs non autobahn stations median volatility difference over the years",
        xaxis_title="year",
        yaxis_title="median difference (€/liter)",
        template="plotly_white"
    )
    fig.update_xaxes(tickformat="%Y", dtick="M12")

    return fig

def display_weather_codes_per_region(year:int):
    '''
    Displays a plotly scatterplot with the (hourly) weathercodes from a chosen region in a chosen year. Return nothing.
    i: int year
    o: go.Figure fig
    '''

    file_path = WEATHER_DIR / "weather_region24.csv"

    weather_codes = WEATHER_DIR / "weather_codes_descriptions.csv"

    df = pd.read_csv(file_path).drop(columns=["precipitation", "temperature_2m"])

    code_df = pd.read_csv(weather_codes)

    #downsmapling df to monthly avg.
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = pd.to_datetime(df["date"]).dt.year

    df_plot = df[df["year"] == year]

    # merge descriptions into the plot df.
    df_plot = df_plot.merge(code_df, on = "weather_code", how = "left")
    
    #sort weather codes by ascending order
    df_plot = df_plot.sort_values("weather_code", ascending=True)

    fig= go.Figure()

    # create scatter plot.
    # this part was created with the help of chatgpt
    fig.add_trace(
        go.Scatter(
            x = df_plot["date"],
            y = df_plot["weather_code"],
            mode = "markers",
            marker = dict(size=5,
                        color=df_plot["weather_code"],
                        colorscale="Turbo",
                        opacity=0.6),
            customdata = df_plot[["description"]],
            name = "",
            hovertemplate = (
                "Date: %{x|%Y-%m-%d %H:%M}<br>"
                "Weather code: %{y}<br>"
                "Description: %{customdata[0]}"
                "<extra></extra>"
            )

        )
    )
    fig.update_layout(
        title_text = f"weather codes for region 24 (Kiel and Surrounding) in year {year}",
        xaxis_title = "Date",
        yaxis_title = "Weather code",
        plot_bgcolor = "white",
        hovermode = "closest"
    )

    # fit for qualitative data (->discrete values)
    fig.update_yaxes(
        type = "category",
        showgrid = True,
        gridcolor = "lightgrey"
    )

    fig.update_xaxes(showgrid = True, gridcolor = "lightgrey")

    return fig


def load_autobahn_results():
    '''
    Loads the summary of the autbahn premium panel regression.
    i: None
    o: pd.DataFrame df
    '''
    df = pd.read_csv(AUTOBAHN_DIR / r'rq3_panel_summary.csv')
    return df

def load_wilcoxon_results():
    '''
    Loads the summary of the wilcoxon signed rank test.
    i: None
    o: pd.DataFrame wilcoxon_df
    '''

    wilcoxon_result_path = AUTOBAHN_DIR / "rq3_wilcoxon.csv"

    wilcoxon_df = pd.read_csv(wilcoxon_result_path)
    
    return wilcoxon_df

def load_overall_border_mann_whitney_results():
    '''
    Loads the overall test result from the Mann-Whitney-U-Test on non-Autobahn border stations.
    i: None
    o:pd.DataFrame df
    '''

    test_result_path = BORDER_DIR / "rq3_overall_non_autobahn_border_test_result.csv"

    df = pd.read_csv(test_result_path)

    return df

def load_yearly_border_mann_whitney_results():
    '''
    Loads the yearly test result from the Mann-Whitney-U-Test on non-Autobahn border stations.
    i: None
    o:pd.DataFrame df
    '''

    test_result_path = BORDER_DIR / "rq3_non_autobahn_yearly_border_test_result.csv"

    df = pd.read_csv(test_result_path)

    return df

def get_country_options():
    '''
    returns the available countries from the border test for the country dropdown.
    i: None
    o: list
    '''
    df = load_overall_border_mann_whitney_results()

    countries = sorted(df["Country"].dropna().unique().tolist())

    return [{"label": c, "value": c} for c in countries]

def load_border_brand_structure():
    '''
    Loads the brand structure df at the border.
    i:None
    o: pd.DataFrame df
    '''
    filepath = BORDER_DIR / "rq3_border_brand_distribution.csv"

    df = pd.read_csv(filepath)

    return df


def load_extreme_weather_regression():
    '''
    Reads the extreme weather regression result from a txt and formats it accordingly.
    i: None
    o: dict
    '''
    result_path = WEATHER_DIR / "rq9_regression_result.txt"
    text = result_path.read_text(encoding="utf-8")

    r2_match = re.search(r"R-squared:\s+([0-9.]+)", text)
    obs_match = re.search(r"No\. Observations:\s+([0-9]+)", text)
    param_match = re.search(
        r"extreme_weather\s+([-\deE.]+)\s+([-\deE.]+)\s+([-\deE.]+)\s+([-\deE.]+)\s+([-\deE.]+)\s+([-\deE.]+)",
        text
    )

    if not (r2_match and obs_match and param_match):
        raise ValueError("Could not parse regression summary file.")

    coefficient = float(param_match.group(1))
    std_err = float(param_match.group(2))
    t_stat = float(param_match.group(3))
    p_value = float(param_match.group(4))
    lower_ci = float(param_match.group(5))
    upper_ci = float(param_match.group(6))

    return {
        "coefficient": coefficient,
        "std_err": std_err,
        "t_stat": t_stat,
        "p_value": p_value,
        "lower_ci": lower_ci,
        "upper_ci": upper_ci,
        "observations": int(obs_match.group(1)),
        "r_squared": float(r2_match.group(1)),
    }
