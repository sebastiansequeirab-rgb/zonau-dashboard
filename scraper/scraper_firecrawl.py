"""
scraper.py — Zona U UCAB balance / movements scraper
Uses Firecrawl's stateless scrape_url with chained browser actions.

Target portal: https://experience.elluciancloud.com/ucabu/ (Ellucian Experience Cloud)
Login via SSO at sso.ucab.edu.ve — Firecrawl starts at RECARGAS_URL, which
redirects to SSO, we authenticate, then land back on the Recargas page.

Two scrape calls (same page, different state):
  1. Main page  → student name + balance
  2. After clicking "Movimientos" button → transactions table

Usage:
    cp .env.example .env          # fill in credentials
    python scraper.py
"""

import os
import re
import json
import time
import pathlib
from datetime import datetime
from dotenv import load_dotenv
from firecrawl import V1FirecrawlApp as FirecrawlApp

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
API_KEY      = os.getenv("FIRECRAWL_API_KEY")
USERNAME     = os.getenv("UCAB_USERNAME")
PASSWORD     = os.getenv("UCAB_PASSWORD")
RECARGAS_URL = (
    "https://experience.elluciancloud.com/ucabu/page/"
    "001G000000oSi8wIAC/DTI/ExperienceRecargaEstacionamiento/"
    "ExperienceRecargaEstacionamientoCard/"
)
OUTPUT_PATH  = pathlib.Path(os.getenv("OUTPUT_PATH", "../dashboard/public/data.json"))

if not API_KEY:
    raise ValueError("FIRECRAWL_API_KEY is not set. Copy .env.example to .env and fill it in.")
if not USERNAME or not PASSWORD:
    raise ValueError("UCAB_USERNAME and UCAB_PASSWORD must be set in .env")

app = FirecrawlApp(api_key=API_KEY)


# ── Login action chain ─────────────────────────────────────────────────────────
def login_actions(extra_actions=None):
    """
    SSO login flow prepended to every scrape call.
    RECARGAS_URL redirects to sso.ucab.edu.ve; after login it redirects back.
    The 8 s final wait lets the balance finish loading (it's async).
    """
    return [
        {"type": "wait",  "milliseconds": 3000},
        {"type": "click", "selector": "input#username"},
        {"type": "write", "text": USERNAME},
        {"type": "click", "selector": "input#password"},
        {"type": "write", "text": PASSWORD},
        {"type": "click", "selector": "button[type='submit']"},
        {"type": "wait",  "milliseconds": 8000},
    ] + (extra_actions or [])


# ── Scrape helpers ─────────────────────────────────────────────────────────────
def scrape(actions, label):
    """Runs a single Firecrawl scrape. Returns markdown string."""
    print(f"  Scraping: {label}...")
    try:
        result = app.scrape_url(
            RECARGAS_URL,
            formats=["markdown"],
            actions=actions,
            timeout=90000,
        )
        md = getattr(result, "markdown", None) or (
            result.get("markdown", "") if hasattr(result, "get") else ""
        )
        if not md:
            print(f"  WARNING: Empty markdown for {label}")
        return md or ""
    except Exception as e:
        print(f"  ERROR scraping {label}: {e}")
        return ""


def scrape_dashboard():
    """Login and capture the main Recargas page (student name + balance)."""
    # Extra 4 s wait after login: balance is loaded async and needs more time
    return scrape(login_actions([{"type": "wait", "milliseconds": 4000}]), "dashboard")


def scrape_movements():
    """Login, click the Movimientos button, wait for table to load."""
    return scrape(
        login_actions([
            {"type": "click", "selector": "img[alt='Movimientos']"},
            {"type": "wait",  "milliseconds": 8000},
        ]),
        "movimientos",
    )


