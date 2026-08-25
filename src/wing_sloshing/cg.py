import numpy as np

from .surface import local_fuel_height


def fuel_cg(
    tank,
    z0,
    acceleration,
    gravity,
    x_start=None,
    x_end=None,
    num_points=1000,
):

    if x_start is None:
        x_start = 0.0

    if x_end is None:
        x_end = tank.length

    x = np.linspace(
        x_start,
        x_end,
        num_points,
    )

    liquid_height = local_fuel_height(
        tank,
        x,
        z0,
        acceleration,
        gravity,
    )

    width = tank.width(x)

    differential_volume = (
        width * liquid_height
    )

    volume = np.trapezoid(
        differential_volume,
        x,
    )

    if volume <= 0.0:
        raise ValueError(
            "Fuel volume must be greater than zero."
        )

    x_moment = np.trapezoid(
        x * differential_volume,
        x,
    )

    x_cg = x_moment / volume

    y_cg = 0.0

    vertical_centroid = (
        liquid_height / 2.0
    )

    z_moment = np.trapezoid(
        vertical_centroid
        * differential_volume,
        x,
    )

    z_cg = z_moment / volume

    return (
        x_cg,
        y_cg,
        z_cg,
    )
