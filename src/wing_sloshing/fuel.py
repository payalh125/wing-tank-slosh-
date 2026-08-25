def fuel_mass(
    volume,
    density,
):
    """
    Calculate fuel mass from fuel volume.
    """

    return volume * density


def fuel_volume(
    mass,
    density,
):
    """
    Calculate fuel volume from fuel mass.
    """

    if density <= 0.0:
        raise ValueError(
            "Fuel density must be greater than zero."
        )

    return mass / density
