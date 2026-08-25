from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


scripts = [
    "run_static_analysis.py",
    "run_acceleration.py",
    "run_sections.py",
    "run_vof_baseline.py",
    "validate_vof.py",
]


def main():

    for script in scripts:

        print()
        print("=" * 60)
        print(f"RUNNING: {script}")
        print("=" * 60)

        subprocess.run(
            [
                sys.executable,
                str(ROOT / script),
            ],
            check=True,
        )

    print()
    print("=" * 60)
    print("ALL ANALYSES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
