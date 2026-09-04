"""Fix lcr-api-2 ChromeDriver resolution on macOS/local dev."""

from __future__ import annotations

import os
import shutil

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import lcr

MACOS_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
_patched = False
_LAMBDA_ONLY_CHROME_ARGS = ("--single-process",)


def _sanitize_chrome_options(options) -> None:
    """Drop Lambda-only flags that crash desktop Chrome."""
    for arg in _LAMBDA_ONLY_CHROME_ARGS:
        while arg in options.arguments:
            options.arguments.remove(arg)


def _chromedriver_candidates() -> list[str]:
    return [
        os.environ.get("CHROMEDRIVER_PATH", ""),
        "/usr/local/bin/chromedriver",
        "/usr/bin/chromedriver",
        shutil.which("chromedriver") or "",
    ]


def _resolve_existing_chromedriver() -> str | None:
    for path in _chromedriver_candidates():
        if path and os.path.isfile(path):
            return path
    return None


def _ensure_chrome_binary_env() -> str | None:
    configured = os.environ.get("CHROME_BIN", "").strip()
    if configured and os.path.isfile(configured):
        return configured
    if os.path.isfile(MACOS_CHROME):
        os.environ["CHROME_BIN"] = MACOS_CHROME
        return MACOS_CHROME
    return None


def apply_lcr_selenium_fix() -> None:
    """Patch lcr.API to use Selenium Manager when chromedriver is missing."""
    global _patched
    if _patched:
        return
    _patched = True

    def patched_init(self, username, password, unit_number, beta=False):
        chrome_bin = _ensure_chrome_binary_env()
        driver_path = _resolve_existing_chromedriver()
        lcr_fallback = lcr.get_chromedriver_path()
        use_selenium_manager = not driver_path or lcr_fallback == "chromedriver"

        options = lcr.build_chrome_options()
        _sanitize_chrome_options(options)
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        if chrome_bin and not options.binary_location:
            options.binary_location = chrome_bin

        if use_selenium_manager:
            service = Service()
        else:
            service = Service(driver_path)

        self.driver = webdriver.Chrome(service=service, options=options)
        self.unit_number = unit_number
        self.session = requests.Session()
        self.beta = beta
        self.host = lcr.BETA_HOST if beta else lcr.HOST
        self._login(username, password)

    lcr.API.__init__ = patched_init
