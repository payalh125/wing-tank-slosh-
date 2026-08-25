import run_static_analysis
import run_acceleration
import run_sections


def main():

    print()
    print("=" * 70)
    print("RUNNING COMPLETE WING TANK ANALYSIS")
    print("=" * 70)

    run_static_analysis.main()

    run_acceleration.main()

    run_sections.main()

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
