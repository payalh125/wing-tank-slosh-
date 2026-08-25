import numpy as np
from scipy.optimize import brentq


def local_free_surface(x, z0, acceleration, gravity):
    """
    Planar quasi-static free surface.

    For longitudinal acceleration:

        z(x) = z0 - (a/g) x
    """

    return z0 - (acceleration / gravity) * x


def liquid_depth(tank, x, z0, acceleration, gravity):
    """
    Local liquid depth, clipped to the physical tank boundaries.
    """

    z_fs = local_free_surface(x, z0, acceleration, gravity)

    h = tank.height(x)

    return np.clip(z_fs, 0.0, h)


def fuel_volume(
    tank,
    z0,
    acceleration,
    gravity,
    x_start=0.0,
    x_end=None,
    num_points=2000
):
    """
    Compute liquid volume beneath the free surface.
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

    area = width * depth

    return np.trapezoid(area, x)


def solve_free_surface(
    tank,
    target_volume,
    acceleration,
    gravity,
    x_start=0.0,
    x_end=None
):
    """
    Solve for the free-surface intercept z0 such that the liquid
    volume equals target_volume.
    """

    if x_end is None:
        x_end = tank.length

    x_test = np.array([x_start, x_end])

    h_test = tank.height(x_test)

    z_min = np.min(h_test) - abs(acceleration / gravity) * tank.length - 1.0

    z_max = np.max(h_test) + abs(acceleration / gravity) * tank.length + 1.0

    def residual(z0):

        volume = fuel_volume(
            tank,
            z0,
            acceleration,
            gravity,
            x_start,
            x_end
        )

        return volume - target_volume

    return brentq(residual, z_min, z_max)


def free_surface_solution(
    tank,
    target_volume,
    acceleration,
    gravity
):
    """
    Convenience function returning the solved z0 and resulting volume.
    """

    z0 = solve_free_surface(
        tank,
        target_volume,
        acceleration,
        gravity
    )

    volume = fuel_volume(
        tank,
        z0,
        acceleration,
        gravity
    )

    return z0, volume
