import numpy as np

from .surface import free_surface


def hydrostatic_pressure(
    sensor_x,
    sensor_z,
    z0,
    acceleration,
    density,
    gravity,
):


    z_free_surface = free_surface(
        sensor_x,
        z0,
        acceleration,
        gravity,
    )

    pressure_head = (
        z_free_surface - sensor_z
    )

    return max(
        0.0,
        density
        * gravity
        * pressure_head,
    )


def sensor_pressures(
    sensors,
    z0,
    acceleration,
    density,
    gravity,
):
    """
    Calculate pressure at multiple sensors.
    """

    results = {}

    for name, location in sensors.items():

        results[name] = hydrostatic_pressure(
            sensor_x=location["x"],
            sensor_z=location["z"],
            z0=z0,
            acceleration=acceleration,
            density=density,
            gravity=gravity,
        )

    return results


def maximum_pressure(
    tank,
    z0,
    acceleration,
    density,
    gravity,
    x_start=None,
    x_end=None,
    num_points=1000,
):
    """
    Calculate the maximum hydrostatic pressure along
    the lower surface of the selected tank region.
    """

    if x_start is None:
        x_start = 0.0

    if x_end is None:
        x_end = tank.length

    x = np.linspace(
        x_start,
        x_end,
        num_points,
    )

    z_surface = free_surface(
        x,
        z0,
        acceleration,
        gravity,
    )

    local_height = tank.height(x)

    fuel_present = (
        z_surface > 0.0
    )

    pressure = np.where(
        fuel_present,
        density
        * gravity
        * np.maximum(
            z_surface,
            0.0,
        ),
        0.0,
    )

    return float(
        np.max(pressure)
    )
