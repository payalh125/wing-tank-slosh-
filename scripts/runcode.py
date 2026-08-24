from pathlib import Path
import sys

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from wing_sloshing.geometry import TankGeometry
from wing_sloshing.fuel import FuelState
from wing_sloshing.pressure import calculate_sensor_pressures
from wing_sloshing.cg import calculate_fuel_cg
from wing_sloshing.plotting import plot_sensor_pressures


def load_configuration(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def main():
    config_path = PROJECT_ROOT / "configs" / "baseline.yaml"
    config = load_configuration(config_path)

    geometry = TankGeometry(
        length=config["tank"]["length"],
        width=config["tank"]["width"],
        height=config["tank"]["height"],
        compartments=config["tank"]["compartments"]
    )

    fuel = FuelState(
        density=config["fuel"]["density"],
        fill_fraction=config["fuel"]["fill_fraction"]
    )

    gravity = config["gravity"]
    sensors = config["sensors"]

    fuel_volume = fuel.volume(geometry)
    fuel_mass = fuel.mass(geometry)
    fuel_height = fuel.fuel_height(geometry)

    pressures = calculate_sensor_pressures(
        sensors=sensors,
        fuel_height=fuel_height,
        density=fuel.density,
        gravity=gravity
    )

    cg = calculate_fuel_cg(
        geometry=geometry,
        fuel=fuel
    )

    print("\n--- BASELINE TANK RESULTS ---")
    print(f"Tank volume: {geometry.total_volume:.3f} m^3")
    print(f"Fuel volume: {fuel_volume:.3f} m^3")
    print(f"Fuel mass:   {fuel_mass:.3f} kg")
    print(f"Fuel height: {fuel_height:.3f} m")

    print("\n--- FUEL CENTRE OF GRAVITY ---")
    print(f"x = {cg['x_cg']:.3f} m")
    print(f"y = {cg['y_cg']:.3f} m")
    print(f"z = {cg['z_cg']:.3f} m")

    pressure_df = pd.DataFrame(pressures)

    output_csv = PROJECT_ROOT / "results" / "tables" / "baseline_pressures.csv"
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    pressure_df.to_csv(output_csv, index=False)

    output_figure = (
        PROJECT_ROOT
        / "results"
        / "figures"
        / "baseline_sensor_pressures.png"
    )

    plot_sensor_pressures(
        pressures,
        output_figure
    )

    print("\nResults written to:")
    print(output_csv)
    print(output_figure)


if __name__ == "__main__":
    main()
