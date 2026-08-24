from .geometry import TankGeometry
from .fuel import FuelState


def calculate_fuel_cg(
    geometry: TankGeometry,
    fuel: FuelState
):
    x_cg = geometry.length / 2.0
    y_cg = geometry.width / 2.0
    z_cg = fuel.fuel_height(geometry) / 2.0

    return {
        "x_cg": x_cg,
        "y_cg": y_cg,
        "z_cg": z_cg
    }
