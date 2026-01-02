from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .client import fetch_trains


def parse_routes(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch CTA train positions and print a sample.")
    parser.add_argument(
        "--routes",
        default="red,blue,brn,g,org,pink,p,y",
        help="Comma-separated route codes (default: all major lines).",
    )
    parser.add_argument(
        "--key-file",
        type=Path,
        help="Path to CTA API key file (default: repo_root/cta_api_key.txt).",
    )

    args = parser.parse_args(argv)
    routes = parse_routes(args.routes)

    if not routes:
        parser.error("At least one route is required.")

    try:
        df = fetch_trains(routes=routes, key_path=args.key_file)
    except Exception as exc:
        parser.error(str(exc))
        return 1

    print(df.head())
    return 0


if __name__ == "__main__":
    sys.exit(main())
