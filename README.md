# Wing Tank Fuel Sloshing Analysis

A Python-based computational framework for investigating fuel redistribution, pressure behaviour and centre-of-gravity movement in a simplified aircraft wing tank.

The project compares three modelling approaches:

- **Analytical modelling** for simplified fuel redistribution and hydrostatic pressure estimation.
- **VOF-based modelling** for free-surface fuel redistribution under prescribed excitation.
- **Smoothed Particle Hydrodynamics (SPH)** for particle-based hydrostatic and dynamic sloshing simulations.

## Features

- Simplified tapered wing-tank geometry
- Fuel volume and fill-level modelling
- Hydrostatic pressure calculation
- Longitudinal and lateral centre-of-gravity calculation
- Prescribed acceleration, pitch and roll excitation
- Internal rib and compartment effects
- VOF-based free-surface modelling
- SPH hydrostatic relaxation and dynamic sloshing
- Pressure and particle-field post-processing
- Numerical validation and volume-conservation checks

## Project Structure

```text
.
├── configurations/      # Simulation and geometry configurations
├── scripts/             # Executable analysis and validation scripts
├── src/
│   └── wing_sloshing/
│       ├── geometry.py
│       ├── fuel.py
│       ├── cg.py
│       ├── pressure.py
│       ├── surface.py
│       ├── vof.py
│       ├── sph_particles.py
│       ├── sph_kernels.py
│       ├── sph_solver.py
│       └── sph_postprocess.py
├── tests/               # Verification and unit tests
├── requirements.txt
└── pyproject.toml
