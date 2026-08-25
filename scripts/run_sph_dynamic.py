

from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt



ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "results" / "sph" / "data"
FIG_DIR = ROOT / "results" / "sph" / "figures"

DATA_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


L = 1.200              # Tank length [m]

# Tapered tank dimensions
W_ROOT = 1.240         # Root-side width [m]
W_TIP = 0.813          # Tip-side width [m]

H_ROOT = 0.285         # Root-side height [m]
H_TIP = 0.187          # Tip-side height [m]


def tank_height(x):
    
    x = np.asarray(x)

    return H_ROOT + (H_TIP - H_ROOT) * (x / L)



RHO0 = 800.0           # Reference density [kg/m^3]
FILL_FRACTION = 0.30

# Reference tank volume from baseline model
TANK_VOLUME = 0.294889400

TARGET_VOLUME = FILL_FRACTION * TANK_VOLUME
TARGET_MASS = TARGET_VOLUME * RHO0



DX = 0.005
H = 1.30 * DX

SOUND_SPEED = 60.0
EOS_GAMMA = 7.0

ARTIFICIAL_VISCOSITY = 0.10

GRAVITY = 9.81

# Numerical damping
DAMPING = 0.20


DT = 1.0e-4

RELAXATION_TIME = 0.20
RELAXATION_STEPS = int(RELAXATION_TIME / DT)

SIMULATION_TIME = 3.0
NSTEPS = int(SIMULATION_TIME / DT)


EXCITATION_AMPLITUDE = 0.050       # Tank displacement [m]
EXCITATION_FREQUENCY = 1.0         # Hz

OMEGA = 2.0 * np.pi * EXCITATION_FREQUENCY

EXCITATION_RAMP_TIME = 1.0


def tank_acceleration(t):
   

    acceleration = (
        EXCITATION_AMPLITUDE
        * OMEGA**2
        * np.sin(OMEGA * t)
    )

    ramp = min(t / EXCITATION_RAMP_TIME, 1.0)

    return ramp * acceleration



def cubic_spline_gradient(rx, rz, h):
    """
    2D cubic spline kernel gradient.

    Parameters
    ----------
    rx, rz : ndarray
        Relative particle coordinates.
    h : float
        Smoothing length.

    Returns
    -------
    grad_x, grad_z : ndarray
        Kernel gradient components.
    """

    r = np.sqrt(rx**2 + rz**2)

    grad_x = np.zeros_like(r)
    grad_z = np.zeros_like(r)

    valid = r > 1.0e-12

    q = r[valid] / h

    sigma = 10.0 / (7.0 * np.pi * h**2)

    dW_dq = np.zeros_like(q)

    region_1 = q < 1.0
    region_2 = (q >= 1.0) & (q < 2.0)

    dW_dq[region_1] = (
        sigma
        * (-3.0 * q[region_1]
           + 2.25 * q[region_1]**2)
        / h
    )

    dW_dq[region_2] = (
        -0.75
        * sigma
        * (2.0 - q[region_2])**2
        / h
    )

    unit_x = rx[valid] / r[valid]
    unit_z = rz[valid] / r[valid]

    grad_x[valid] = dW_dq * unit_x
    grad_z[valid] = dW_dq * unit_z

    return grad_x, grad_z



def create_particles():
    """
    Create the initial uniform particle distribution.

    The liquid height is chosen from the baseline fill condition.
    """

    # Baseline free-surface height
    liquid_level = 0.071819143

    x_values = np.arange(
        DX / 2.0,
        L,
        DX
    )

    x_list = []
    z_list = []

    for x_i in x_values:

        z_max = min(
            liquid_level,
            tank_height(x_i)
        )

        z_values = np.arange(
            DX / 2.0,
            z_max,
            DX
        )

        for z_i in z_values:
            x_list.append(x_i)
            z_list.append(z_i)

    x = np.array(x_list, dtype=float)
    z = np.array(z_list, dtype=float)

    return x, z




