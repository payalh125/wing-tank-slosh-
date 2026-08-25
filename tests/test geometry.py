import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1] / "src")
)

from wing_sloshing.geometry import TaperedTank


def test_baseline_tank_volume():

    tank = TaperedTank(
        length=1.2,
        root_width=1.24,
        tip_width=0.813,
        root_height=0.285,
        tip_height=0.187
    )

    expected_volume = 0.2948894

    calculated_volume = tank.volume()

    assert abs(
        calculated_volume - expected_volume
    ) < 1e-6
