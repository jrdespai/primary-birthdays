#!/usr/bin/env python3
"""Generate Primary children and teacher birthday reports from LCR."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from primary_birthdays.auth import LcrConfigError, lcr_session
from primary_birthdays.export_csv import export_csv
from primary_birthdays.export_html import export_html
from primary_birthdays.fetch import fetch_members_and_org_map, fetch_members_with_callings
from primary_birthdays.filter import (
    extract_primary_children,
    extract_primary_leader_uuids,
    extract_primary_leaders,
    index_members_by_uuid,
)
from primary_birthdays.report import build_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Primary birthday report from LCR / Member Tools."
    )
    parser.add_argument(
        "--month",
        type=int,
        choices=range(1, 13),
        metavar="N",
        help="Filter to birthdays in month N (1-12). Default: full year.",
    )
    parser.add_argument(
        "--org-name",
        default="Primary",
        help="Primary organization name as shown in LCR (default: Primary).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for generated files (default: output/).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        with lcr_session() as api:
            logging.info("Fetching LCR data...")
            members, org_map = fetch_members_and_org_map(api)
            callings = fetch_members_with_callings(api)

            members_by_uuid = index_members_by_uuid(members)
            leader_uuids = extract_primary_leader_uuids(callings, org_name=args.org_name)
            children = extract_primary_children(members, org_map, leader_uuids)
            leaders = extract_primary_leaders(
                callings,
                members_by_uuid,
                org_name=args.org_name,
            )

            report = build_report(children, leaders, month=args.month)

            csv_path = args.output_dir / "primary-birthdays.csv"
            html_path = args.output_dir / "primary-birthdays.html"
            templates_dir = Path(__file__).resolve().parent / "templates"

            export_csv(report, csv_path)
            export_html(report, html_path, templates_dir)

            logging.info(
                "Report written: %d children, %d leaders",
                report["totals"]["children"],
                report["totals"]["leaders"],
            )
            logging.info("CSV:  %s", csv_path.resolve())
            logging.info("HTML: %s", html_path.resolve())

    except LcrConfigError as exc:
        logging.error("%s", exc)
        return 1
    except Exception as exc:
        logging.error("Failed to generate report: %s", exc)
        if args.verbose:
            raise
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
