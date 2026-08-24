import numpy as np


def hydrostatic_pressure(
    sensor_z: float,
    fuel_height: float,
    density: float,
    gravity: float
) -> float:
    depth = fuel_height - sensor_z

    if depth <= 0.0:
        return 0.0

    return density * gravity * depth


def calculate_sensor_pressures(
    sensors,
    fuel_height: float,
    density: float,
    gravity: float
):
    results = []

    for sensor in sensors:
        pressure = hydrostatic_pressure(
            sensor_z=sensor["z"],
            fuel_height=fuel_height,
            density=density,
            gravity=gravity
        )

        results.append(
            {
                "sensor": sensor["name"],
                "x": sensor["x"],
                "y": sensor["y"],
                "z": sensor["z"],
                "pressure_pa": pressure
            }
        )

    return results
