from wing_sloshing.geometry import TankGeometry
from wing_sloshing.fuel import FuelState
from wing_sloshing.cg import calculate_fuel_cg


def test_static_fuel_cg():
    geometry = TankGeometry(
        length=6.0,
        width=2.0,
        height=1.0,
        compartments=3
    )

    fuel = FuelState(
        density=800.0,
        fill_fraction=0.5
    )

    cg = calculate_fuel_cg(geometry, fuel)

    assert cg["x_cg"] == 3.0
    assert cg["y_cg"] == 1.0
    assert cg["z_cg"] == 0.25
