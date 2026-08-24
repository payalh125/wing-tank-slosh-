from pathlib import Path

import matplotlib.pyplot as plt


def plot_sensor_pressures(data, output_path):
    names = [item["sensor"] for item in data]
    pressures = [item["pressure_pa"] for item in data]

    plt.figure(figsize=(8, 5))
    plt.bar(names, pressures)

    plt.xlabel("Pressure sensor")
    plt.ylabel("Gauge pressure [Pa]")
    plt.title("Hydrostatic pressure at sensor locations")

    plt.grid(axis="y")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
