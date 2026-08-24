from dataclasses import dataclass

from .geometry import TankGeometry


@dataclass
class FuelState:
    density: float
    fill_fraction: float

    def volume(self, geometry: TankGeometry) -> float:
        return geometry.total_volume * self.fill_fraction

    def mass(self, geometry: TankGeometry) -> float:
        return self.density * self.volume(geometry)

    def fuel_height(self, geometry: TankGeometry) -> float:
        return geometry.height * self.fill_fraction
