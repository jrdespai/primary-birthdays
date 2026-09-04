"""Export birthday report to printable HTML."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


def export_html(report: dict[str, Any], output_path: Path, templates_dir: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("report.html")
    html = template.render(
        report=report,
        generated_on=date.today().strftime("%B %d, %Y"),
    )
    output_path.write_text(html, encoding="utf-8")
