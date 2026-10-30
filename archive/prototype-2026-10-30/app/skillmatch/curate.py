"""Check the hand-curated adverts file.

python -m skillmatch.curate validate [path]
"""

import sys

from skillmatch.sources.curated import CSV_PATH, validate


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] != ["validate"]:
        print("usage: python -m skillmatch.curate validate [path]")
        return 2
    path = argv[1] if len(argv) > 1 else CSV_PATH
    problems = validate(path)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {path} is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
