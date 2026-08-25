from pathlib import Path

import numpy as np

from wing_sloshing.geometry import (
    TaperedTank,
)

from wing_sloshing.surface import (
    solve_free_surface,
    fuel_volume,
)

from wing_sloshing.cg import (
    fuel_cg,
)

from wing_sloshing.pressure import (
    maximum_pressure,
)

from wing_sloshing.sections import (
    initial_section_volumes,
    sealed_section_cg,
    transient_section_transfer,
)

from wing_sloshing.plotting import (
    plot_cg_comparison,
    plot_pressure_comparison,
    plot_fuel_transfer,
    plot_transient_cg,
)

from configurations.baseline import (
    TANK_LENGTH,
    ROOT_WIDTH,
    TIP_WIDTH,
    ROOT_HEIGHT,
    TIP_HEIGHT,
    FUEL_DENSITY,
    GRAVITY,
    BAFFLE_LOCATION,
    OPENING_AREA,
    DISCHARGE_COEFFICIENT,
    NUM_X,
    FILL_FRACTIONS,
    ACCELERATIONS_G,
    TRANSIENT_FILL_FRACTION,
    TRANSIENT_ACCELERATION_G,
    TRANSIENT_DURATION,
    TRANSIENT_POINTS,
)


ROOT_DIRECTORY = Path(
    __file__
).resolve().parents[1]

FIGURE_DIRECTORY = (
    ROOT_DIRECTORY
    / "results"
    / "figures"
)