def initialise_hydrostatic_state(x, z, mass_per_particle):

    liquid_level = 0.071819143

    depth = np.maximum(
        liquid_level - z,
        0.0
    )

    # Hydrostatic pressure
    pressure = RHO0 * GRAVITY * depth

    # Tait equation inversion
    B = RHO0 * SOUND_SPEED**2 / EOS_GAMMA

    rho = RHO0 * (
        1.0 + pressure / B
    ) ** (1.0 / EOS_GAMMA)

    vx = np.zeros_like(x)
    vz = np.zeros_like(z)

    return rho, pressure, vx, vz



def equation_of_state(rho):
    """
    Weakly compressible SPH Tait equation of state.
    """

    B = RHO0 * SOUND_SPEED**2 / EOS_GAMMA

    pressure = B * (
        (rho / RHO0) ** EOS_GAMMA - 1.0
    )

    return pressure

def update_density(
    x,
    z,
    vx,
    vz,
    rho,
    mass
):
  

    n = len(x)

    drho_dt = np.zeros(n)

    support_radius = 2.0 * H

    for i in range(n):

        rx = x[i] - x
        rz = z[i] - z

        r = np.sqrt(rx**2 + rz**2)

        neighbours = (
            (r > 1.0e-12)
            & (r < support_radius)
        )

        if not np.any(neighbours):
            continue

        rx_n = rx[neighbours]
        rz_n = rz[neighbours]

        dvx = vx[i] - vx[neighbours]
        dvz = vz[i] - vz[neighbours]

        grad_x, grad_z = cubic_spline_gradient(
            rx_n,
            rz_n,
            H
        )

        velocity_gradient = (
            dvx * grad_x
            + dvz * grad_z
        )

        drho_dt[i] = (
            mass
            * np.sum(velocity_gradient)
        )

    rho_new = rho + DT * drho_dt

    # Numerical density limits
    rho_new = np.clip(
        rho_new,
        0.95 * RHO0,
        1.05 * RHO0
    )

    return rho_new


def pressure_acceleration(
    x,
    z,
    rho,
    pressure,
    mass
):
    """
    Symmetric SPH pressure-gradient acceleration.
    """

    n = len(x)

    ax = np.zeros(n)
    az = np.zeros(n)

    support_radius = 2.0 * H

    for i in range(n):

        rx = x[i] - x
        rz = z[i] - z

        r = np.sqrt(rx**2 + rz**2)

        neighbours = (
            (r > 1.0e-12)
            & (r < support_radius)
        )

        if not np.any(neighbours):
            continue

        j = np.where(neighbours)[0]

        grad_x, grad_z = cubic_spline_gradient(
            rx[j],
            rz[j],
            H
        )

        pressure_term = (
            pressure[i] / rho[i]**2
            + pressure[j] / rho[j]**2
        )

        ax[i] -= (
            mass
            * np.sum(
                pressure_term * grad_x
            )
        )

        az[i] -= (
            mass
            * np.sum(
                pressure_term * grad_z
            )
        )

    return ax, az


def apply_damping(vx, vz):

    ax_damping = -DAMPING * vx
    az_damping = -DAMPING * vz

    return ax_damping, az_damping



def enforce_boundaries(x, z, vx, vz):
    

    epsilon = 0.25 * DX


    left = x < epsilon

    x[left] = epsilon

    vx[left & (vx < 0.0)] *= -0.30


    right = x > L - epsilon

    x[right] = L - epsilon

    vx[right & (vx > 0.0)] *= -0.30

   
    bottom = z < epsilon

    z[bottom] = epsilon

    vz[bottom & (vz < 0.0)] *= -0.20

    z_top = tank_height(x) - epsilon

    above_top = z > z_top

    z[above_top] = z_top[above_top]

    vz[above_top & (vz > 0.0)] *= -0.20

    return x, z, vx, vz




def count_particles_outside(x, z):

    z_top = tank_height(x)

    outside = (
        (x < 0.0)
        | (x > L)
        | (z < 0.0)
        | (z > z_top)
    )

    return int(np.sum(outside))


