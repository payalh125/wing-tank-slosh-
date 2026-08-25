import numpy as np


class TaperedTank:
    """
    Linearly tapered wing fuel tank.

    The tank width and height vary linearly along the longitudinal
    coordinate x.
    """

    def __init__(
        self,
        length,
        root_width,
        tip_width,
        root_height,
        tip_height
    ):
        self.length = length
        self.root_width = root_width
        self.tip_width = tip_width
        self.root_height = root_height
        self.tip_height = tip_height

    def width(self, x):
        x = np.asarray(x)

        return (
            self.root_width
            + (self.tip_width - self.root_width)
            * x / self.length
        )

    def height(self, x):
        x = np.asarray(x)

        return (
            self.root_height
            + (self.tip_height - self.root_height)
            * x / self.length
        )

    def cross_section_area(self, x):
        return self.width(x) * self.height(x)

    def volume(self, num_points=10000):
        x = np.linspace(0.0, self.length, num_points)

        area = self.cross_section_area(x)

        return np.trapezoid(area, x)

    def coordinates(self, num_points=1000):
        return np.linspace(0.0, self.length, num_points)
