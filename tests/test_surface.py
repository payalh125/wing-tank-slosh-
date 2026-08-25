from wing_sloshing.geometry import (
    TaperedTank,
)

from wing_sloshing.surface import (
    solve_free_surface,
    fuel_volume,
)


def test_static_volume_solution():

    tank = TaperedTank(
        1.2,
        1.24,
        0.813,
        0.285,
        0.187,
    )

    target_volume = (
        0.60 * tank.volume()
    )

    z0 = solve_free_surface(
        tank=tank,
        target_volume=target_volume,
        acceleration=0.0,
        gravity=9.81,
    )

    calculated_volume = fuel_volume(
        tank=tank,
        z0=z0,
        acceleration=0.0,
        gravity=9.81,
    )

    assert abs(
        calculated_volume
        - target_volume
    ) < 1e-6
