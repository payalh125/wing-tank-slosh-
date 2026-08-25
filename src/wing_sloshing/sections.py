from .free_surface import (
    fuel_volume,
    solve_free_surface
)

from .cg import fuel_cg


def compartment_static_volumes(
    tank,
    total_fuel_volume,
    baffle_location
):
    """
    Determine initial fuel distribution between two compartments
    under zero acceleration.
    """

    z0 = solve_free_surface(
        tank,
        total_fuel_volume,
        acceleration=0.0,
        gravity=9.81
    )

    left_volume = fuel_volume(
        tank,
        z0,
        acceleration=0.0,
        gravity=9.81,
        x_start=0.0,
        x_end=baffle_location
    )

    right_volume = fuel_volume(
        tank,
        z0,
        acceleration=0.0,
        gravity=9.81,
        x_start=baffle_location,
        x_end=tank.length
    )

    return z0, left_volume, right_volume


def sealed_compartment_cg(
    tank,
    left_volume,
    right_volume,
    acceleration,
    gravity,
    baffle_location
):
    """
    Calculate CG when fuel cannot redistribute across the baffle.
    """

    z0_left = solve_free_surface(
        tank,
        left_volume,
        acceleration,
        gravity,
        x_start=0.0,
        x_end=baffle_location
    )

    z0_right = solve_free_surface(
        tank,
        right_volume,
        acceleration,
        gravity,
        x_start=baffle_location,
        x_end=tank.length
    )

    xL, yL, zL, VL = fuel_cg(
        tank,
        z0_left,
        acceleration,
        gravity,
        x_start=0.0,
        x_end=baffle_location
    )

    xR, yR, zR, VR = fuel_cg(
        tank,
        z0_right,
        acceleration,
        gravity,
        x_start=baffle_location,
        x_end=tank.length
    )

    total_volume = VL + VR

    x_cg = (xL * VL + xR * VR) / total_volume
    y_cg = (yL * VL + yR * VR) / total_volume
    z_cg = (zL * VL + zR * VR) / total_volume

    return x_cg, y_cg, z_cg, total_volume
