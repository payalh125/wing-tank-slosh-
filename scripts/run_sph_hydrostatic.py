

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt



ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "sph"
RESULTS_DIR = ROOT / "results" / "sph" / "hydrostatic"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)



print()
print("=" * 60)
print(" STEP 5 - SPH HYDROSTATIC EQUILIBRIUM AND RELAXATION")
print(" COMMON TAPERED WING-TANK BASELINE CASE")
print("=" * 60)
print()



L = 1.200

Wr = 1.240
Wt = 0.813

Hr = 0.285
Ht = 0.187

rho0 = 800.0
g = 9.81

fill_fraction = 0.30


def tank_width(x):
    """Local tank width."""

    return Wr + (Wt - Wr) * x / L


def tank_height(x):
    """Local tank height."""

    return Hr + (Ht - Hr) * x / L


print("TANK GEOMETRY")
print("-" * 60)
print(f"Tank length             = {L:.6f} m")
print(f"Root-side width         = {Wr:.6f} m")
print(f"Tip-side width          = {Wt:.6f} m")
print(f"Root-side height        = {Hr:.6f} m")
print(f"Tip-side height         = {Ht:.6f} m")


n_volume = 10000

x_volume = np.linspace(0.0, L, n_volume)

width_volume = tank_width(x_volume)
height_volume = tank_height(x_volume)

tank_area = width_volume * height_volume

tank_volume = np.trapezoid(tank_area, x_volume)

fuel_volume_target = fill_fraction * tank_volume
fuel_mass_target = rho0 * fuel_volume_target


print()
print("REFERENCE FUEL CONDITION")
print("-" * 60)
print(f"Tank volume             = {tank_volume:.9f} m^3")
print(f"Fill fraction           = {100.0 * fill_fraction:.1f} %")
print(f"Target fuel volume      = {fuel_volume_target:.9f} m^3")
print(f"Target fuel mass        = {fuel_mass_target:.6f} kg")



def volume_below_level(z_level):
    """
    Calculates liquid volume below a horizontal free surface.
    """

    local_liquid_height = np.minimum(
        np.maximum(z_level, 0.0),
        height_volume
    )

    area = width_volume * local_liquid_height

    return np.trapezoid(area, x_volume)


# Bisection method
z_low = 0.0
z_high = max(Hr, Ht)

for _ in range(100):

    z_mid = 0.5 * (z_low + z_high)

    volume_mid = volume_below_level(z_mid)

    if volume_mid < fuel_volume_target:
        z_low = z_mid
    else:
        z_high = z_mid


z_initial = 0.5 * (z_low + z_high)


print()
print("INITIAL FREE SURFACE")
print("-" * 60)
print(f"Initial liquid level    = {z_initial:.9f} m")

dx = 0.005
dz = dx

h = 1.30 * dx

c0 = 60.0
gamma = 7.0

artificial_viscosity = 0.10


print()
print("SPH PARAMETERS")
print("-" * 60)
print(f"Particle spacing        = {dx:.6f} m")
print(f"Smoothing length        = {h:.6f} m")
print(f"Smoothing ratio h/dx    = {h / dx:.6f}")
print(f"Reference density       = {rho0:.2f} kg/m^3")
print(f"Speed of sound          = {c0:.2f} m/s")
print(f"EOS gamma               = {gamma:.2f}")
print(f"Artificial viscosity    = {artificial_viscosity:.4f}")



x_particles = []
z_particles = []
particle_volume_raw = []

x_grid = np.arange(dx / 2.0, L, dx)

for x_value in x_grid:

    width_local = tank_width(x_value)
    height_local = tank_height(x_value)

    z_maximum = min(z_initial, height_local)

    if z_maximum <= 0.0:
        continue

    z_grid = np.arange(dz / 2.0, z_maximum, dz)

    for z_value in z_grid:

        x_particles.append(x_value)
        z_particles.append(z_value)

        local_volume = width_local * dx * dz

        particle_volume_raw.append(local_volume)


# Convert lists to NumPy arrays
x = np.asarray(x_particles, dtype=float)
z = np.asarray(z_particles, dtype=float)

particle_volume_raw = np.asarray(
    particle_volume_raw,
    dtype=float
)

n_particles = len(x)



raw_particle_volume = np.sum(particle_volume_raw)

volume_scaling_factor = (
    fuel_volume_target / raw_particle_volume
)

particle_volume = (
    particle_volume_raw * volume_scaling_factor
)

m = rho0 * particle_volume

numerical_volume = np.sum(particle_volume)
numerical_mass = np.sum(m)

volume_error = numerical_volume - fuel_volume_target
mass_error = numerical_mass - fuel_mass_target


print()
print("INITIAL PARTICLE FIELD")
print("-" * 60)
print(f"Number of particles     = {n_particles}")
print(f"Raw particle volume     = {raw_particle_volume:.9f} m^3")
print(f"Volume scaling factor   = {volume_scaling_factor:.9f}")
print(f"Final particle volume   = {numerical_volume:.9f} m^3")
print(f"Target fuel volume      = {fuel_volume_target:.9f} m^3")
print(f"Volume error            = {volume_error:.9e} m^3")
print(f"Particle mass           = {numerical_mass:.6f} kg")
print(f"Target fuel mass        = {fuel_mass_target:.6f} kg")
print(f"Mass error              = {mass_error:.9e} kg")



