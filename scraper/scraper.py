"""
scraper_playwright.py — Zona U UCAB scraper using Playwright (local browser).

Credentials stay on YOUR machine only — never sent to third-party servers.
Requires: pip install playwright && playwright install chromium

Usage:
    python scraper_playwright.py
"""

import os
import re
import json
import pathlib
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
USERNAME     = os.getenv("UCAB_USERNAME")
PASSWORD     = os.getenv("UCAB_PASSWORD")
RECARGAS_URL = (
    "https://experience.elluciancloud.com/ucabu/page/"
    "001G000000oSi8wIAC/DTI/ExperienceRecargaEstacionamiento/"
    "ExperienceRecargaEstacionamientoCard/"
)
OUTPUT_PATH  = pathlib.Path(os.getenv("OUTPUT_PATH", "../dashboard/public/data.json"))

if not USERNAME or not PASSWORD:
    raise ValueError("UCAB_USERNAME and UCAB_PASSWORD must be set in .env")


# ── Browser helpers ────────────────────────────────────────────────────────────
def login(page):
    """
    Navigate to RECARGAS_URL (redirects to SSO), fill credentials, submit.
    Waits until the balance element is visible before returning.
    Credentials are typed directly into the browser — never sent over the network
    to any third party.
    """
    print("  Navigating to portal...")
    page.goto(RECARGAS_URL, wait_until="domcontentloaded")

    # SSO form
    page.wait_for_selector("input#username", timeout=15000)
    page.fill("input#username", USERNAME)
    page.fill("input#password", PASSWORD)
    page.click("button[type='submit']")

    # Wait until we're back on the Recargas page with balance loaded
    print("  Waiting for balance to load...")
    try:
        # Wait for network to settle after SSO redirect
        page.wait_for_load_state("networkidle", timeout=20000)
        # Then wait for the balance text to appear (not the loading spinner)
        page.wait_for_function(
            """() => {
                const body = document.body;
                if (!body) return false;
                const text = body.innerText || '';
                return text.includes('Bs') && !text.includes('Cargando');
            }""",
            timeout=15000,
        )
    except PWTimeout:
        print("  WARNING: Balance may still be loading")


def get_text(page):
    """Return visible text content of the page."""
    return page.inner_text("body")


# ── Parsers ────────────────────────────────────────────────────────────────────
def parse_student(text):
    match = re.search(r'Hola[,!\s]+([^\n!#]+)', text, re.IGNORECASE)
    full_name = match.group(1).strip().rstrip("!,") if match else "Desconocido"
    parts = full_name.split()
    first = parts[0] if parts else full_name
    return {
        "name": first,
        "full_name": full_name,
        "initials": first[0].upper() if first else "?",
    }


def parse_balance(text):
    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*Bs', text)
    raw = match.group(1) if match else "0,00"
    as_float = float(raw.replace(".", "").replace(",", "."))
    return {
        "balance_bs": as_float,
        "balance_formatted": raw + " Bs",
        "last_updated": datetime.now().isoformat(),
    }


def _parse_amount_ve(raw):
    clean = re.sub(r'[^\d,.]', '', raw)
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    elif "," in clean:
        clean = clean.replace(",", ".")
    return float(clean) if clean else 0.0


def parse_movements_from_table(page):
    """
    Reads the Detalle de transacciones table directly from the DOM.
    Returns list of movement dicts.

    Columns: Fecha | Número | Código | Descripción | Recarga | Term | Cajero
    """
    rows = page.query_selector_all("table tbody tr")
    results = []
    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) < 5:
            continue
        try:
            date        = cells[0].inner_text().strip()
            numero      = cells[1].inner_text().strip()
            amount_raw  = cells[4].inner_text().strip()
            cajero      = cells[6].inner_text().strip() if len(cells) > 6 else ""

            is_debit = bool(re.search(r'descuento|entrada vehicular', numero, re.IGNORECASE))
            amount   = _parse_amount_ve(amount_raw)

            results.append({
                "date":        date,
                "description": numero,
                "amount_bs":   round(amount * (-1 if is_debit else 1), 2),
                "type":        "debit" if is_debit else "credit",
                "cajero":      cajero,
            })
        except Exception:
            continue
    return results


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    now = datetime.now().isoformat()
    print("Zona U UCAB Scraper (Playwright)")
    print("=" * 40)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page    = context.new_page()

        # ── Pass 1: balance + student name ─────────────────────────────────────
        print("\n[1/2] Scraping dashboard (balance + name)...")
        login(page)
        dashboard_text = get_text(page)

        student = parse_student(dashboard_text)
        wallet  = parse_balance(dashboard_text)
        print(f"  Student : {student['full_name']}")
        print(f"  Balance : {wallet['balance_formatted']}")

        # ── Pass 2: movements table ────────────────────────────────────────────
        print("\n[2/2] Scraping movements...")
        try:
            # Click the Movimientos button (has img alt="Movimientos")
            page.click("img[alt='Movimientos']")
            # Wait for the table to appear
            page.wait_for_selector("table tbody tr", timeout=15000)
        except PWTimeout:
            print("  WARNING: Movements table did not load in time")

        movements = parse_movements_from_table(page)
        print(f"  Movements: {len(movements)} entries")

        browser.close()

    # access_logs = parking entries (debits)
    access_logs = [m for m in movements if m["type"] == "debit"]

    output = {
        "scraped_at":  now,
        "student":     student,
        "wallet":      wallet,
        "movements":   movements,
        "access_logs": access_logs,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2))

    print(f"\nDone! Output written to: {OUTPUT_PATH}")
    print(f"  Student  : {student['full_name']}")
    print(f"  Balance  : {wallet['balance_formatted']}")
    print(f"  Movements: {len(movements)} entries")
    print(f"  Access   : {len(access_logs)} parking entries")

    if not movements:
        print("\n  NOTE: No movements parsed.")


if __name__ == "__main__":
    main()
