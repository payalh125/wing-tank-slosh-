from pathlib import Path

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
    sensor_pressures,
)

from wing_sloshing.plotting import (
    plot_sensor_response,
)

from configurations.baseline import (
    TANK_LENGTH,
    ROOT_WIDTH,
    TIP_WIDTH,
    ROOT_HEIGHT,
    TIP_HEIGHT,
    FUEL_DENSITY,
    GRAVITY,
    NUM_X,
    FILL_FRACTIONS,
    ACCELERATIONS_G,
    PRESSURE_SENSORS,
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

    tank_volume = tank.volume(
        NUM_X
    )

    print()
    print("=" * 60)
    print("ACCELERATED FUEL DISTRIBUTION ANALYSIS")
    print("=" * 60)

    for fill_fraction in FILL_FRACTIONS:

        target_volume = (
            fill_fraction
            * tank_volume
        )

        x_cg_results = []

        sensor_results = {
            name: []
            for name in PRESSURE_SENSORS
        }

        print()
        print(
            f"FILL FRACTION = "
            f"{fill_fraction * 100:.0f}%"
        )

        print("-" * 60)

        for acceleration_g in ACCELERATIONS_G:

            acceleration = (
                acceleration_g
                * GRAVITY
            )

            z0 = solve_free_surface(
                tank=tank,
                target_volume=target_volume,
                acceleration=acceleration,
                gravity=GRAVITY,
                num_points=NUM_X,
            )

            calculated_volume = fuel_volume(
                tank=tank,
                z0=z0,
                acceleration=acceleration,
                gravity=GRAVITY,
                num_points=NUM_X,
            )

            x_cg, _, _ = fuel_cg(
                tank=tank,
                z0=z0,
                acceleration=acceleration,
                gravity=GRAVITY,
                num_points=NUM_X,
            )

            pressures = sensor_pressures(
                sensors=PRESSURE_SENSORS,
                z0=z0,
                acceleration=acceleration,
                density=FUEL_DENSITY,
                gravity=GRAVITY,
            )

            volume_error = (
                calculated_volume
                - target_volume
            )

            x_cg_results.append(
                x_cg
            )

            for sensor_name in PRESSURE_SENSORS:

                sensor_results[
                    sensor_name
                ].append(
                    pressures[sensor_name]
                )

            print(
                f"a = {acceleration_g:+.2f} g | "
                f"XCG = {x_cg:.6f} m | "
                f"Volume error = "
                f"{volume_error:.3e} m^3"
            )

        output_path = (
            FIGURE_DIRECTORY
            / (
                f"sensor_response_"
                f"{int(fill_fraction * 100)}"
                f"percent.png"
            )
        )

        plot_sensor_response(
            accelerations_g=ACCELERATIONS_G,
            pressure_results=sensor_results,
            fill_fraction=fill_fraction,
            output_path=output_path,
        )


if __name__ == "__main__":
    main()
