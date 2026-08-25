from pathlib import Path
import sys

import numpy as np
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


from wing_sloshing.geometry import tank_volume
from wing_sloshing.vof import (
    create_grid,
    tank_mask,
    liquid_fraction,
    adjust_surface_for_volume,
    calculate_volume,
    calculate_xcg,
)

from configurations.vof_baseline import (
    TANK,
    FLUID,
    CASE,
    GRID,
)


def main():

    print("=" * 60)
    print(" BASELINE VOF FREE-SURFACE REPRESENTATION")
    print("=" * 60)

    length = TANK["length"]
    root_width = TANK["root_width"]
    tip_width = TANK["tip_width"]
    root_height = TANK["root_height"]
    tip_height = TANK["tip_height"]

    density = FLUID["density"]
    gravity = FLUID["gravity"]

    fill_fraction = CASE["fill_fraction"]
    amplitude = CASE["amplitude"]
    frequency = CASE["frequency"]
    simulation_time = CASE["simulation_time"]
    time_step = CASE["time_step"]

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

    print()
    print("TANK GEOMETRY")
    print("-" * 60)

    print(f"Tank length             = {length:.6f} m")
    print(f"Root-side width         = {root_width:.6f} m")
    print(f"Tip-side width          = {tip_width:.6f} m")
    print(f"Root-side height        = {root_height:.6f} m")
    print(f"Tip-side height         = {tip_height:.6f} m")

    print()
    print("FILL CONDITION")
    print("-" * 60)

    print(f"Fill fraction           = {fill_fraction * 100:.1f} %")
    print(f"Target fuel volume      = {target_volume:.9f} m^3")
    print(
        f"Target fuel mass        = "
        f"{density * target_volume:.6f} kg"
    )

    print()
    print("EXCITATION CONDITION")
    print("-" * 60)

    print(f"Amplitude               = {amplitude:.6f} m")
    print(f"Frequency               = {frequency:.6f} Hz")
    print(f"Simulation time         = {simulation_time:.6f} s")
    print(f"Time step               = {time_step:.6f} s")

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

    time = np.arange(
        0.0,
        simulation_time + time_step,
        time_step,
    )

    xcg_history = np.zeros(len(time))
    volume_history = np.zeros(len(time))

    omega = 2.0 * np.pi * frequency

    for i, current_time in enumerate(time):

        acceleration = (
            -amplitude
            * omega**2
            * np.sin(omega * current_time)
        )

        surface = adjust_surface_for_volume(
            x,
            target_volume,
            acceleration,
            length,
            root_width,
            tip_width,
            root_height,
            tip_height,
            gravity,
        )

        surface_2d = np.tile(
            surface,
            (len(z), 1),
        )

        alpha = liquid_fraction(
            X,
            Z,
            surface_2d,
            domain,
        )

        xcg_history[i] = calculate_xcg(
            alpha,
            X,
            Z,
            x,
            z,
            length,
            root_width,
            tip_width,
        )

        volume_history[i] = calculate_volume(
            alpha,
            x,
            z,
            length,
            root_width,
            tip_width,
        )

    print()
    print("SIMULATION COMPLETED")

    final_volume = volume_history[-1]

    volume_error = np.max(
        np.abs(volume_history - target_volume)
    )

    print()
    print("VOLUME RESULTS")
    print("-" * 60)

    print(f"Target fuel volume      = {target_volume:.9f} m^3")
    print(f"Final fuel volume       = {final_volume:.9f} m^3")
    print(f"Maximum volume error    = {volume_error:.6e} m^3")

    print()
    print("CG RESPONSE")
    print("-" * 60)

    print(f"Initial XCG             = {xcg_history[0]:.6f} m")
    print(f"Minimum XCG             = {np.min(xcg_history):.6f} m")
    print(f"Maximum XCG             = {np.max(xcg_history):.6f} m")

    excursion = (
        np.max(xcg_history)
        - np.min(xcg_history)
    )

    print(f"Total XCG excursion     = {excursion:.6f} m")

    results_dir = ROOT / "results" / "vof"

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure()

    plt.plot(
        time,
        xcg_history,
    )

    plt.xlabel("Time [s]")
    plt.ylabel("Fuel XCG [m]")
    plt.title("Baseline VOF Free-Surface XCG Response")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        results_dir / "vof_xcg_response.png",
        dpi=300,
    )

    plt.close()

    plt.figure()

    plt.plot(
        time,
        volume_history,
    )

    plt.axhline(
        target_volume,
        linestyle="--",
    )

    plt.xlabel("Time [s]")
    plt.ylabel("Liquid volume [m³]")
    plt.title("VOF Volume Conservation Check")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        results_dir / "vof_volume_conservation.png",
        dpi=300,
    )

    plt.close()

    print()
    print("Figures saved to:")
    print(results_dir)

    print()
    print("=" * 60)
    print(" VOF BASELINE CASE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
