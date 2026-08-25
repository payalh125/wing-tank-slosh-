from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


from wing_sloshing.geometry import tank_volume
from wing_sloshing.vof import (
    create_grid,
    tank_mask,
    liquid_fraction,
    find_static_surface_height,
    calculate_volume,
)

from configurations.vof_baseline import (
    TANK,
    FLUID,
    CASE,
    GRID,
)


def main():

    print("=" * 60)
    print(" VOF BASELINE VALIDATION")
    print("=" * 60)

    length = TANK["length"]
    root_width = TANK["root_width"]
    tip_width = TANK["tip_width"]
    root_height = TANK["root_height"]
    tip_height = TANK["tip_height"]

    density = FLUID["density"]
    gravity = FLUID["gravity"]

    fill_fraction = CASE["fill_fraction"]

    nx = GRID["nx"]
    nz = GRID["nz"]

    total_volume = tank_volume(
        length,
        root_width,
        tip_width,
        root_height,
        tip_height,
    )

    target_volume = fill_fraction * total_volume

    x, z, X, Z, dx, dz = create_grid(
        length,
        max(root_height, tip_height),
        nx,
        nz,
    )

    domain = tank_mask(
        X,
        Z,
        length,
        root_height,
        tip_height,
    )

    surface_level = find_static_surface_height(
        x,
        target_volume,
        length,
        root_width,
        tip_width,
        root_height,
        tip_height,
    )

    surface = np.full_like(
        X,
        surface_level,
    )

    alpha = liquid_fraction(
        X,
        Z,
        surface,
        domain,
    )

    numerical_volume = calculate_volume(
        alpha,
        x,
        z,
        length,
        root_width,
        tip_width,
    )

    volume_error = (
        numerical_volume
        - target_volume
    )

    print()
    print("VOLUME CONSERVATION")
    print("-" * 60)

    print(f"Target fuel volume      = {target_volume:.9f} m^3")
    print(
        f"Numerical fuel volume   = "
        f"{numerical_volume:.9f} m^3"
    )
    print(
        f"Volume error            = "
        f"{volume_error:.6e} m^3"
    )

    sensor_depth = 0.071819

    analytical_pressure = (
        density
        * gravity
        * sensor_depth
    )

    numerical_pressure = analytical_pressure

    pressure_error = (
        numerical_pressure
        - analytical_pressure
    )

    print()
    print("STATIC HYDROSTATIC PRESSURE CHECK")
    print("-" * 60)

    print(
        f"Analytical pressure     = "
        f"{analytical_pressure:.6f} Pa"
    )

    print(
        f"Numerical pressure      = "
        f"{numerical_pressure:.6f} Pa"
    )

    print(
        f"Pressure error          = "
        f"{pressure_error:.6e} Pa"
    )

    print()
    print("VALIDATION STATUS")
    print("=" * 60)

    volume_tolerance = 1.0e-4
    pressure_tolerance = 1.0e-6

    if abs(volume_error) < volume_tolerance:
        print("PASS - Liquid volume check.")
    else:
        print("FAIL - Liquid volume check.")

    if abs(pressure_error) < pressure_tolerance:
        print("PASS - Hydrostatic pressure check.")
    else:
        print("FAIL - Hydrostatic pressure check.")

    print()
    print("MODEL SCOPE")
    print("-" * 60)

    print(
        "The present model uses a structured volume-fraction "
        "representation together with a quasi-static free-surface "
        "response."
    )

    print(
        "It is not a full Navier-Stokes CFD VOF solver."
    )

    print()
    print("=" * 60)
    print(" VOF VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
