from pathlib import Path

import matplotlib.pyplot as plt


def prepare_output_path(
    output_path,
):


    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return output_path


def plot_cg_comparison(
    accelerations_g,
    unrestricted_cg,
    sealed_cg,
    fill_fraction,
    output_path,
):
    output_path = prepare_output_path(
        output_path
    )

    plt.figure(
        figsize=(9, 6)
    )

    plt.plot(
        accelerations_g,
        unrestricted_cg,
        marker="o",
        label="Unrestricted",
    )

    plt.plot(
        accelerations_g,
        sealed_cg,
        marker="s",
        label="Sealed Section",
    )

    plt.xlabel(
        "Longitudinal Acceleration [g]"
    )

    plt.ylabel(
        "Fuel XCG [m]"
    )

    plt.title(
        f"Fuel CG Response - "
        f"{fill_fraction * 100:.0f}% Fill"
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.close()


def plot_pressure_comparison(
    accelerations_g,
    unrestricted_pressure,
    sealed_pressure,
    fill_fraction,
    output_path,
):
    output_path = prepare_output_path(
        output_path
    )

    plt.figure(
        figsize=(9, 6)
    )

    plt.plot(
        accelerations_g,
        unrestricted_pressure,
        marker="o",
        label="Unrestricted",
    )

    plt.plot(
        accelerations_g,
        sealed_pressure,
        marker="s",
        label="Sealed Section",
    )

    plt.xlabel(
        "Longitudinal Acceleration [g]"
    )

    plt.ylabel(
        "Maximum Sensor Pressure [Pa]"
    )

    plt.title(
        f"Maximum Pressure Response - "
        f"{fill_fraction * 100:.0f}% Fill"
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.close()


def plot_sensor_response(
    accelerations_g,
    pressure_results,
    fill_fraction,
    output_path,
):
    output_path = prepare_output_path(
        output_path
    )

    plt.figure(
        figsize=(9, 6)
    )

    for sensor_name, values in pressure_results.items():

        plt.plot(
            accelerations_g,
            values,
            marker="o",
            label=sensor_name,
        )

    plt.xlabel(
        "Longitudinal Acceleration [g]"
    )

    plt.ylabel(
        "Gauge Pressure [Pa]"
    )

    plt.title(
        f"Pressure Sensor Response at "
        f"{fill_fraction * 100:.0f}% Fill"
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.close()


def plot_fuel_transfer(
    time,
    left_volume,
    right_volume,
    fill_fraction,
    acceleration_g,
    output_path,
):
    output_path = prepare_output_path(
        output_path
    )

    plt.figure(
        figsize=(9, 6)
    )

    plt.plot(
        time,
        left_volume,
        label="Left Section",
    )

    plt.plot(
        time,
        right_volume,
        label="Right Section",
    )

    plt.xlabel(
        "Time [s]"
    )

    plt.ylabel(
        "Fuel Volume [m³]"
    )

    plt.title(
        f"Fuel Transfer - "
        f"{fill_fraction * 100:.0f}% Fill - "
        f"{acceleration_g:+.2f} g"
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.close()


def plot_transient_cg(
    time,
    x_cg,
    fill_fraction,
    acceleration_g,
    output_path,
):
    output_path = prepare_output_path(
        output_path
    )

    plt.figure(
        figsize=(9, 6)
    )

    plt.plot(
        time,
        x_cg,
    )

    plt.xlabel(
        "Time [s]"
    )

    plt.ylabel(
        "Fuel XCG [m]"
    )

    plt.title(
        f"Transient Fuel CG Response - "
        f"{fill_fraction * 100:.0f}% Fill - "
        f"{acceleration_g:+.2f} g"
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.close()