def main():

    tank = TaperedTank(
        TANK_LENGTH,
        ROOT_WIDTH,
        TIP_WIDTH,
        ROOT_HEIGHT,
        TIP_HEIGHT,
    )

    total_tank_volume = tank.volume(
        NUM_X
    )

    print()
    print("=" * 60)
    print("SECTIONED TANK ANALYSIS")
    print("=" * 60)

    print(
        f"Total tank volume = "
        f"{total_tank_volume:.9f} m^3"
    )

    print(
        f"Section location = "
        f"{BAFFLE_LOCATION:.3f} m"
    )

    for fill_fraction in FILL_FRACTIONS:

        total_fuel_volume = (
            fill_fraction
            * total_tank_volume
        )

        left_initial, right_initial = (
            initial_section_volumes(
                tank=tank,
                total_fuel_volume=total_fuel_volume,
                section_location=BAFFLE_LOCATION,
                num_points=NUM_X,
            )
        )

        unrestricted_cg = []
        sealed_cg = []

        unrestricted_pressure = []
        sealed_pressure = []

        print()
        print("=" * 60)

        print(
            f"FILL FRACTION = "
            f"{fill_fraction * 100:.0f}%"
        )

        print("=" * 60)

        print(
            "Acceleration | "
            "XCG Unrestricted | "
            "XCG Sealed | "
            "MaxP Unrestricted | "
            "MaxP Sealed"
        )

        for acceleration_g in ACCELERATIONS_G:

            acceleration = (
                acceleration_g
                * GRAVITY
            )


            z0_unrestricted = solve_free_surface(
                tank=tank,
                target_volume=total_fuel_volume,
                acceleration=acceleration,
                gravity=GRAVITY,
                num_points=NUM_X,
            )

            x_unrestricted, _, _ = fuel_cg(
                tank=tank,
                z0=z0_unrestricted,
                acceleration=acceleration,
                gravity=GRAVITY,
                num_points=NUM_X,
            )

            pressure_unrestricted = maximum_pressure(
                tank=tank,
                z0=z0_unrestricted,
                acceleration=acceleration,
                density=FUEL_DENSITY,
                gravity=GRAVITY,
                num_points=NUM_X,
            )


            (
                x_sealed,
                z0_left,
                z0_right,
            ) = sealed_section_cg(
                tank=tank,
                left_volume=left_initial,
                right_volume=right_initial,
                section_location=BAFFLE_LOCATION,
                acceleration=acceleration,
                gravity=GRAVITY,
                num_points=NUM_X,
            )

            pressure_left = maximum_pressure(
                tank=tank,
                z0=z0_left,
                acceleration=acceleration,
                density=FUEL_DENSITY,
                gravity=GRAVITY,
                x_start=0.0,
                x_end=BAFFLE_LOCATION,
                num_points=NUM_X,
            )

            pressure_right = maximum_pressure(
                tank=tank,
                z0=z0_right,
                acceleration=acceleration,
                density=FUEL_DENSITY,
                gravity=GRAVITY,
                x_start=BAFFLE_LOCATION,
                x_end=tank.length,
                num_points=NUM_X,
            )

            pressure_sealed = max(
                pressure_left,
                pressure_right,
            )

            unrestricted_cg.append(
                x_unrestricted
            )

            sealed_cg.append(
                x_sealed
            )

            unrestricted_pressure.append(
                pressure_unrestricted
            )

            sealed_pressure.append(
                pressure_sealed
            )

            print(
                f"{acceleration_g:+8.2f} g | "
                f"{x_unrestricted:16.6f} | "
                f"{x_sealed:10.6f} | "
                f"{pressure_unrestricted:18.2f} | "
                f"{pressure_sealed:11.2f}"
            )

        cg_output = (
            FIGURE_DIRECTORY
            / (
                f"section_cg_"
                f"{int(fill_fraction * 100)}"
                f"percent.png"
            )
        )

        plot_cg_comparison(
            accelerations_g=ACCELERATIONS_G,
            unrestricted_cg=unrestricted_cg,
            sealed_cg=sealed_cg,
            fill_fraction=fill_fraction,
            output_path=cg_output,
        )

        pressure_output = (
            FIGURE_DIRECTORY
            / (
                f"section_pressure_"
                f"{int(fill_fraction * 100)}"
                f"percent.png"
            )
        )

        plot_pressure_comparison(
            accelerations_g=ACCELERATIONS_G,
            unrestricted_pressure=unrestricted_pressure,
            sealed_pressure=sealed_pressure,
            fill_fraction=fill_fraction,
            output_path=pressure_output,
        )

    print()
    print("=" * 60)
    print("TRANSIENT FUEL REDISTRIBUTION")
    print("=" * 60)

    transient_total_volume = (
        TRANSIENT_FILL_FRACTION
        * total_tank_volume
    )

    left_initial, right_initial = (
        initial_section_volumes(
            tank=tank,
            total_fuel_volume=transient_total_volume,
            section_location=BAFFLE_LOCATION,
            num_points=NUM_X,
        )
    )

    transient_acceleration = (
        TRANSIENT_ACCELERATION_G
        * GRAVITY
    )

    transient_results = (
        transient_section_transfer(
            tank=tank,
            initial_left_volume=left_initial,
            initial_right_volume=right_initial,
            section_location=BAFFLE_LOCATION,
            acceleration=transient_acceleration,
            density=FUEL_DENSITY,
            gravity=GRAVITY,
            opening_area=OPENING_AREA,
            discharge_coefficient=DISCHARGE_COEFFICIENT,
            duration=TRANSIENT_DURATION,
            num_points_time=TRANSIENT_POINTS,
            num_points_space=500,
        )
    )

    left_final = (
        transient_results[
            "left_volume"
        ][-1]
    )

    right_final = (
        transient_results[
            "right_volume"
        ][-1]
    )

    final_x_cg = (
        transient_results[
            "x_cg"
        ][-1]
    )

    volume_error = (
        left_final
        + right_final
        - transient_total_volume
    )

    print(
        f"Initial left volume  = "
        f"{left_initial:.9f} m^3"
    )

    print(
        f"Initial right volume = "
        f"{right_initial:.9f} m^3"
    )

    print(
        f"Final left volume    = "
        f"{left_final:.9f} m^3"
    )

    print(
        f"Final right volume   = "
        f"{right_final:.9f} m^3"
    )

    print(
        f"Final XCG            = "
        f"{final_x_cg:.6f} m"
    )

    print(
        f"Volume error         = "
        f"{volume_error:.12e} m^3"
    )

    fuel_transfer_output = (
        FIGURE_DIRECTORY
        / "transient_fuel_transfer.png"
    )

    plot_fuel_transfer(
        time=transient_results["time"],
        left_volume=transient_results["left_volume"],
        right_volume=transient_results["right_volume"],
        fill_fraction=TRANSIENT_FILL_FRACTION,
        acceleration_g=TRANSIENT_ACCELERATION_G,
        output_path=fuel_transfer_output,
    )

    cg_output = (
        FIGURE_DIRECTORY
        / "transient_cg_response.png"
    )

    plot_transient_cg(
        time=transient_results["time"],
        x_cg=transient_results["x_cg"],
        fill_fraction=TRANSIENT_FILL_FRACTION,
        acceleration_g=TRANSIENT_ACCELERATION_G,
        output_path=cg_output,
    )


if __name__ == "__main__":
    main()
