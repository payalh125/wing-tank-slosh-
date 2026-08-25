import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from wing_sloshing.geometry import TaperedTank
from wing_sloshing.free_surface import solve_free_surface
from wing_sloshing.cg import fuel_cg
from wing_sloshing.compartments import (
    compartment_static_volumes,
    sealed_compartment_cg
)

from configurations.baseline_tank import *


def main():

    tank = TaperedTank(
        TANK_LENGTH,
        ROOT_WIDTH,
        TIP_WIDTH,
        ROOT_HEIGHT,
        TIP_HEIGHT
    )

    tank_volume = tank.volume()

    print("=" * 60)
    print("COMPARTMENT-LIMITED FUEL REDISTRIBUTION")
    print("=" * 60)

    for fill_fraction in FILL_FRACTIONS:

        fuel_volume = fill_fraction * tank_volume

        _, left_volume, right_volume = (
            compartment_static_volumes(
                tank,
                fuel_volume,
                BAFFLE_LOCATION
            )
        )

        print("\n")
        print("=" * 60)
        print(f"FILL FRACTION = {fill_fraction:.0%}")
        print("=" * 60)

        print(f"Initial left volume  = {left_volume:.9f} m^3")
        print(f"Initial right volume = {right_volume:.9f} m^3")

        for acceleration_g in ACCELERATIONS_G:

            acceleration = acceleration_g * GRAVITY

            z0 = solve_free_surface(
                tank,
                fuel_volume,
                acceleration,
                GRAVITY
            )

            unrestricted = fuel_cg(
                tank,
                z0,
                acceleration,
                GRAVITY
            )

            sealed = sealed_compartment_cg(
                tank,
                left_volume,
                right_volume,
                acceleration,
                GRAVITY,
                BAFFLE_LOCATION
            )

            print(
                f"\na = {acceleration_g:+.2f} g"
            )

            print(
                f"Unrestricted XCG = "
                f"{unrestricted[0]:.6f} m"
            )

            print(
                f"Compartment XCG = "
                f"{sealed[0]:.6f} m"
            )


if __name__ == "__main__":
    main()
