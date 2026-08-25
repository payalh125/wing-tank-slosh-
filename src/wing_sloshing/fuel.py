class Fuel:
    """
    Fuel properties and basic mass calculations.
    """

    def __init__(self, density):
        self.density = density

    def mass_from_volume(self, volume):
        return self.density * volume

    def volume_from_mass(self, mass):
        return mass / self.density