# ── Parsers ────────────────────────────────────────────────────────────────────
def parse_student(markdown):
    """
    Extracts name from '## Hola, Sebastian' heading.
    Returns dict with name, full_name, initials.
    """
    match = re.search(r'##\s*Hola[,!\s]+([^\n#]+)', markdown, re.IGNORECASE)
    if not match:
        match = re.search(r'Hola[,!\s]+([^\n!#]+)', markdown, re.IGNORECASE)
    full_name = match.group(1).strip().rstrip("!,") if match else "Desconocido"
    parts = full_name.split()
    first = parts[0] if parts else full_name
    return {
        "name": first,
        "full_name": full_name,
        "initials": first[0].upper() if first else "?",
    }


def parse_balance(markdown):
    """
    Extracts balance from Venezuelan format: '1.742,69 Bs' → 1742.69
    """
    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*Bs', markdown)
    if not match:
        match = re.search(r'saldo[^\d]{0,30}(\d[\d.,]+)', markdown, re.IGNORECASE)
    raw = match.group(1) if match else "0,00"
    as_float = float(raw.replace(".", "").replace(",", "."))
    return {
        "balance_bs": as_float,
        "balance_formatted": raw + " Bs",
        "last_updated": datetime.now().isoformat(),
    }


def parse_markdown_table(markdown):
    """
    Parses all markdown table rows.
    Skips separator rows (--- pattern).
    Returns list of column-value lists.
    """
    rows = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cols = [c.strip() for c in stripped.split("|")]
        cols = [c for c in cols if c]
        if not cols:
            continue
        if all(re.match(r'^-+$', c) for c in cols):
            continue
        rows.append(cols)
    return rows


def _parse_amount_ve(raw):
    """Convert Venezuelan number string to float. '8.000,00' → 8000.0"""
    clean = re.sub(r'[^\d,.]', '', raw)
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    elif "," in clean:
        clean = clean.replace(",", ".")
    return float(clean) if clean else 0.0


def parse_movements(markdown):
    """
    Parses the Detalle de transacciones table.

    Column layout (from real portal HTML):
        Fecha | Número | Código | Descripción | Recarga | Term | Cajero

    - Parking charges (debit):
        Número = 'Descuento por entrada vehicular - Plan: ...'
    - Recargas (credit):
        Número = actual transaction number (digits)

    Amount sign:  debit → negative, credit → positive.
    """
    results = []
    rows = parse_markdown_table(markdown)

    # Skip header row (first row is headers, not a date)
    if rows and not re.match(r'\d{2}-\d{2}-\d{4}', rows[0][0] if rows[0] else ""):
        rows = rows[1:]

    for cols in rows:
        if len(cols) < 5:
            continue
        try:
            date        = cols[0]
            numero      = cols[1] if len(cols) > 1 else ""
            descripcion = cols[3] if len(cols) > 3 else ""
            amount_raw  = cols[4] if len(cols) > 4 else "0"
            cajero      = cols[6] if len(cols) > 6 else ""

            is_debit = bool(re.search(r'descuento|entrada vehicular', numero, re.IGNORECASE))
            amount   = _parse_amount_ve(amount_raw)

            results.append({
                "date":        date,
                "description": numero,
                "tipo":        descripcion,
                "amount_bs":   round(amount * (-1 if is_debit else 1), 2),
                "type":        "debit" if is_debit else "credit",
                "cajero":      cajero,
            })
        except (ValueError, IndexError):
            continue

    return results


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    now = datetime.now().isoformat()
    print("Zona U UCAB Scraper")
    print("=" * 40)

    print("\n[1/2] Scraping dashboard (balance + student name)...")
    dashboard_md = scrape_dashboard()
    time.sleep(2)

    print("\n[2/2] Scraping movements...")
    movements_md = scrape_movements()

    student   = parse_student(dashboard_md)
    wallet    = parse_balance(dashboard_md)
    movements = parse_movements(movements_md)

    # access_logs = parking entries (debits)
    access_logs = [m for m in movements if m["type"] == "debit"]

    output = {
        "scraped_at": now,
        "student":    student,
        "wallet":     wallet,
        "movements":  movements,
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
        print("\n  NOTE: No movements parsed. The Movimientos button selector may need tuning.")


if __name__ == "__main__":
    main()
