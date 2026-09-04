"""Tests for CSV and HTML export."""

from pathlib import Path

from primary_birthdays.export_csv import export_csv
from primary_birthdays.export_html import export_html
from primary_birthdays.report import build_report


def test_export_csv_and_html(tmp_path: Path):
    children = [
        {
            "uuid": "c1",
            "name": "Anderson, Emma",
            "birthday": "03/15/2020",
            "mmdd": "0315",
            "age": 5,
            "role": "Child",
            "class": "Sunbeams",
            "position": "",
        }
    ]
    teachers = [
        {
            "uuid": "t1",
            "name": "Clark, Sarah",
            "birthday": "01/10/1993",
            "mmdd": "0110",
            "age": 32,
            "role": "Teacher",
            "class": "Sunbeams",
            "position": "Primary Teacher",
        }
    ]
    report = build_report(children, teachers)

    csv_path = tmp_path / "primary-birthdays.csv"
    html_path = tmp_path / "primary-birthdays.html"
    templates_dir = Path(__file__).resolve().parent.parent / "templates"

    export_csv(report, csv_path)
    export_html(report, html_path, templates_dir)

    csv_text = csv_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")

    assert "Anderson, Emma" in csv_text
    assert "Clark, Sarah" in csv_text
    assert "Primary Birthday Report" in html_text
    assert "January" in html_text
    assert "March" in html_text
