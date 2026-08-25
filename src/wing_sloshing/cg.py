import numpy as np

from .free_surface import liquid_depth


def fuel_cg(
    tank,
    z0,
    acceleration,
    gravity,
    x_start=0.0,
    x_end=None,
    num_points=3000
):
    """
    Calculate fuel centre of gravity.

    The liquid cross-section is represented as a rectangular column
    with local width w(x) and liquid depth d(x).
    """

    if x_end is None:
        x_end = tank.length

    x = np.linspace(x_start, x_end, num_points)

    width = tank.width(x)

    depth = liquid_depth(
        tank,
        x,
        z0,
        acceleration,
        gravity
    )

    dV_dx = width * depth

    volume = np.trapezoid(dV_dx, x)

    if volume <= 0.0:
        raise ValueError("Fuel volume must be positive.")

    x_moment = np.trapezoid(x * dV_dx, x)

    y_centroid = width / 2.0

    y_moment = np.trapezoid(
        y_centroid * dV_dx,
        x
    )

    z_centroid = depth / 2.0

    z_moment = np.trapezoid(
        z_centroid * dV_dx,
        x
    )

    x_cg = x_moment / volume
    y_cg = y_moment / volume
    z_cg = z_moment / volume

    return x_cg, y_cg, z_cg, volume
