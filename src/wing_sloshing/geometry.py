from dataclasses import dataclass


@dataclass
class TankGeometry:
    length: float
    width: float
    height: float
    compartments: int

    @property
    def total_volume(self) -> float:
        return self.length * self.width * self.height

    @property
    def compartment_length(self) -> float:
        return self.length / self.compartments
