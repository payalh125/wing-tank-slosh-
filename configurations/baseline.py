

TANK_LENGTH = 1.200

ROOT_WIDTH = 1.240
TIP_WIDTH = 0.813

ROOT_HEIGHT = 0.285
TIP_HEIGHT = 0.187



FUEL_DENSITY = 800.0
GRAVITY = 9.81



BAFFLE_LOCATION = 0.600

OPENING_AREA = 0.010
DISCHARGE_COEFFICIENT = 0.600




NUM_X = 1000


FILL_FRACTIONS = [0.30, 0.60, 0.90]

ACCELERATIONS_G = [
    -0.50,
    -0.25,
    0.00,
    0.25,
    0.50
]


# Pressure sensor locations


PRESSURE_SENSORS = {
    "P1": {"x": 0.00, "z": 0.00},
    "P2": {"x": 0.24, "z": 0.00},
    "P3": {"x": 0.48, "z": 0.00},
    "P4": {"x": 0.72, "z": 0.00},
    "P5": {"x": 0.96, "z": 0.00},
    "P6": {"x": 1.20, "z": 0.00},
}



TRANSIENT_FILL_FRACTION = 0.30
TRANSIENT_ACCELERATION_G = -0.50

TRANSIENT_DURATION = 10.0
TRANSIENT_POINTS = 250