def hydrostatic_relaxation(
    x,
    z,
    rho,
    pressure,
    vx,
    vz,
    mass
):
    """
    Relax the initial particle state before applying excitation.
    """

    print()
    print("HYDROSTATIC RELAXATION")
    print("-" * 60)

    print(
        f"Relaxation time         = "
        f"{RELAXATION_TIME:.4f} s"
    )

    print(
        f"Relaxation steps        = "
        f"{RELAXATION_STEPS}"
    )

    for step in range(RELAXATION_STEPS):

        # Density update
        rho = update_density(
            x,
            z,
            vx,
            vz,
            rho,
            mass
        )

        pressure = equation_of_state(rho)

        # Pressure acceleration
        ax_p, az_p = pressure_acceleration(
            x,
            z,
            rho,
            pressure,
            mass
        )

        # Gravity
        az_total = az_p - GRAVITY

        # Damping
        ax_damp, az_damp = apply_damping(
            vx,
            vz
        )

        ax_total = ax_p + ax_damp
        az_total += az_damp

        # Velocity update
        vx += DT * ax_total
        vz += DT * az_total

        # Position update
        x += DT * vx
        z += DT * vz

        # Boundary enforcement
        x, z, vx, vz = enforce_boundaries(
            x,
            z,
            vx,
            vz
        )

    print("Relaxation completed.")

    return x, z, rho, pressure, vx, vz


