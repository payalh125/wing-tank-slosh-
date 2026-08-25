import numpy as np


def create_grid(length, height, nx, nz):
   

    x = np.linspace(0.0, length, nx)
    z = np.linspace(0.0, height, nz)

    X, Z = np.meshgrid(x, z)

    dx = x[1] - x[0]
    dz = z[1] - z[0]

    return x, z, X, Z, dx, dz


def local_tank_height(x, length, root_height, tip_height):
   

    return root_height + (tip_height - root_height) * x / length


def local_tank_width(x, length, root_width, tip_width):
    

    return root_width + (tip_width - root_width) * x / length


def tank_mask(X, Z, length, root_height, tip_height):
   

    height = local_tank_height(
        X,
        length,
        root_height,
        tip_height,
    )

    return (X >= 0.0) & (X <= length) & (Z >= 0.0) & (Z <= height)


def liquid_fraction(
    X,
    Z,
    surface_height,
    tank_domain,
):
 
    alpha = np.zeros_like(X, dtype=float)

    liquid = (Z <= surface_height) & tank_domain

    alpha[liquid] = 1.0

    return alpha


def find_static_surface_height(
    x,
    target_volume,
    length,
    root_width,
    tip_width,
    root_height,
    tip_height,
):

    def volume_at_height(level):

        local_height = local_tank_height(
            x,
            length,
            root_height,
            tip_height,
        )

        local_width = local_tank_width(
            x,
            length,
            root_width,
            tip_width,
        )

        liquid_height = np.minimum(
            np.maximum(level, 0.0),
            local_height,
        )

        area = local_width * liquid_height

        return np.trapezoid(area, x)

    lower = 0.0
    upper = max(root_height, tip_height)

    for _ in range(100):

        mid = 0.5 * (lower + upper)

        volume = volume_at_height(mid)

        if volume < target_volume:
            lower = mid
        else:
            upper = mid

    return 0.5 * (lower + upper)


def free_surface_profile(
    x,
    base_level,
    acceleration,
    gravity=9.81,
):
    

    x_reference = 0.5 * (x[0] + x[-1])

    return (
        base_level
        - acceleration / gravity
        * (x - x_reference)
    )


def adjust_surface_for_volume(
    x,
    target_volume,
    acceleration,
    length,
    root_width,
    tip_width,
    root_height,
    tip_height,
    gravity=9.81,
):
    

    def calculate_volume(intercept):

        surface = free_surface_profile(
            x,
            intercept,
            acceleration,
            gravity,
        )

        local_height = local_tank_height(
            x,
            length,
            root_height,
            tip_height,
        )

        local_width = local_tank_width(
            x,
            length,
            root_width,
            tip_width,
        )

        liquid_height = np.minimum(
            np.maximum(surface, 0.0),
            local_height,
        )

        area = local_width * liquid_height

        return np.trapezoid(area, x)

    lower = -max(root_height, tip_height)
    upper = 2.0 * max(root_height, tip_height)

    for _ in range(100):

        intercept = 0.5 * (lower + upper)

        volume = calculate_volume(intercept)

        if volume < target_volume:
            lower = intercept
        else:
            upper = intercept

    intercept = 0.5 * (lower + upper)

    surface = free_surface_profile(
        x,
        intercept,
        acceleration,
        gravity,
    )

    return surface


def calculate_volume(
    alpha,
    x,
    z,
    length,
    root_width,
    tip_width,
):
    
    local_width = local_tank_width(
        x,
        length,
        root_width,
        tip_width,
    )

    dx = x[1] - x[0]
    dz = z[1] - z[0]

    width_2d = np.tile(
        local_width,
        (len(z), 1),
    )

    volume = np.sum(
        alpha * width_2d
    ) * dx * dz

    return volume


def calculate_xcg(
    alpha,
    X,
    Z,
    x,
    z,
    length,
    root_width,
    tip_width,
):

    local_width = local_tank_width(
        x,
        length,
        root_width,
        tip_width,
    )

    dx = x[1] - x[0]
    dz = z[1] - z[0]

    width_2d = np.tile(
        local_width,
        (len(z), 1),
    )

    volume_elements = alpha * width_2d * dx * dz

    total_volume = np.sum(volume_elements)

    if total_volume <= 0.0:
        raise ValueError("Liquid volume is zero.")

    xcg = np.sum(
        X * volume_elements
    ) / total_volume

    return xcg


def hydrostatic_pressure(
    surface,
    sensor_x,
    sensor_z,
    density,
    gravity=9.81,
):

    local_surface = np.interp(
        sensor_x,
        np.linspace(
            0.0,
            1.0,
            len(surface),
        ),
        surface,
    )

    liquid_depth = local_surface - sensor_z

    if liquid_depth <= 0.0:
        return 0.0

    return density * gravity * liquid_depth
