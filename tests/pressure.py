from wing_sloshing.pressure import hydrostatic_pressure


def test_pressure_at_bottom():
    pressure = hydrostatic_pressure(
        sensor_z=0.0,
        fuel_height=1.0,
        density=1000.0,
        gravity=9.81
    )

    assert pressure == 9810.0


def test_pressure_above_surface():
    pressure = hydrostatic_pressure(
        sensor_z=1.2,
        fuel_height=1.0,
        density=1000.0,
        gravity=9.81
    )

    assert pressure == 0.0
