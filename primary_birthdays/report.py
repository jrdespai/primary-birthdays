"""Build and sort the combined Primary birthday report."""

from __future__ import annotations

from typing import Any

MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def birthday_sort_key(row: dict[str, Any]) -> tuple[str, str]:
    mmdd = row.get("mmdd") or "9999"
    return (mmdd, row.get("name", "").lower())


def filter_by_month(rows: list[dict[str, Any]], month: int | None) -> list[dict[str, Any]]:
    if month is None:
        return rows
    month_str = f"{month:02d}"
    return [r for r in rows if (r.get("mmdd") or "")[:2] == month_str]


def build_report(
    children: list[dict[str, Any]],
    leaders: list[dict[str, Any]],
    month: int | None = None,
) -> dict[str, Any]:
    children = filter_by_month(children, month)
    leaders = filter_by_month(leaders, month)

    combined = children + leaders
    by_month = _group_by_month(combined)

    flat_rows: list[dict[str, Any]] = []
    for month_name in MONTH_NAMES:
        for row in by_month[month_name]:
            flat_rows.append({**row, "month": month_name})

    return {
        "by_month": by_month,
        "flat_rows": flat_rows,
        "month_names": MONTH_NAMES,
        "totals": {
            "children": len(children),
            "leaders": len(leaders),
            "all": len(flat_rows),
        },
    }


def _group_by_month(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {name: [] for name in MONTH_NAMES}

    for row in rows:
        mmdd = row.get("mmdd") or ""
        if len(mmdd) >= 2 and mmdd[:2].isdigit():
            month_index = int(mmdd[:2]) - 1
            if 0 <= month_index < 12:
                grouped[MONTH_NAMES[month_index]].append(row)

    for name in MONTH_NAMES:
        grouped[name] = sorted(grouped[name], key=birthday_sort_key)

    return grouped
