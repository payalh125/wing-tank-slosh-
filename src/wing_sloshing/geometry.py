import numpy as np


class TaperedTank:


    def __init__(
        self,
        length,
        root_width,
        tip_width,
        root_height,
        tip_height,
    ):
        self.length = float(length)

        self.root_width = float(root_width)
        self.tip_width = float(tip_width)

        self.root_height = float(root_height)
        self.tip_height = float(tip_height)

    def width(self, x):
        x = np.asarray(x)

        return (
            self.root_width
            + (
                self.tip_width - self.root_width
            )
            * x / self.length
        )

    def height(self, x):
        x = np.asarray(x)

        return (
            self.root_height
            + (
                self.tip_height - self.root_height
            )
            * x / self.length
        )

    def cross_section_area(self, x):
        return self.width(x) * self.height(x)

    def coordinates(self, num_points=1000):
        return np.linspace(
            0.0,
            self.length,
            num_points,
        )

    def volume_between(
        self,
        x_start,
        x_end,
        num_points=1000,
    ):
        x = np.linspace(
            x_start,
            x_end,
            num_points,
        )

        area = self.cross_section_area(x)

        return np.trapezoid(area, x)

    def volume(self, num_points=1000):
        return self.volume_between(
            0.0,
            self.length,
            num_points,
        )
