import argparse
import logging

from skillmatch.etl.pipeline import run


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m skillmatch.etl")
    ap.add_argument("--mode", choices=["fixtures", "live"], default="fixtures")
    ap.add_argument("--offline", action="store_true", help="never call the network")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s"
    )
    result = run(args.mode, offline=True if args.offline else None)
    print(f"{result.mode} build: {result.db_path}")
    for stage, count in result.stage_counts.items():
        print(f"  {stage:45s} {count:6d}")
    print("  excluded by reason:")
    for reason, count in result.excluded.most_common():
        print(f"    {reason:43s} {count:6d}")
    for r in result.source_runs:
        print(
            f"  source {r['source_id']:18s} {r['status']:9s} fetched={r['fetched']} requests={r['requests']}"
        )
    print(f"quality report: {result.report_path}")


if __name__ == "__main__":
    main()
