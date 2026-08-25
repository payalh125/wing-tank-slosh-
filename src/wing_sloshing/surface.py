import numpy as np

from scipy.optimize import brentq


def free_surface(
    x,
    z0,
    acceleration,
    gravity,
):
  

    x = np.asarray(x)

    return (
        z0
        - (acceleration / gravity) * x
    )


def local_fuel_height(
    tank,
    x,
    z0,
    acceleration,
    gravity,
):
    

    surface_height = free_surface(
        x,
        z0,
        acceleration,
        gravity,
    )

    tank_height = tank.height(x)

    return np.clip(
        surface_height,
        0.0,
        tank_height,
    )


def fuel_volume(
    tank,
    z0,
    acceleration,
    gravity,
    x_start=None,
    x_end=None,
    num_points=1000,
):
    """
    Calculate fuel volume for a specified free-surface intercept.

    tank : TaperedTank
        Tank geometry.

    z0 : float
        Free-surface elevation at x = 0.

    acceleration : float
        Longitudinal acceleration in m/s^2.

    gravity : float
        Gravitational acceleration in m/s^2.

    x_start, x_end : float
        Optional limits for analysing only part of the tank.

    num_points : int
        Number of longitudinal integration points.
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

    liquid_height = local_fuel_height(
        tank,
        x,
        z0,
        acceleration,
        gravity,
    )

    width = tank.width(x)

    cross_sectional_liquid_area = (
        width * liquid_height
    )

    return np.trapezoid(
        cross_sectional_liquid_area,
        x,
    )


def solve_free_surface(
    tank,
    target_volume,
    acceleration,
    gravity,
    x_start=None,
    x_end=None,
    num_points=1000,
):
   
    if target_volume < 0.0:
        raise ValueError(
            "Target volume cannot be negative."
        )

    if x_start is None:
        x_start = 0.0

    if x_end is None:
        x_end = tank.length

    maximum_volume = tank.volume_between(
        x_start,
        x_end,
        num_points,
    )

    tolerance = 1e-9

    if target_volume > maximum_volume + tolerance:
        raise ValueError(
            "Target volume exceeds the available tank volume."
        )

    if target_volume <= tolerance:
        return -10.0 * tank.length

    if maximum_volume - target_volume <= tolerance:
        return 10.0 * tank.length

    def volume_residual(z0):
        return (
            fuel_volume(
                tank,
                z0,
                acceleration,
                gravity,
                x_start=x_start,
                x_end=x_end,
                num_points=num_points,
            )
            - target_volume
        )

    slope = acceleration / gravity

    x_values = np.array([
        x_start,
        x_end,
    ])

    tank_heights = tank.height(x_values)

    lower_bound = (
        np.min(slope * x_values)
        - np.max(tank_heights)
        - tank.length
    )

    upper_bound = (
        np.max(tank_heights + slope * x_values)
        + tank.length
    )

    f_lower = volume_residual(
        lower_bound
    )

    f_upper = volume_residual(
        upper_bound
    )

    expansion_count = 0

    while (
        f_lower * f_upper > 0.0
        and expansion_count < 20
    ):
        span = upper_bound - lower_bound

        lower_bound -= span
        upper_bound += span

        f_lower = volume_residual(
            lower_bound
        )

        f_upper = volume_residual(
            upper_bound
        )

        expansion_count += 1

    if f_lower * f_upper > 0.0:
        raise RuntimeError(
            "Unable to bracket free-surface solution."
        )

    return brentq(
        volume_residual,
        lower_bound,
        upper_bound,
    )
