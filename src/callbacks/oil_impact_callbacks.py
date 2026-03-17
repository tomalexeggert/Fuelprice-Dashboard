from dash import Input, Output, ctx, State
from src.figures.oil_impact_figures import (plot_national_fuel_prices_year,
                                            plot_ccf_oil_to_fuel, plot_ccf_heatmap_oil,
                                            fit_hac_model_all_years, fit_asym_hac_model_all_years,
                                            plot_asym_lag_effects)

def register_oil_callbacks(app):
    @app.callback(
        Output("national-fuel-prices-graph", "figure"),
        Input("year-dropdown", "value"),
        Input("show-oil-switch", "value")
    )
    def update_national_fuel_prices_graph(year, show_oil):
        fig = plot_national_fuel_prices_year(year, stat="mean", show_oil=show_oil)
        return fig
    
    @app.callback(
        Output("diesel-ccf-graph-year", "figure"),
        Output("e5-ccf-graph-year", "figure"),
        Output("e10-ccf-graph-year", "figure"),
        Input("year-dropdown", "value")
    )
    def update_ccf_oil_to_fuel_graphs(year):
        diesel_fig = plot_ccf_oil_to_fuel(year=year, fuel_type="diesel")
        e5_fig = plot_ccf_oil_to_fuel(year=year, fuel_type="e5")
        e10_fig = plot_ccf_oil_to_fuel(year=year, fuel_type="e10")
        return diesel_fig, e5_fig, e10_fig
    
    @app.callback(
        Output("ccf-heatmap-all", "figure"),
        Output("fuel-btn-diesel", "color"),
        Output("fuel-btn-e5", "color"),
        Output("fuel-btn-e10", "color"),
        Input("fuel-btn-diesel", "n_clicks"),
        Input("fuel-btn-e5", "n_clicks"),
        Input("fuel-btn-e10", "n_clicks"),
    )
    def update_heatmap(diesel, e5, e10):
        button_id = ctx.triggered_id
        if button_id == "fuel-btn-diesel":
            fuel = "diesel_mean_last"
            colors = ("info", "primary", "primary")
        elif button_id == "fuel-btn-e10":
            fuel = "e10_mean_last"
            colors = ("primary", "primary", "info")
        else:
            fuel = "e5_mean_last"
            colors = ("primary", "info", "primary")
        fig = plot_ccf_heatmap_oil(fuel)
        return fig, *colors
    
    @app.callback(
        Output("hac-r2", "children"),
        Output("hac-fstat", "children"),
        Output("hac-fpval", "children"),
        Output("hac-nobs", "children"),
        Input("fuel-btn-diesel", "n_clicks"),
        Input("fuel-btn-e5", "n_clicks"),
        Input("fuel-btn-e10", "n_clicks"),
    )
    def update_hac_results(diesel_clicks, e5_clicks, e10_clicks):
        button_id = ctx.triggered_id
        if button_id == "fuel-btn-diesel":
            fuel_type = "diesel_mean_last"
        elif button_id == "fuel-btn-e10":
            fuel_type = "e10_mean_last"
        else:
            fuel_type = "e5_mean_last"
        results = fit_hac_model_all_years(fuel_type=fuel_type, K=3)
        return (
            f"{results['r2']:.3f}",
            f"{results['f_stat']:.2f}",
            f"{results['f_pval']:.3e}",
            f"{results['nobs']}"
        )
    
    @app.callback(
    Output("collapse-r2", "is_open"),
    Input("toggle-r2", "n_clicks"),
    State("collapse-r2", "is_open"),
    )
    def toggle_r2(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-fstat", "is_open"),
        Input("toggle-fstat", "n_clicks"),
        State("collapse-fstat", "is_open"),
    )
    def toggle_fstat(n, is_open):
        if n:
            return not is_open
        return is_open
    @app.callback(
        Output("collapse-fpval", "is_open"),
        Input("toggle-fpval", "n_clicks"),
        State("collapse-fpval", "is_open"),
    )
    def toggle_fpval(n, is_open):
        if n:
            return not is_open
        return is_open
    @app.callback(
        Output("collapse-nobs", "is_open"),
        Input("toggle-nobs", "n_clicks"),
        State("collapse-nobs", "is_open"),
    )
    def toggle_nobs(n, is_open):
        if n:
            return not is_open
        return is_open
    

    @app.callback(
        Output("hac-r2-asym", "children"),
        Output("hac-fstat-asym", "children"),
        Output("hac-fpval-asym", "children"),
        Output("hac-nobs-asym", "children"),
        Output("wald-f-asym", "children"),
        Output("wald-p-asym", "children"),
        Output("wald-decision-asym", "children"),
        Output("wald-interpretation-asym", "children"),
        Output("asym-lag-effects-graph", "figure"),
        Input("fuel-btn-diesel", "n_clicks"),
        Input("fuel-btn-e5", "n_clicks"),
        Input("fuel-btn-e10", "n_clicks"),
    )
    def update_asym_model(diesel, e5, e10):
        button_id = ctx.triggered_id

        if button_id == "fuel-btn-diesel":
            fuel = "diesel_mean_last"
            fuel_label = "Diesel"
        elif button_id == "fuel-btn-e10":
            fuel = "e10_mean_last"
            fuel_label = "E10"
        else:
            fuel = "e5_mean_last"
            fuel_label = "E5"

        res = fit_asym_hac_model_all_years(fuel_type=fuel, K=3)
        fig = plot_asym_lag_effects(fuel_type=fuel, K=3)

        reject_h0 = res["wald_pval"] < 0.05
        decision = "Reject H₀" if reject_h0 else "Do not reject H₀"

        if reject_h0:
            interpretation = (
                f"For {fuel_label}, the Wald test rejects symmetric pass-through "
                f"(p = {res['wald_pval']:.3e}). Positive and negative oil price changes "
                f"have significantly different effects on fuel prices."
            )
        else:
            interpretation = (
                f"For {fuel_label}, the Wald test does not reject symmetric pass-through "
                f"(p = {res['wald_pval']:.3e}). No statistically significant asymmetry is detected."
            )

        return (
            f"{res['r2']:.3f}",
            f"{res['f_stat']:.2f}",
            f"{res['f_pval']:.3e}",
            f"{res['nobs']}",
            f"{res['wald_f']:.3f}",
            f"{res['wald_pval']:.3e}",
            decision,
            interpretation,
            fig,
        )