from .oil_impact_callbacks import register_oil_callbacks
from .station_callbacks import register_station_callbacks
from .competition_callbacks import register_competition_callbacks
from .home_callbacks import register_home_callbacks


def register_callbacks(app):

    register_oil_callbacks(app)
    register_station_callbacks(app)
    register_competition_callbacks(app)
    register_home_callbacks(app)