def main():

    print()
    print("=" * 60)
    print(" STEP 6/7 - SPH DYNAMIC SLOSHING AND RESPONSE")
    print(" COMMON TAPERED WING-TANK BASELINE CASE")
    print("=" * 60)


    print()
    print("TANK GEOMETRY")
    print("-" * 60)

    print(f"Tank length             = {L:.6f} m")
    print(f"Root-side width         = {W_ROOT:.6f} m")
    print(f"Tip-side width          = {W_TIP:.6f} m")
    print(f"Root-side height        = {H_ROOT:.6f} m")
    print(f"Tip-side height         = {H_TIP:.6f} m")


    print()
    print("REFERENCE FUEL CONDITION")
    print("-" * 60)

    print(f"Tank volume             = {TANK_VOLUME:.9f} m^3")
    print(f"Fill fraction           = {FILL_FRACTION * 100:.1f} %")
    print(f"Target fuel volume      = {TARGET_VOLUME:.9f} m^3")
    print(f"Target fuel mass        = {TARGET_MASS:.6f} kg")


    x, z = create_particles()

    n_particles = len(x)

    raw_volume = n_particles * DX**2

    volume_scale = TARGET_VOLUME / raw_volume

    particle_volume = (
        TARGET_VOLUME / n_particles
    )

    mass = TARGET_MASS / n_particles

    print()
    print("INITIAL PARTICLE FIELD")
    print("-" * 60)

    print(
        f"Number of particles     = "
        f"{n_particles}"
    )

    print(
        f"Raw particle volume     = "
        f"{raw_volume:.9f} m^3"
    )

    print(
        f"Volume scaling factor   = "
        f"{volume_scale:.9f}"
    )

    print(
        f"Particle mass           = "
        f"{mass:.12f} kg"
    )

    
    rho, pressure, vx, vz = (
        initialise_hydrostatic_state(
            x,
            z,
            mass
        )
    )

    initial_xcg = np.average(
        x,
        weights=np.full(n_particles, mass)
    )

    initial_zcg = np.average(
        z,
        weights=np.full(n_particles, mass)
    )

    print()
    print("HYDROSTATIC INITIALISATION")
    print("-" * 60)

    print(
        f"Initial XCG             = "
        f"{initial_xcg:.9f} m"
    )

    print(
        f"Initial ZCG             = "
        f"{initial_zcg:.9f} m"
    )

    print(
        f"Minimum density         = "
        f"{rho.min():.6f} kg/m^3"
    )

    print(
        f"Maximum density         = "
        f"{rho.max():.6f} kg/m^3"
    )


    x, z, rho, pressure, vx, vz = (
        hydrostatic_relaxation(
            x,
            z,
            rho,
            pressure,
            vx,
            vz,
            mass
        )
    )


    np.savez(
        DATA_DIR / "sph_step5_relaxed_state.npz",
        x=x,
        z=z,
        vx=vx,
        vz=vz,
        rho=rho,
        pressure=pressure,
        particle_mass=mass
    )


    max_acceleration = (
        EXCITATION_AMPLITUDE
        * OMEGA**2
    )

    print()
    print("EXCITATION CONDITION")
    print("-" * 60)

    print(
        f"Amplitude               = "
        f"{EXCITATION_AMPLITUDE:.6f} m"
    )

    print(
        f"Frequency               = "
        f"{EXCITATION_FREQUENCY:.6f} Hz"
    )

    print(
        f"Angular frequency       = "
        f"{OMEGA:.6f} rad/s"
    )

    print(
        f"Maximum acceleration    = "
        f"{max_acceleration:.6f} m/s^2"
    )

    print(
        f"Maximum acceleration    = "
        f"{max_acceleration / GRAVITY:.6f} g"
    )

    print(
        f"Excitation ramp time    = "
        f"{EXCITATION_RAMP_TIME:.6f} s"
    )

    print()
    print("TIME INTEGRATION")
    print("-" * 60)

    print(f"Time step               = {DT:.6e} s")
    print(f"Simulation time         = {SIMULATION_TIME:.6f} s")
    print(f"Number of steps         = {NSTEPS}")

    
    time_history = []
    xcg_history = []
    zcg_history = []

    rho_min_history = []
    rho_max_history = []

    pressure_max_history = []

    velocity_max_history = []

    acceleration_history = []

    outside_history = []

    # Store every N steps
    OUTPUT_INTERVAL = 100

    print()
    print("RUNNING DYNAMIC SLOSHING SIMULATION")
    print("-" * 60)


    for step in range(NSTEPS + 1):

        t = step * DT

        

        a_tank = tank_acceleration(t)

        rho = update_density(
            x,
            z,
            vx,
            vz,
            rho,
            mass
        )


        pressure = equation_of_state(rho)


        ax_p, az_p = pressure_acceleration(
            x,
            z,
            rho,
            pressure,
            mass
        )

       

        ax_damp, az_damp = apply_damping(
            vx,
            vz
        )

        # Tank-frame longitudinal forcing
        ax_total = (
            ax_p
            + ax_damp
            - a_tank
        )

        # Gravity
        az_total = (
            az_p
            + az_damp
            - GRAVITY
        )


        vx += DT * ax_total
        vz += DT * az_total

        

        x += DT * vx
        z += DT * vz

    
        x, z, vx, vz = enforce_boundaries(
            x,
            z,
            vx,
            vz
        )

   
        if step % OUTPUT_INTERVAL == 0:

            xcg = np.average(
                x,
                weights=np.full(n_particles, mass)
            )

            zcg = np.average(
                z,
                weights=np.full(n_particles, mass)
            )

            vmax = np.max(
                np.sqrt(vx**2 + vz**2)
            )

            outside = count_particles_outside(
                x,
                z
            )

            time_history.append(t)

            xcg_history.append(xcg)
            zcg_history.append(zcg)

            rho_min_history.append(
                np.min(rho)
            )

            rho_max_history.append(
                np.max(rho)
            )

            pressure_max_history.append(
                np.max(pressure)
            )

            velocity_max_history.append(
                vmax
            )

            acceleration_history.append(
                a_tank
            )

            outside_history.append(
                outside
            )


        if (
            step > 0
            and step % 2000 == 0
        ):

            xcg_now = np.average(
                x,
                weights=np.full(
                    n_particles,
                    mass
                )
            )

            vmax_now = np.max(
                np.sqrt(vx**2 + vz**2)
            )

            outside_now = count_particles_outside(
                x,
                z
            )

            print(
                f"Step {step:5d} / {NSTEPS} | "
                f"Time = {t:.3f} s | "
                f"XCG = {xcg_now:.5f} m | "
                f"Vmax = {vmax_now:.4f} m/s | "
                f"rho = {rho.min():.2f} to "
                f"{rho.max():.2f} | "
                f"Outside = {outside_now}"
            )

    print()
    print("Simulation completed.")


    time_history = np.asarray(time_history)

    xcg_history = np.asarray(xcg_history)
    zcg_history = np.asarray(zcg_history)

    rho_min_history = np.asarray(
        rho_min_history
    )

    rho_max_history = np.asarray(
        rho_max_history
    )

    pressure_max_history = np.asarray(
        pressure_max_history
    )

    velocity_max_history = np.asarray(
        velocity_max_history
    )

    acceleration_history = np.asarray(
        acceleration_history
    )

    outside_history = np.asarray(
        outside_history
    )

    final_mass = n_particles * mass

    final_volume = (
        final_mass / RHO0
    )

    min_xcg = np.min(xcg_history)
    max_xcg = np.max(xcg_history)

    xcg_excursion = (
        max_xcg - min_xcg
    )

    rho_min = np.min(rho_min_history)
    rho_max = np.max(rho_max_history)

    density_deviation = max(
        abs(rho_min - RHO0),
        abs(rho_max - RHO0)
    )

    density_deviation_percent = (
        100.0
        * density_deviation
        / RHO0
    )

    max_pressure = np.max(
        pressure_max_history
    )

    max_velocity = np.max(
        velocity_max_history
    )

    max_outside = np.max(
        outside_history
    )

    print()
    print("=" * 60)
    print(" SPH DYNAMIC RESPONSE RESULTS")
    print("=" * 60)

    print()
    print("MASS AND VOLUME")
    print("-" * 60)

    print(
        f"Final particle mass     = "
        f"{final_mass:.9f} kg"
    )

    print(
        f"Target fuel mass        = "
        f"{TARGET_MASS:.9f} kg"
    )

    print(
        f"Mass error              = "
        f"{abs(final_mass - TARGET_MASS):.9e} kg"
    )

    print(
        f"Final represented volume= "
        f"{final_volume:.9f} m^3"
    )

    print()
    print("CG RESPONSE")
    print("-" * 60)

    print(
        f"Initial XCG             = "
        f"{initial_xcg:.9f} m"
    )

    print(
        f"Minimum XCG             = "
        f"{min_xcg:.9f} m"
    )

    print(
        f"Maximum XCG             = "
        f"{max_xcg:.9f} m"
    )

    print(
        f"Total XCG excursion     = "
        f"{xcg_excursion:.9f} m"
    )

    print()
    print("PARTICLE VELOCITY")
    print("-" * 60)

    print(
        f"Maximum particle speed  = "
        f"{max_velocity:.9f} m/s"
    )

    print()
    print("DENSITY RESPONSE")
    print("-" * 60)

    print(
        f"Minimum density         = "
        f"{rho_min:.9f} kg/m^3"
    )

    print(
        f"Maximum density         = "
        f"{rho_max:.9f} kg/m^3"
    )

    print(
        f"Maximum density deviation = "
        f"{density_deviation_percent:.6f} %"
    )

    print()
    print("PRESSURE RESPONSE")
    print("-" * 60)

    print(
        f"Maximum pressure        = "
        f"{max_pressure:.9f} Pa"
    )

    print()
    print("PARTICLE CONTAINMENT")
    print("-" * 60)

    print(
        f"Maximum particles outside = "
        f"{max_outside}"
    )

  

    np.savez(
        DATA_DIR / "sph_dynamic_results.npz",

        time=time_history,

        xcg=xcg_history,
        zcg=zcg_history,

        acceleration=acceleration_history,

        rho_min=rho_min_history,
        rho_max=rho_max_history,

        pressure_max=pressure_max_history,

        velocity_max=velocity_max_history,

        particles_outside=outside_history,

        final_x=x,
        final_z=z,

        final_vx=vx,
        final_vz=vz,

        final_rho=rho,
        final_pressure=pressure,

        particle_mass=mass,

        initial_xcg=initial_xcg,
        initial_zcg=initial_zcg
    )

    csv_file = (
        DATA_DIR
        / "sph_response_history.csv"
    )

    with open(
        csv_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "time_s",
            "tank_acceleration_m_s2",
            "xcg_m",
            "zcg_m",
            "rho_min_kg_m3",
            "rho_max_kg_m3",
            "pressure_max_pa",
            "velocity_max_m_s",
            "particles_outside"
        ])

        for i in range(
            len(time_history)
        ):

            writer.writerow([
                time_history[i],
                acceleration_history[i],
                xcg_history[i],
                zcg_history[i],
                rho_min_history[i],
                rho_max_history[i],
                pressure_max_history[i],
                velocity_max_history[i],
                outside_history[i]
            ])

   
    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        time_history,
        xcg_history,
        label="XCG"
    )

    plt.axhline(
        initial_xcg,
        linestyle="--",
        label="Initial XCG"
    )

    plt.xlabel("Time [s]")
    plt.ylabel("Longitudinal centre of gravity, XCG [m]")

    plt.title(
        "SPH Longitudinal Centre-of-Gravity Response"
    )

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        FIG_DIR / "sph_xcg_response.png",
        dpi=300
    )

    plt.close()

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        time_history,
        rho_min_history,
        label="Minimum density"
    )

    plt.plot(
        time_history,
        rho_max_history,
        label="Maximum density"
    )

    plt.axhline(
        RHO0,
        linestyle="--",
        label="Reference density"
    )

    plt.xlabel("Time [s]")
    plt.ylabel("Density [kg/m³]")

    plt.title(
        "SPH Density Range During Sloshing"
    )

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        FIG_DIR / "sph_density_response.png",
        dpi=300
    )

    plt.close()

 
    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        time_history,
        velocity_max_history
    )

    plt.xlabel("Time [s]")
    plt.ylabel(
        "Maximum particle speed [m/s]"
    )

    plt.title(
        "SPH Maximum Particle Velocity"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        FIG_DIR / "sph_velocity_response.png",
        dpi=300
    )

    plt.close()


    plt.figure(
        figsize=(12, 5)
    )

    plt.scatter(
        x,
        z,
        s=2
    )

    x_wall = np.linspace(
        0.0,
        L,
        300
    )

    z_wall = tank_height(
        x_wall
    )

    plt.plot(
        x_wall,
        z_wall,
        linewidth=1.5
    )

    plt.plot(
        [0.0, L],
        [0.0, 0.0],
        linewidth=1.5
    )

    plt.plot(
        [0.0, 0.0],
        [0.0, H_ROOT],
        linewidth=1.5
    )

    plt.plot(
        [L, L],
        [0.0, H_TIP],
        linewidth=1.5
    )

    plt.xlabel(
        "Tank longitudinal coordinate, x [m]"
    )

    plt.ylabel(
        "Tank vertical coordinate, z [m]"
    )

    plt.title(
        "Final SPH Particle Distribution"
    )

    plt.xlim(
        -0.02,
        L + 0.02
    )

    plt.ylim(
        -0.02,
        H_ROOT + 0.02
    )

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        FIG_DIR
        / "sph_final_particle_distribution.png",
        dpi=300
    )

    plt.close()

  

    print()
    print("=" * 60)
    print(" SPH MODEL STATUS")
    print("=" * 60)

    if max_outside == 0:
        print(
            "PASS - Particle containment verified."
        )
    else:
        print(
            "WARNING - Particle containment issue detected."
        )

    if density_deviation_percent < 5.0:
        print(
            "PASS - Density variation remains within 5 %."
        )
    else:
        print(
            "WARNING - Density variation exceeds 5 %."
        )

    print()
    print("RESULTS SAVED TO:")
    print(f"  {DATA_DIR}")
    print(f"  {FIG_DIR}")

    print()
    print("=" * 60)
    print(" SPH DYNAMIC SLOSHING SIMULATION COMPLETED")
    print("=" * 60)




if __name__ == "__main__":
    main()
