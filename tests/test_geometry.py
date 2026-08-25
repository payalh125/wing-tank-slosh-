from wing_sloshing.geometry import (
    TaperedTank,
)


def test_tank_volume():

    tank = TaperedTank(
        1.2,
        1.24,
        0.813,
        0.285,
        0.187,
    )

    calculated_volume = tank.volume()

    expected_volume = (
        0.2948894
    )

    assert abs(
        calculated_volume
        - expected_volume
    ) < 1e-6
