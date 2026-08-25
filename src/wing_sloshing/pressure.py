import numpy as np


def hydrostatic_pressure(
    sensor_x,
    sensor_z,
    z0,
    acceleration,
    density,
    gravity
):
    """
    Quasi-static gauge pressure at a sensor.

    The local free-surface elevation is:

        z_fs = z0 - (a/g)x

    Gauge pressure is:

        p = rho g (z_fs - z_sensor)

    Pressure is zero when the sensor is above the liquid.
    """

    z_free_surface = (
        z0
        - (acceleration / gravity) * sensor_x
    )

    pressure_head = z_free_surface - sensor_z

    return max(
        0.0,
        density * gravity * pressure_head
    )


def sensor_pressures(
    sensors,
    z0,
    acceleration,
    density,
    gravity
):
    """
    Calculate pressure at multiple sensors.

    sensors should be a dictionary:

    {
        "P1": {"x": ..., "z": ...},
        ...
    }
    """

    results = {}

    for name, location in sensors.items():

        results[name] = hydrostatic_pressure(
            sensor_x=location["x"],
            sensor_z=location["z"],
            z0=z0,
            acceleration=acceleration,
            density=density,
            gravity=gravity
        )

    return results
