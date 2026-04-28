"""
scraper.py — Zona U UCAB scraper (Playwright, multi-user ready)

Credentials are passed as parameters — never stored, never logged,
never sent to third-party services. Chromium runs locally on the server.
"""

import re
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

RECARGAS_URL = (
    "https://experience.elluciancloud.com/ucabu/page/"
    "001G000000oSi8wIAC/DTI/ExperienceRecargaEstacionamiento/"
    "ExperienceRecargaEstacionamientoCard/"
)


# ── Browser helpers ────────────────────────────────────────────────────────────

def _login(page, username: str, password: str):
    """
    Navigate to RECARGAS_URL (redirects to SSO), fill credentials, submit.
    Waits until balance is visible before returning.
    Credentials never leave this process — Playwright types them directly
    into the local Chromium instance.
    """
    page.goto(RECARGAS_URL, wait_until="domcontentloaded")
    page.wait_for_selector("input#username", timeout=15000)
    page.fill("input#username", username)
    page.fill("input#password", password)
    page.click("button[type='submit']")

    try:
        page.wait_for_load_state("networkidle", timeout=20000)
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
        pass  # Balance might still load — parsers handle missing data gracefully


# ── Parsers ────────────────────────────────────────────────────────────────────

def _parse_student(text: str) -> dict:
    match = re.search(r'Hola[,!\s]+([^\n!#]+)', text, re.IGNORECASE)
    full_name = match.group(1).strip().rstrip("!,") if match else "Desconocido"
    parts = full_name.split()
    first = parts[0] if parts else full_name
    return {
        "name": first,
        "full_name": full_name,
        "initials": first[0].upper() if first else "?",
    }


def _parse_balance(text: str) -> dict:
    match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*Bs', text)
    raw = match.group(1) if match else "0,00"
    as_float = float(raw.replace(".", "").replace(",", "."))
    return {
        "balance_bs": as_float,
        "balance_formatted": raw + " Bs",
        "last_updated": datetime.now().isoformat(),
    }


def _parse_amount_ve(raw: str) -> float:
    clean = re.sub(r'[^\d,.]', '', raw)
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    elif "," in clean:
        clean = clean.replace(",", ".")
    return float(clean) if clean else 0.0


def _parse_movements(page) -> list:
    """Read transactions table directly from the DOM."""
    rows = page.query_selector_all("table tbody tr")
    results = []
    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) < 5:
            continue
        try:
            date       = cells[0].inner_text().strip()
            numero     = cells[1].inner_text().strip()
            amount_raw = cells[4].inner_text().strip()
            cajero     = cells[6].inner_text().strip() if len(cells) > 6 else ""

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


# ── Public API ─────────────────────────────────────────────────────────────────

def scrape(username: str, password: str) -> dict:
    """
    Run the full scrape for a given user.
    Returns a dict with student, wallet, movements, access_logs.
    Raises an exception if login fails or the portal is unreachable.
    """
    now = datetime.now().isoformat()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page    = context.new_page()

        # ── Pass 1: balance + student name ─────────────────────────────────────
        _login(page, username, password)

        # Detect login failure (SSO still showing = bad credentials)
        if "sso.ucab.edu.ve" in page.url or page.query_selector("input#username"):
            browser.close()
            raise ValueError("Credenciales incorrectas")

        dashboard_text = page.inner_text("body")
        student = _parse_student(dashboard_text)
        wallet  = _parse_balance(dashboard_text)

        # ── Pass 2: movements table ─────────────────────────────────────────────
        try:
            page.click("img[alt='Movimientos']")
            page.wait_for_selector("table tbody tr", timeout=15000)
        except PWTimeout:
            pass  # Return empty movements rather than crashing

        movements = _parse_movements(page)
        browser.close()

    access_logs = [m for m in movements if m["type"] == "debit"]

    return {
        "scraped_at":  now,
        "student":     student,
        "wallet":      wallet,
        "movements":   movements,
        "access_logs": access_logs,
    }
