TANK = {
    "length": 1.20,
    "root_width": 1.240,
    "tip_width": 0.813,
    "root_height": 0.285,
    "tip_height": 0.187,
}

FLUID = {
    "density": 800.0,
    "dynamic_viscosity": 1.0e-3,
    "gravity": 9.81,
}

CASE = {
    "fill_fraction": 0.30,
    "amplitude": 0.05,
    "frequency": 1.0,
    "simulation_time": 5.0,
    "time_step": 0.002,
}

GRID = {
    "nx": 160,
    "nz": 80,
}

SENSORS = {
    "left": {
        "x": 0.18,
        "z": 0.013515,
    },
    "right": {
        "x": 1.02,
        "z": 0.010085,
    },
}
