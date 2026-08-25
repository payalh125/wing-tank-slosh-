import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from wing_sloshing.geometry import TaperedTank
from wing_sloshing.fuel import Fuel
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

    fuel = Fuel(FUEL_DENSITY)

    tank_volume = tank.volume()

    print("=" * 60)
    print("STATIC TAPERED WING TANK ANALYSIS")
    print("=" * 60)

    print(f"\nTank volume = {tank_volume:.9f} m^3")

    for fill_fraction in FILL_FRACTIONS:

        target_volume = fill_fraction * tank_volume

        z0 = solve_free_surface(
            tank,
            target_volume,
            acceleration=0.0,
            gravity=GRAVITY
        )

        x_cg, y_cg, z_cg, volume = fuel_cg(
            tank,
            z0,
            acceleration=0.0,
            gravity=GRAVITY
        )

        mass = fuel.mass_from_volume(volume)

        print("\n" + "-" * 60)
        print(f"Fill fraction = {fill_fraction:.0%}")

        print(f"Fuel volume = {volume:.9f} m^3")
        print(f"Fuel mass   = {mass:.4f} kg")

        print(f"X CG = {x_cg:.6f} m")
        print(f"Y CG = {y_cg:.6f} m")
        print(f"Z CG = {z_cg:.6f} m")


if __name__ == "__main__":
    main()