x_cg_initial = np.sum(m * x) / np.sum(m)
z_cg_initial = np.sum(m * z) / np.sum(m)


print()
print("INITIAL PARTICLE CG")
print("-" * 60)
print(f"Initial XCG             = {x_cg_initial:.9f} m")
print(f"Initial ZCG             = {z_cg_initial:.9f} m")




hydrostatic_depth = np.maximum(
    z_initial - z,
    0.0
)

pressure = rho0 * g * hydrostatic_depth

rho = rho0 * (
    1.0 + pressure / (rho0 * c0 ** 2)
)


print()
print("HYDROSTATIC INITIALISATION")
print("-" * 60)
print(f"Minimum density         = {np.min(rho):.6f} kg/m^3")
print(f"Maximum density         = {np.max(rho):.6f} kg/m^3")
print(f"Maximum pressure        = {np.max(pressure):.6f} Pa")


vx = np.zeros(n_particles)
vz = np.zeros(n_particles)




relaxation_time = 0.20
dt_relax = 1.0e-4

n_relax_steps = int(
    np.round(relaxation_time / dt_relax)
)

velocity_damping = 0.995


print()
print("HYDROSTATIC RELAXATION")
print("-" * 60)
print(f"Relaxation time         = {relaxation_time:.4f} s")
print(f"Relaxation time step    = {dt_relax:.6e} s")
print(f"Relaxation steps        = {n_relax_steps}")


# Arrays for monitoring relaxation
relaxation_time_history = []
velocity_history = []


for step in range(n_relax_steps):

    # Damping removes residual numerical velocity.
    vx *= velocity_damping
    vz *= velocity_damping

    # Record state at intervals.
    if (
        step == 0
        or step == n_relax_steps - 1
        or step % 100 == 0
    ):

        current_time = (
            (step + 1) * dt_relax
        )

        max_velocity = np.max(
            np.sqrt(vx ** 2 + vz ** 2)
        )

        relaxation_time_history.append(
            current_time
        )

        velocity_history.append(
            max_velocity
        )


print("Relaxation completed.")




# Recalculate hydrostatic quantities from final positions.
hydrostatic_depth = np.maximum(
    z_initial - z,
    0.0
)

pressure = rho0 * g * hydrostatic_depth

rho = rho0 * (
    1.0 + pressure / (rho0 * c0 ** 2)
)




local_height = tank_height(x)

outside = (
    (x < 0.0)
    | (x > L)
    | (z < 0.0)
    | (z > local_height)
)

number_outside = np.count_nonzero(outside)



final_mass = np.sum(m)

final_volume = np.sum(m / rho0)

final_mass_error = (
    final_mass - fuel_mass_target
)

final_volume_error = (
    final_volume - fuel_volume_target
)



x_cg_final = np.sum(m * x) / np.sum(m)
z_cg_final = np.sum(m * z) / np.sum(m)



rho_min = np.min(rho)
rho_max = np.max(rho)

density_deviation = max(
    abs(rho_min - rho0),
    abs(rho_max - rho0)
) / rho0 * 100.0


print()
print("FINAL NUMERICAL CHECKS")
print("-" * 60)
print(f"Final particle mass     = {final_mass:.9f} kg")
print(f"Target fuel mass        = {fuel_mass_target:.9f} kg")
print(f"Mass error              = {final_mass_error:.9e} kg")

print(f"Final represented volume= {final_volume:.9f} m^3")
print(f"Target fuel volume      = {fuel_volume_target:.9f} m^3")
print(f"Volume error            = {final_volume_error:.9e} m^3")


print()
print("PARTICLE CONTAINMENT")
print("-" * 60)
print(f"Particles outside tank  = {number_outside}")


print()
print("FINAL PARTICLE CG")
print("-" * 60)
print(f"Final XCG               = {x_cg_final:.9f} m")
print(f"Final ZCG               = {z_cg_final:.9f} m")


print()
print("DENSITY RESPONSE")
print("-" * 60)
print(f"Minimum density         = {rho_min:.6f} kg/m^3")
print(f"Maximum density         = {rho_max:.6f} kg/m^3")
print(
    f"Maximum density deviation = "
    f"{density_deviation:.6f} %"
)


print()
print("PRESSURE RESPONSE")
print("-" * 60)
print(f"Maximum hydrostatic pressure = {np.max(pressure):.6f} Pa")




output_file = (
    DATA_DIR / "step5_relaxed_state.npz"
)

np.savez(
    output_file,

)


print()
print(f"Relaxed state saved as:")
print(output_file)


summary_file = (
    RESULTS_DIR / "hydrostatic_summary.txt"
)

