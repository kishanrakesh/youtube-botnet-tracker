import csv
import re
import os
from pathlib import Path
from typing import Iterable
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

CSV_FILE   = "video_comment_channels.csv"          # <-- change or pass via CLI args
OUT_DIR    = Path("screenshots")  # all PNGs will be dropped here
TIMEOUT_MS = 30_000               # 30 s per page

def slugify(url: str) -> str:
    """Turn a URL into a filesystem-safe stem."""
    return re.sub(r"[^A-Za-z0-9]+", "_", url).strip("_")[:80]

def read_urls(path: str) -> Iterable[str]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)

        next(reader, None)          # ← skip the header row

        for row in reader:
            if row and row[0].strip() and int(row[2]) > 10:
                yield row[0].strip()

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    urls = list(read_urls(CSV_FILE))
    if not urls:
        print("No URLs found in first column—exiting.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page    = browser.new_page()

        for idx, url in enumerate(urls, start=1):
            fname = OUT_DIR / f"{idx:04d}_{slugify(url)}.png"
            try:
                page.goto(url, timeout=TIMEOUT_MS, wait_until="networkidle")
                page.screenshot(path=fname, full_page=True)
                print(f"[✓] {url}  →  {fname}")
            except PWTimeout:
                print(f"[×] Timed out: {url}")
            except Exception as e:
                print(f"[×] {url}  →  {e}")

        browser.close()

if __name__ == "__main__":
    main()