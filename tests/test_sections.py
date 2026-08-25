from wing_sloshing.geometry import (
    TaperedTank,
)

from wing_sloshing.sections import (
    initial_section_volumes,
)


def test_initial_section_volume_conservation():

    tank = TaperedTank(
        1.2,
        1.24,
        0.813,
        0.285,
        0.187,
    )

    total_fuel_volume = (
        0.30 * tank.volume()
    )

    left_volume, right_volume = (
        initial_section_volumes(
            tank=tank,
            total_fuel_volume=total_fuel_volume,
            section_location=0.6,
        )
    )

    reconstructed_volume = (
        left_volume
        + right_volume
    )

    assert abs(
        reconstructed_volume
        - total_fuel_volume
    ) < 1e-10
