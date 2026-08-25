import numpy as np

from wing_sloshing.vof import (
    local_tank_height,
    local_tank_width,
)


def test_root_dimensions():

    length = 1.2

    height = local_tank_height(
        np.array([0.0]),
        length,
        0.285,
        0.187,
    )

    width = local_tank_width(
        np.array([0.0]),
        length,
        1.240,
        0.813,
    )

    assert np.isclose(height[0], 0.285)
    assert np.isclose(width[0], 1.240)


def test_tip_dimensions():

    length = 1.2

    height = local_tank_height(
        np.array([length]),
        length,
        0.285,
        0.187,
    )

    width = local_tank_width(
        np.array([length]),
        length,
        1.240,
        0.813,
    )

    assert np.isclose(height[0], 0.187)
    assert np.isclose(width[0], 0.813)
