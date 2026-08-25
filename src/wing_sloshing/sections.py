import numpy as np

from scipy.integrate import solve_ivp

from .surface import (
    solve_free_surface,
    free_surface,
)
from .cg import fuel_cg


def initial_section_volumes(
    tank,
    total_fuel_volume,
    section_location,
    num_points=1000,
):
    """
    Divide the initial fuel volume between the left and
    right sections according to their geometric volume.

    """

    left_capacity = tank.volume_between(
        0.0,
        section_location,
        num_points,
    )

    right_capacity = tank.volume_between(
        section_location,
        tank.length,
        num_points,
    )

    total_capacity = (
        left_capacity
        + right_capacity
    )

    left_fraction = (
        left_capacity / total_capacity
    )

    left_volume = (
        total_fuel_volume
        * left_fraction
    )

    right_volume = (
        total_fuel_volume
        - left_volume
    )

    return (
        left_volume,
        right_volume,
    )


def sealed_section_cg(
    tank,
    left_volume,
    right_volume,
    section_location,
    acceleration,
    gravity,
    num_points=1000,
):
    """
    Calculate the overall fuel CG when the two sections
    retain fixed fuel volumes.
    """

    z0_left = solve_free_surface(
        tank,
        left_volume,
        acceleration,
        gravity,
        x_start=0.0,
        x_end=section_location,
        num_points=num_points,
    )

    z0_right = solve_free_surface(
        tank,
        right_volume,
        acceleration,
        gravity,
        x_start=section_location,
        x_end=tank.length,
        num_points=num_points,
    )

    x_left, _, _ = fuel_cg(
        tank,
        z0_left,
        acceleration,
        gravity,
        x_start=0.0,
        x_end=section_location,
        num_points=num_points,
    )

    x_right, _, _ = fuel_cg(
        tank,
        z0_right,
        acceleration,
        gravity,
        x_start=section_location,
        x_end=tank.length,
        num_points=num_points,
    )

    total_volume = (
        left_volume
        + right_volume
    )

    x_cg = (
        x_left * left_volume
        + x_right * right_volume
    ) / total_volume

    return (
        x_cg,
        z0_left,
        z0_right,
    )


def section_pressures_at_opening(
    tank,
    left_volume,
    right_volume,
    section_location,
    acceleration,
    density,
    gravity,
    num_points=1000,
):
    """
    Calculate the pressure difference across the lower
    opening between the two sections.
    """

    z0_left = solve_free_surface(
        tank,
        left_volume,
        acceleration,
        gravity,
        x_start=0.0,
        x_end=section_location,
        num_points=num_points,
    )

    z0_right = solve_free_surface(
        tank,
        right_volume,
        acceleration,
        gravity,
        x_start=section_location,
        x_end=tank.length,
        num_points=num_points,
    )

    left_surface = free_surface(
        section_location,
        z0_left,
        acceleration,
        gravity,
    )

    right_surface = free_surface(
        section_location,
        z0_right,
        acceleration,
        gravity,
    )

    pressure_left = max(
        0.0,
        density
        * gravity
        * left_surface,
    )

    pressure_right = max(
        0.0,
        density
        * gravity
        * right_surface,
    )

    return (
        pressure_left,
        pressure_right,
    )


def transient_section_transfer(
    tank,
    initial_left_volume,
    initial_right_volume,
    section_location,
    acceleration,
    density,
    gravity,
    opening_area,
    discharge_coefficient,
    duration,
    num_points_time=250,
    num_points_space=500,
):
    
    total_volume = (
        initial_left_volume
        + initial_right_volume
    )

    left_capacity = tank.volume_between(
        0.0,
        section_location,
        num_points_space,
    )

    right_capacity = tank.volume_between(
        section_location,
        tank.length,
        num_points_space,
    )

    def flow_rate(
        left_volume,
        right_volume,
    ):
        left_volume = np.clip(
            left_volume,
            0.0,
            left_capacity,
        )

        right_volume = np.clip(
            right_volume,
            0.0,
            right_capacity,
        )

        pressure_left, pressure_right = (
            section_pressures_at_opening(
                tank=tank,
                left_volume=left_volume,
                right_volume=right_volume,
                section_location=section_location,
                acceleration=acceleration,
                density=density,
                gravity=gravity,
                num_points=num_points_space,
            )
        )

        pressure_difference = (
            pressure_left
            - pressure_right
        )

        if abs(pressure_difference) < 1e-6:
            return 0.0

        magnitude = (
            discharge_coefficient
            * opening_area
            * np.sqrt(
                2.0
                * abs(pressure_difference)
                / density
            )
        )

        return (
            np.sign(
                pressure_difference
            )
            * magnitude
        )

    def derivatives(
        time,
        state,
    ):
        left_volume = state[0]

        right_volume = (
            total_volume
            - left_volume
        )

        q = flow_rate(
            left_volume,
            right_volume,
        )

        if (
            left_volume <= 0.0
            and q > 0.0
        ):
            q = 0.0

        if (
            right_volume <= 0.0
            and q < 0.0
        ):
            q = 0.0

        return [-q]

    time = np.linspace(
        0.0,
        duration,
        num_points_time,
    )

    solution = solve_ivp(
        derivatives,
        (
            0.0,
            duration,
        ),
        [initial_left_volume],
        t_eval=time,
        rtol=1e-7,
        atol=1e-9,
    )

    left_volume = np.clip(
        solution.y[0],
        0.0,
        left_capacity,
    )

    right_volume = (
        total_volume
        - left_volume
    )

    x_cg = np.zeros_like(
        solution.t
    )

    for index in range(
        len(solution.t)
    ):
        current_left_volume = (
            left_volume[index]
        )

        current_right_volume = (
            right_volume[index]
        )

        if current_left_volume > 1e-9:

            z0_left = solve_free_surface(
                tank,
                current_left_volume,
                acceleration,
                gravity,
                x_start=0.0,
                x_end=section_location,
                num_points=num_points_space,
            )

            x_left, _, _ = fuel_cg(
                tank,
                z0_left,
                acceleration,
                gravity,
                x_start=0.0,
                x_end=section_location,
                num_points=num_points_space,
            )

        else:
            x_left = 0.0

        if current_right_volume > 1e-9:

            z0_right = solve_free_surface(
                tank,
                current_right_volume,
                acceleration,
                gravity,
                x_start=section_location,
                x_end=tank.length,
                num_points=num_points_space,
            )

            x_right, _, _ = fuel_cg(
                tank,
                z0_right,
                acceleration,
                gravity,
                x_start=section_location,
                x_end=tank.length,
                num_points=num_points_space,
            )

        else:
            x_right = 0.0

        x_cg[index] = (
            x_left * current_left_volume
            + x_right * current_right_volume
        ) / total_volume

    return {
        "time": solution.t,
        "left_volume": left_volume,
        "right_volume": right_volume,
        "x_cg": x_cg,
    }
