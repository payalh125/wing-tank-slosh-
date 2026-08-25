import pytest

from wing_sloshing.geometry import (
    TaperedTank,
)

from wing_sloshing.surface import (
    solve_free_surface,
    fuel_volume,
)


@pytest.mark.parametrize(
    "fill_fraction, acceleration_g",
    [
        (0.30, -0.50),
        (0.30, 0.50),
        (0.60, -0.50),
        (0.60, 0.50),
        (0.90, -0.50),
        (0.90, 0.50),
    ],
)
def test_accelerated_volume_conservation(
    fill_fraction,
    acceleration_g,
):

    tank = TaperedTank(
        1.2,
        1.24,
        0.813,
        0.285,
        0.187,
    )

    target_volume = (
        fill_fraction
        * tank.volume()
    )

    acceleration = (
        acceleration_g
        * 9.81
    )

    z0 = solve_free_surface(
        tank=tank,
        target_volume=target_volume,
        acceleration=acceleration,
        gravity=9.81,
    )

    calculated_volume = fuel_volume(
        tank=tank,
        z0=z0,
        acceleration=acceleration,
        gravity=9.81,
    )

    assert abs(
        calculated_volume
        - target_volume
    ) < 1e-6
