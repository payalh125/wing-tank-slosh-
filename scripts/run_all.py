
from pathlib import Path
import subprocess
import sys



PROJECT_ROOT = Path(__file__).resolve().parent




WORKFLOW = [
    {
        "name": "VOF Baseline Simulation",
        "script": PROJECT_ROOT / "vof" / "run_vof.py",
    },
    {
        "name": "VOF Validation",
        "script": PROJECT_ROOT / "vof" / "validation.py",
    },
    {
        "name": "SPH Hydrostatic Relaxation",
        "script": PROJECT_ROOT / "sph" / "run_sph_hydrostatic.py",
    },
    {
        "name": "SPH Dynamic Sloshing",
        "script": PROJECT_ROOT / "sph" / "run_sph_dynamic.py",
    },
]


def run_script(name, script_path):
    """
    Execute one simulation script.

    Parameters
    ----------
    name : str
        Name of the simulation stage.

    script_path : pathlib.Path
        Path to the Python script.
    """

    print()
    print("=" * 70)
    print(f" RUNNING: {name.upper()}")
    print("=" * 70)
    print()

    if not script_path.exists():

        print(f"ERROR: Required script not found:")
        print(script_path)

        return False

    try:

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            check=True,
        )

        if result.returncode == 0:

            print()
            print("-" * 70)
            print(f"COMPLETED: {name}")
            print("-" * 70)

            return True

        else:

            print()
            print(f"WARNING: {name} returned an error.")

            return False

    except subprocess.CalledProcessError:

        print()
        print("=" * 70)
        print(f"FAILED: {name}")
        print("=" * 70)

        return False


def main():

    print()
    print("=" * 70)
    print(" WING TANK SLOSHING SIMULATION FRAMEWORK")
    print("=" * 70)

    print()
    print("Simulation methods:")
    print("  1. Simplified VOF-inspired free-surface model")
    print("  2. Simplified SPH particle-based model")

    print()
    print("Execution workflow:")

    for i, stage in enumerate(WORKFLOW, start=1):

        print(f"  {i}. {stage['name']}")

    print()

    completed_stages = []
    failed_stages = []

  

    for stage in WORKFLOW:

        success = run_script(
            stage["name"],
            stage["script"],
        )

        if success:

            completed_stages.append(stage["name"])

        else:

            failed_stages.append(stage["name"])

            print()
            print("Stopping workflow because a simulation stage failed.")

            break


    print()
    print("=" * 70)
    print(" MASTER SIMULATION SUMMARY")
    print("=" * 70)

    print()

    if completed_stages:

        print("Completed stages:")

        for stage in completed_stages:

            print(f"  [PASS] {stage}")

    print()

    if failed_stages:

        print("Failed stages:")

        for stage in failed_stages:

            print(f"  [FAIL] {stage}")

        print()
        print("=" * 70)
        print(" WORKFLOW TERMINATED")
        print("=" * 70)

        sys.exit(1)

    else:

        print("All simulation stages completed successfully.")

        print()
        print("=" * 70)
        print(" WING TANK SLOSHING WORKFLOW COMPLETED")
        print("=" * 70)




if __name__ == "__main__":

    main()