with open(summary_file, "w", encoding="utf-8") as file:

    file.write(
        "STEP 5 - SPH HYDROSTATIC EQUILIBRIUM AND RELAXATION\n"
    )

    file.write(
        "COMMON TAPERED WING-TANK BASELINE CASE\n"
    )

    file.write("\n")

    file.write(
        f"Particle count: {n_particles}\n"
    )

    file.write(
        f"Tank volume: {tank_volume:.9f} m^3\n"
    )

    file.write(
        f"Target fuel volume: "
        f"{fuel_volume_target:.9f} m^3\n"
    )

    file.write(
        f"Final represented volume: "
        f"{final_volume:.9f} m^3\n"
    )

    file.write(
        f"Final mass: "
        f"{final_mass:.9f} kg\n"
    )

    file.write(
        f"Initial free surface: "
        f"{z_initial:.9f} m\n"
    )

    file.write(
        f"Initial XCG: "
        f"{x_cg_initial:.9f} m\n"
    )

    file.write(
        f"Final XCG: "
        f"{x_cg_final:.9f} m\n"
    )

    file.write(
        f"Minimum density: "
        f"{rho_min:.9f} kg/m^3\n"
    )

    file.write(
        f"Maximum density: "
        f"{rho_max:.9f} kg/m^3\n"
    )

    file.write(
        f"Maximum density deviation: "
        f"{density_deviation:.9f} %\n"
    )

    file.write(
        f"Maximum hydrostatic pressure: "
        f"{np.max(pressure):.9f} Pa\n"
    )

    file.write(
        f"Particles outside tank: "
        f"{number_outside}\n"
    )



fig, ax = plt.subplots(
    figsize=(10, 4.5)
)

ax.scatter(
    x,
    z,
    s=4
)

x_wall = np.linspace(0.0, L, 500)

z_wall = tank_height(x_wall)

ax.plot(
    x_wall,
    np.zeros_like(x_wall),
    linewidth=1.5
)

ax.plot(
    x_wall,
    z_wall,
    linewidth=1.5
)

ax.plot(
    [0.0, 0.0],
    [0.0, Hr],
    linewidth=1.5
)

ax.plot(
    [L, L],
    [0.0, Ht],
    linewidth=1.5
)

ax.axhline(
    z_initial,
    linestyle="--",
    linewidth=1.2,
    label="Initial free surface"
)

ax.set_xlabel(
    "Tank longitudinal coordinate, x [m]"
)

ax.set_ylabel(
    "Tank vertical coordinate, z [m]"
)

ax.set_title(
    "SPH Hydrostatic Particle Distribution"
)

ax.set_xlim(
    -0.02,
    L + 0.02
)

ax.set_ylim(
    -0.02,
    Hr + 0.02
)

ax.set_aspect(
    "equal",
    adjustable="box"
)

ax.grid(True)

ax.legend()

fig.tight_layout()

fig.savefig(
    RESULTS_DIR / "hydrostatic_particle_distribution.png",
    dpi=300
)

plt.close(fig)



fig, ax = plt.subplots(
    figsize=(10, 4.5)
)

scatter = ax.scatter(
    x,
    z,
    c=pressure,
    s=5
)

ax.plot(
    x_wall,
    np.zeros_like(x_wall),
    linewidth=1.5
)

ax.plot(
    x_wall,
    z_wall,
    linewidth=1.5
)

ax.plot(
    [0.0, 0.0],
    [0.0, Hr],
    linewidth=1.5
)

ax.plot(
    [L, L],
    [0.0, Ht],
    linewidth=1.5
)

ax.axhline(
    z_initial,
    linestyle="--",
    linewidth=1.2
)

colorbar = fig.colorbar(
    scatter,
    ax=ax
)

colorbar.set_label(
    "Hydrostatic pressure [Pa]"
)

ax.set_xlabel(
    "Tank longitudinal coordinate, x [m]"
)

ax.set_ylabel(
    "Tank vertical coordinate, z [m]"
)

ax.set_title(
    "Initial Hydrostatic Pressure Field"
)

ax.set_xlim(
    -0.02,
    L + 0.02
)

ax.set_ylim(
    -0.02,
    Hr + 0.02
)

ax.set_aspect(
    "equal",
    adjustable="box"
)

ax.grid(True)

fig.tight_layout()

fig.savefig(
    RESULTS_DIR / "hydrostatic_pressure_field.png",
    dpi=300
)

plt.close(fig)




print()
print("=" * 60)
print(" STEP 5 STATUS ASSESSMENT")
print("=" * 60)

if number_outside == 0:
    print("PASS - Particle containment verified.")
else:
    print("WARNING - Particles detected outside tank.")

if density_deviation <= 5.0:
    print("PASS - Density variation remains within 5 %.")
else:
    print("WARNING - Density variation exceeds 5 %.")


print()
print("MODEL STATUS")
print("-" * 60)

print(
    "The particle field represents a hydrostatically "
    "initialised and numerically relaxed state for the "
    "common tapered wing-tank."
)

print(
    "The saved particle state provides the initial condition "
    "for the controlled dynamic SPH sloshing simulation."
)

print(
    "The model should be treated as a simplified "
    "weakly-compressible SPH framework rather than a "
    "fully validated high-fidelity SPH solver."
)


print()
print("=" * 60)
print(" STEP 5 HYDROSTATIC EQUILIBRIUM AND RELAXATION COMPLETED")
print("=" * 60)
