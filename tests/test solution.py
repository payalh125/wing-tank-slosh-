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


def test_static_volume_conservation():

    tank = TaperedTank(
        1.2,
        1.24,
        0.813,
        0.285,
        0.187
    )

    total_volume = tank.volume()

    target_volume = 0.6 * total_volume

    z0 = solve_free_surface(
        tank,
        target_volume,
        acceleration=0.0,
        gravity=9.81
    )

    calculated_volume = fuel_volume(
        tank,
        z0,
        acceleration=0.0,
        gravity=9.81
    )

    assert abs(
        calculated_volume - target_volume
    ) < 1e-6
