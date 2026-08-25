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

from configurations.baseline import (
    TANK_LENGTH,
    ROOT_WIDTH,
    TIP_WIDTH,
    ROOT_HEIGHT,
    TIP_HEIGHT,
    GRAVITY,
    NUM_X,
)


def main():

    tank = TaperedTank(
        TANK_LENGTH,
        ROOT_WIDTH,
        TIP_WIDTH,
        ROOT_HEIGHT,
        TIP_HEIGHT,
    )

    total_volume = tank.volume(
        NUM_X
    )

    target_volume = (
        0.60 * total_volume
    )

    z0 = solve_free_surface(
        tank=tank,
        target_volume=target_volume,
        acceleration=0.0,
        gravity=GRAVITY,
        num_points=NUM_X,
    )

    calculated_volume = fuel_volume(
        tank=tank,
        z0=z0,
        acceleration=0.0,
        gravity=GRAVITY,
        num_points=NUM_X,
    )

    x_cg, y_cg, z_cg = fuel_cg(
        tank=tank,
        z0=z0,
        acceleration=0.0,
        gravity=GRAVITY,
        num_points=NUM_X,
    )

    volume_error = (
        calculated_volume
        - target_volume
    )

    print()
    print("=" * 60)
    print("STATIC FUEL DISTRIBUTION ANALYSIS")
    print("=" * 60)

    print(
        f"Tank volume      = "
        f"{total_volume:.9f} m^3"
    )

    print(
        f"Fuel volume      = "
        f"{target_volume:.9f} m^3"
    )

    print(
        f"Calculated volume = "
        f"{calculated_volume:.9f} m^3"
    )

    print(
        f"Volume error      = "
        f"{volume_error:.12e} m^3"
    )

    print()

    print(
        f"Fuel XCG = "
        f"{x_cg:.6f} m"
    )

    print(
        f"Fuel YCG = "
        f"{y_cg:.6f} m"
    )

    print(
        f"Fuel ZCG = "
        f"{z_cg:.6f} m"
    )


if __name__ == "__main__":
    main()

