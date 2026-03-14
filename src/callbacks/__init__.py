from .oil_impact_callbacks import register_oil_callbacks
from .stations_callbacks import register_station_callbacks


def register_callbacks(app):

    register_oil_callbacks(app)
    register_station_callbacks(app)