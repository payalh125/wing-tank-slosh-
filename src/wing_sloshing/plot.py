import matplotlib.pyplot as plt


def plot_cg_vs_acceleration(
    accelerations,
    unrestricted_cg,
    compartment_cg,
    output_path=None
):
    plt.figure()

    plt.plot(
        accelerations,
        unrestricted_cg,
        marker="o",
        label="Unrestricted redistribution"
    )

    plt.plot(
        accelerations,
        compartment_cg,
        marker="s",
        label="Compartment-limited redistribution"
    )

    plt.xlabel("Longitudinal acceleration [g]")
    plt.ylabel("Fuel CG position [m]")

    plt.grid(True)
    plt.legend()

    if output_path is not None:
        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight"
        )

    plt.show()


def plot_pressure_distribution(
    accelerations,
    pressures,
    output_path=None
):
    plt.figure()

    for sensor_name, sensor_pressure in pressures.items():

        plt.plot(
            accelerations,
            sensor_pressure,
            marker="o",
            label=sensor_name
        )

    plt.xlabel("Longitudinal acceleration [g]")
    plt.ylabel("Gauge pressure [Pa]")

    plt.grid(True)
    plt.legend()

    if output_path is not None:
        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight"
        )

    plt.show()
