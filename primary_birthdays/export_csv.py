"""Export birthday report to CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


CSV_COLUMNS = ["Month", "Name", "Birthday", "Age", "Role", "Class", "Position"]


def export_csv(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()

        for month_name in report["month_names"]:
            for row in report["by_month"][month_name]:
                writer.writerow(_row_to_csv(row, month_name))


def _row_to_csv(row: dict[str, Any], month_name: str) -> dict[str, str]:
    return {
        "Month": month_name,
        "Name": row.get("name", ""),
        "Birthday": row.get("birthday", ""),
        "Age": str(row.get("age", "")),
        "Role": row.get("role", ""),
        "Class": row.get("class", ""),
        "Position": row.get("position", ""),
    }
