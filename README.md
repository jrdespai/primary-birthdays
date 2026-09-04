# Primary Birthday Report

Local Python tool that generates a birthday report for Primary children and their teachers using Leader and Clerk Resources (LCR) / Member Tools data.

**Unofficial tool — not endorsed by the Church.** Uses reverse-engineered internal LCR endpoints via [lcr-api-2](https://pypi.org/project/lcr-api-2/). Run locally only; do not upload membership data to cloud services.

## Prerequisites

- Python 3.10+
- Google Chrome (for Selenium login)
- LCR/Member Tools access as Primary presidency, secretary, or ward clerk

## Setup

```bash
cd primary-birthdays
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Church Account credentials and ward unit number
```

Your ward unit number appears in parentheses on the LCR home page after your ward name.

## Usage

```bash
python main.py
```

Writes to `output/`:

- `primary-birthdays.csv` — spreadsheet-friendly
- `primary-birthdays.html` — printable report grouped by class and month

### Options

```bash
python main.py --month 3          # Only March birthdays
python main.py --org-name Primary # Primary organization name (default: Primary)
python main.py --output-dir ./output
```

## Report structure

1. **Primary children** — grouped by class (Nursery through Valiant), sorted by birthday within each class
2. **Primary teachers** — sorted by birthday, with class assignment from calling

## Troubleshooting

- **Login fails / MFA**: Church Account 2FA may require a visible browser session. Try running with a non-headless Chrome (see lcr-api-2 docs) or update lcr-api-2.
- **ChromeDriver errors**: The tool auto-configures Chrome on macOS via Selenium Manager. If issues persist, set `CHROME_BIN` in `.env` (see `.env.example`). You do not need to install chromedriver manually on most Macs.
- **ChromeDriver errors (legacy)**: `rm -rf ~/.wdm/drivers/chromedriver` and reinstall, or set `CHROMEDRIVER_PATH`.
- **Empty Primary roster**: Confirm your calling grants Primary organization access in Member Tools.

## Verification

After generating a report, compare against Member Tools:

1. **Children** — LCR → Callings → Primary → select all classes; counts per class should match the HTML report.
2. **Teachers** — LCR → Members with Callings; filter to Primary teacher callings.
3. **Birthdates** — Spot-check a few names against the member list or birthday list report.

Run unit tests locally (no LCR credentials required):

```bash
python -m pytest tests/ -v
```


If automation breaks, export JSON from LCR in Chrome DevTools (Network tab) on the Primary Organization or Class Attendance pages and join with the Birthday List report manually.
