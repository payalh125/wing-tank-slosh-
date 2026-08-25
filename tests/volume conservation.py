import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from wing_sloshing.geometry import TaperedTank
from wing_sloshing.free_surface import (
    solve_free_surface,
    fuel_volume
)


def test_accelerated_volume_conservation():

    tank = TaperedTank(
        1.2,
        1.24,
        0.813,
        0.285,
        0.187
    )

    tank_volume = tank.volume()

    fill_fraction = 0.3

    target_volume = fill_fraction * tank_volume

    acceleration = 0.5 * 9.81

    z0 = solve_free_surface(
        tank,
        target_volume,
        acceleration,
        gravity=9.81
    )

    calculated_volume = fuel_volume(
        tank,
        z0,
        acceleration,
        gravity=9.81
    )

    assert abs(
        calculated_volume - target_volume
    ) < 1e-6
