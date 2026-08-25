import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from wing_sloshing.geometry import TaperedTank
from wing_sloshing.free_surface import solve_free_surface
from wing_sloshing.cg import fuel_cg

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
    print("QUASI-STATIC LONGITUDINAL ACCELERATION ANALYSIS")
    print("=" * 60)

    for fill_fraction in FILL_FRACTIONS:

        fuel_volume = fill_fraction * tank_volume

        print("\n")
        print("=" * 60)
        print(f"FILL FRACTION = {fill_fraction:.0%}")
        print("=" * 60)

        for acceleration_g in ACCELERATIONS_G:

            acceleration = acceleration_g * GRAVITY

            z0 = solve_free_surface(
                tank,
                fuel_volume,
                acceleration,
                GRAVITY
            )

            x_cg, y_cg, z_cg, solved_volume = fuel_cg(
                tank,
                z0,
                acceleration,
                GRAVITY
            )

            volume_error = solved_volume - fuel_volume

            print(
                f"a = {acceleration_g:+.2f} g | "
                f"XCG = {x_cg:.6f} m | "
                f"YCG = {y_cg:.6f} m | "
                f"ZCG = {z_cg:.6f} m | "
                f"Volume error = {volume_error:.3e} m^3"
            )


if __name__ == "__main__":
    main()
