#!/usr/bin/env python3
"""
find_fcc.py - List every product (FCC ID) registered under a given FCC grantee code.

An FCC ID is made of a grantee code + a product code, e.g. ``2BPFE-DD001`` is
grantee ``2BPFE`` (WaveGo Tech LLC) + product ``DD001`` (Skyrover S1). Querying the
FCC Equipment Authorization System (EAS) by grantee code therefore returns every
device that grantee has ever certified.

Usage:
    python3 find_fcc.py "2BPFE"
    python3 find_fcc.py "2BPFE" --all          # dump every raw XML field
    python3 find_fcc.py "2BPFE" --records 500  # cap rows fetched
    python3 find_fcc.py "2BPFE" --no-names     # skip product-name lookup (faster)

Grant details (product name, contact, certifier):
    The XML feed only carries 11 fields and has no product/model name. Each
    device's FCC Form 731 Grant of Equipment Authorization holds more: the human
    name (e.g. "XTRA MUSE") in the "Notes" field, the "Attention:" contact person
    on the application, and the certifying TCB. The contact and TCB are strong
    fingerprints for linking shell companies. We harvest the per-device
    application_id tokens from the HTML search results, then fetch each grant form
    to read these. Use --no-names to skip this (one extra request per product).

Beating Akamai:
    apps.fcc.gov sits behind Akamai Bot Manager, which fingerprints the TLS
    ClientHello (JA3/JA4). Plain ``requests`` gets tarpitted into multi-minute
    timeouts. If ``curl_cffi`` is installed we impersonate Chrome's TLS stack,
    which sails through in well under a second. We fall back to ``requests`` only
    if ``curl_cffi`` is unavailable.

This is a companion to main.py, which hunts for DJI shell companies by OcuSync
frequency fingerprints. Here we go the other way: given a grantee, show its catalog.
"""

import argparse
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests
from fake_useragent import UserAgent
from rich.console import Console
from rich.table import Table
from rich import box

# curl_cffi lets us impersonate a real browser's TLS fingerprint, which is what
# gets us past Akamai. It exposes a requests-compatible API, so the rest of the
# code is engine-agnostic.
try:
    from curl_cffi import requests as curl_requests
    from curl_cffi.requests.exceptions import (
        Timeout as CurlTimeout,
        HTTPError as CurlHTTPError,
        RequestException as CurlError,
    )

    HAVE_CURL = True
except ImportError:  # pragma: no cover - curl_cffi is the happy path
    HAVE_CURL = False

# Build engine-agnostic exception tuples. Order matters where we catch them:
# timeouts and HTTP errors are subclasses of the broad curl error, so they must
# be caught before the connection/catch-all tuple.
TIMEOUT_EXC = (requests.exceptions.Timeout,) + ((CurlTimeout,) if HAVE_CURL else ())
HTTP_EXC = (requests.exceptions.HTTPError,) + ((CurlHTTPError,) if HAVE_CURL else ())
CONN_EXC = (requests.exceptions.ConnectionError,) + ((CurlError,) if HAVE_CURL else ())

BASE_URL = "https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm?calledFromFrame=N"
SEARCH_URL = "https://apps.fcc.gov/oetcf/eas/reports/GenericSearchResult.cfm"
GRANT_FORM_URL = "https://apps.fcc.gov/oetcf/tcb/reports/Tcb731GrantForm.cfm"


class ScrapingError(Exception):
    pass


def build_session(timeout: int):
    """Create a session and hydrate FCC/Akamai cookies.

    Prefers a curl_cffi session impersonating Chrome (beats Akamai's TLS
    fingerprinting); falls back to plain requests with a random user agent.
    """
    if HAVE_CURL:
        session = curl_requests.Session(impersonate="chrome")
        # curl_cffi already sets browser-matching default headers; we only add
        # the form's expected provenance headers.
        session.headers.update({"Referer": BASE_URL, "Origin": "https://apps.fcc.gov"})
    else:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": UserAgent().random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://apps.fcc.gov",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": BASE_URL,
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "Priority": "u=0, i",
            }
        )

    tries = 0
    while tries <= 10:
        try:
            response = session.get(BASE_URL, timeout=timeout)
            if response.status_code == 200:
                return session
        except TIMEOUT_EXC + CONN_EXC:
            pass
        tries += 1
        time.sleep(1)

    raise ScrapingError("could not initialize an FCC scraping session (site timed out)")


def _search_form(grantee_code: str, records: int, outputformat: str) -> dict:
    """The EAS search form payload. ``outputformat`` is 'XML' for the data feed
    or '' for the HTML results page (which carries the application_id tokens)."""
    return {
        "grantee_code": grantee_code,
        "product_code": "",
        "applicant_name": "",
        "grant_date_from": "",
        "grant_date_to": "",
        "comments": "",
        "application_purpose": "",
        "application_purpose_description": "",
        "grant_code_1": "",
        "grant_code_2": "",
        "grant_code_3": "",
        "test_firm": "",
        "application_status": "",
        "application_status_description": "",
        "equipment_class": "",
        "equipment_class_description": "",
        # No frequency filter: we want the grantee's full catalog, not just OcuSync.
        # The *_exact_match flags stay "on" to mirror the browser's working request
        # (they're harmless when their value fields are blank).
        "lower_frequency": "",
        "upper_frequency": "",
        "freq_exact_match": "on",
        "bandwidth_from": "",
        "emission_designator": "",
        "tolerance_from": "",
        "tolerance_to": "",
        "tolerance_exact_match": "on",
        "power_output_from": "",
        "power_output_to": "",
        "power_exact_match": "on",
        "rule_part_1": "",
        "rule_part_2": "",
        "rule_part_3": "",
        "rule_part_exact_match": "on",
        "product_description": "",
        "modular_type_description": "",
        "tcb_code": "",
        "tcb_code_description": "",
        "tcb_scope": "",
        "tcb_scope_description": "",
        "outputformat": outputformat,
        "show_records": str(records),
        "fetchfrom": "0",
        "calledFromFrame": "N",
    }


def fetch_grantee_xml(session, grantee_code: str, records: int, timeout: int) -> str:
    """POST the EAS search form, asking for every product under ``grantee_code``."""
    try:
        response = session.post(
            SEARCH_URL,
            params={"RequestTimeout": "500"},
            data=_search_form(grantee_code, records, "XML"),
            timeout=timeout,
        )
        response.raise_for_status()
    except TIMEOUT_EXC:
        raise ScrapingError("the FCC search request timed out")
    except HTTP_EXC as exc:
        raise ScrapingError(f"the FCC returned an HTTP error: {exc}")
    except CONN_EXC as exc:
        raise ScrapingError(f"could not reach the FCC: {exc}")
    return response.text


def fetch_application_ids(session, grantee_code: str, records: int, timeout: int) -> dict:
    """Return {fcc_id: application_id_token}.

    The XML feed has no application_id, but the HTML results page embeds it in
    every device's grant/exhibit detail links. Tokens come URL-encoded; we keep
    them that way and decode just before use.
    """
    try:
        response = session.post(
            SEARCH_URL,
            params={"RequestTimeout": "500"},
            data=_search_form(grantee_code, records, ""),
            timeout=timeout,
        )
        response.raise_for_status()
    except TIMEOUT_EXC:
        raise ScrapingError("the FCC HTML search timed out")
    except (HTTP_EXC + CONN_EXC) as exc:
        raise ScrapingError(f"could not reach the FCC: {exc}")

    mapping = {}
    pairs = re.findall(
        r'application_id=([^&"]+)&(?:amp;)?fcc_id=([^"&]+)', response.text
    )
    for appid, fcc_id in pairs:
        mapping.setdefault(fcc_id, appid)
    return mapping


def _clean(fragment: str) -> str:
    """Strip tags/entities and collapse whitespace from an HTML fragment."""
    text = re.sub(r"<[^>]+>", " ", fragment).replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def _grant_field(html: str, label: str) -> str:
    """Pull a labelled value out of a Form 731 grant table (e.g. 'Notes')."""
    for row in re.findall(r"<TR[^>]*>(.*?)</TR>", html, re.S | re.I):
        cells = re.findall(r"<TD[^>]*>(.*?)</TD>", row, re.S | re.I)
        clean = [_clean(c) for c in cells]
        clean = [c for c in clean if c]
        if len(clean) >= 2 and clean[0].rstrip(":").strip().lower() == label.lower():
            return clean[1]
    return ""


def _grant_tcb(html: str) -> str:
    """The certifying Telecommunication Certification Body (the 'By:' block).

    The TCB name is the first line of its cell; its address follows after <BR>s.
    """
    anchor = re.search(r"By:\s*</td>", html, re.I)
    if not anchor:
        return ""
    tail = html[anchor.end(): anchor.end() + 1500]
    for cell in re.findall(r"<td[^>]*>(.*?)</td>", tail, re.S | re.I):
        name = _clean(re.split(r"<br>", cell, maxsplit=1, flags=re.I)[0])
        # Skip the empty spacer cell and the adjacent "Date of Grant" cell.
        if not name or name.lower().startswith("date of grant"):
            continue
        return name
    return ""


def _grant_attention(html: str) -> str:
    """The 'Attention:' contact person named on the application."""
    match = re.search(r"Attention:(.*?)</strong>", html, re.S | re.I)
    if not match:
        return ""
    return _clean(match.group(1)).rstrip(",").strip()


def fetch_grant_details(session, appid: str, fcc_id: str, timeout: int) -> dict:
    """Read product name, certifying TCB and contact from a Form 731 grant."""
    try:
        response = session.get(
            GRANT_FORM_URL,
            params={
                "mode": "COPY",
                "RequestTimeout": "500",
                "tcb_code": "",
                # Decode the token (%3D%3D -> ==); the client re-encodes it safely.
                "application_id": urllib.parse.unquote(appid),
                "fcc_id": fcc_id,
            },
            timeout=timeout,
        )
        response.raise_for_status()
    except (TIMEOUT_EXC + HTTP_EXC + CONN_EXC) as exc:
        raise ScrapingError(f"could not fetch grant form for {fcc_id}: {exc}")
    html = response.text
    return {
        "name": _grant_field(html, "Notes"),
        "tcb": _grant_tcb(html),
        "attention": _grant_attention(html),
    }


def resolve_grant_details(
    session, products: list, grantee_code: str, records: int, timeout: int,
    console: Console,
) -> None:
    """Populate each product's ``_product_name``/``_tcb``/``_attention`` in place
    from its Form 731 grant."""
    try:
        mapping = fetch_application_ids(session, grantee_code, records, timeout)
    except ScrapingError as exc:
        console.print(f"[yellow]!!! could not resolve grant details: {exc}[/yellow]")
        mapping = {}

    total = len(products)
    with console.status("[dim]resolving grant details...[/dim]") as status:
        for i, product in enumerate(products, 1):
            fcc_id = product["fcc_id"]
            product["_product_name"] = ""
            product["_tcb"] = ""
            product["_attention"] = ""
            appid = mapping.get(fcc_id)
            if not appid:
                continue
            status.update(
                f"[dim]resolving grant details ({i}/{total}): {fcc_id}[/dim]"
            )
            try:
                details = fetch_grant_details(session, appid, fcc_id, timeout)
                product["_product_name"] = details["name"]
                product["_tcb"] = details["tcb"]
                product["_attention"] = details["attention"]
            except ScrapingError:
                pass


def _text(row, tag):
    value = row.findtext(tag)
    return value.strip() if value else ""


def _fmt_freq(value: str) -> str:
    """FCC frequencies arrive as e.g. '5829.50000000'; trim the noise."""
    value = (value or "").strip()
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    return value


def parse_rows(xml_text: str):
    """Return (products, all_tags).

    The FCC returns one <Row> per frequency band, so a single FCC ID can appear
    several times. We collapse to one entry per FCC ID and accumulate the
    distinct frequency ranges. ``products`` is a list of dicts keyed by the raw
    XML tag names (so --all can show whatever the FCC actually sent).
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ScrapingError(f"could not parse the FCC response as XML: {exc}")

    rows = root.findall("Row")
    all_tags = []
    products = {}

    for row in rows:
        for child in row:
            if child.tag not in all_tags:
                all_tags.append(child.tag)

        fcc_id = _text(row, "fcc_id")
        # Some grantees return blank fcc_id on stray rows; skip those.
        if not fcc_id:
            continue

        low = _fmt_freq(_text(row, "lower_freq_mhz"))
        high = _fmt_freq(_text(row, "upper_freq_mhz"))
        freq = f"{low} - {high}" if (low or high) else ""

        if fcc_id not in products:
            entry = {
                child.tag: (child.text.strip() if child.text else "") for child in row
            }
            entry["fcc_id"] = fcc_id
            entry["_frequencies"] = []
            products[fcc_id] = entry

        if freq and freq not in products[fcc_id]["_frequencies"]:
            products[fcc_id]["_frequencies"].append(freq)

    return list(products.values()), all_tags


def _parse_date(value: str):
    """FCC dates are m/d/Y; return an ISO string for display and a sort key."""
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return time.strftime("%Y-%m-%d", time.strptime(value, fmt))
        except (ValueError, TypeError):
            continue
    return value


def fcc_gov_url(fcc_id: str) -> str:
    return "https://gov.fccid.io/" + fcc_id


def _product_code(fcc_id: str, grantee_code: str) -> str:
    """The product code is whatever follows the grantee code in the FCC ID."""
    if "-" in fcc_id:
        return fcc_id.split("-", 1)[1]
    if fcc_id.upper().startswith(grantee_code.upper()):
        return fcc_id[len(grantee_code):]
    return fcc_id


def render_table(grantee_code: str, products: list, console: Console, show_names: bool):
    """Curated, colorized one-row-per-product view."""
    # Newest grants first.
    products = sorted(
        products,
        key=lambda p: _parse_date(p.get("grant_date", "")),
        reverse=True,
    )

    table = Table(
        title=f"[bold]FCC products for grantee [yellow]{grantee_code}[/yellow]  "
        f"([cyan]{len(products)}[/cyan] found)[/bold]",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold white",
        expand=False,
    )
    table.add_column("FCC ID", style="bold yellow", no_wrap=True)
    if show_names:
        table.add_column("Product name", style="bold green")
    table.add_column("Product code", style="cyan", no_wrap=True)
    table.add_column("Applicant", style="white")
    if show_names:
        # Per-device fingerprints (only available once we fetch the grant form).
        table.add_column("Contact", style="bold magenta")
        table.add_column("TCB (certifier)", style="blue")
    table.add_column("Granted", style="green", no_wrap=True)
    table.add_column("fccid.io", style="dim cyan", no_wrap=True)

    for product in products:
        cells = [product["fcc_id"]]
        if show_names:
            cells.append(product.get("_product_name") or "-")
        cells.append(_product_code(product["fcc_id"], grantee_code))
        cells.append(product.get("applicant_name", ""))
        if show_names:
            cells.append(product.get("_attention") or "-")
            cells.append(product.get("_tcb") or "-")
        cells.append(_parse_date(product.get("grant_date", "")))
        cells.append(fcc_gov_url(product["fcc_id"]))
        table.add_row(*cells)

    console.print(table)


def render_all(grantee_code: str, products: list, all_tags: list, console: Console):
    """Raw dump of every XML field the FCC returned (one column per tag)."""
    raw_freq_tags = ("lower_freq_mhz", "upper_freq_mhz")
    columns = [t for t in all_tags if t not in raw_freq_tags]
    # Include grant-form fields if they were resolved.
    if any(p.get("_product_name") for p in products):
        columns.append("product_name")
    if any(p.get("_attention") for p in products):
        columns.append("attention")
    if any(p.get("_tcb") for p in products):
        columns.append("tcb")
    columns.append("frequencies")

    table = Table(
        title=f"[bold]ALL FCC fields for grantee [yellow]{grantee_code}[/yellow] "
        f"([cyan]{len(products)}[/cyan] products)[/bold]",
        box=box.SIMPLE_HEAVY,
        header_style="bold cyan",
        title_style="bold white",
    )
    for col in columns:
        table.add_column(col, overflow="fold")

    for product in sorted(
        products, key=lambda p: _parse_date(p.get("grant_date", "")), reverse=True
    ):
        cells = []
        for col in columns:
            if col == "frequencies":
                cells.append("\n".join(product.get("_frequencies", [])) or "-")
            elif col == "product_name":
                cells.append(product.get("_product_name", ""))
            elif col == "attention":
                cells.append(product.get("_attention", ""))
            elif col == "tcb":
                cells.append(product.get("_tcb", ""))
            else:
                cells.append(product.get(col, ""))
        table.add_row(*cells)

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="List every product (FCC ID) registered under an FCC grantee code."
    )
    parser.add_argument("grantee_code", help='FCC grantee code, e.g. "2BPFE"')
    parser.add_argument(
        "--records",
        type=int,
        default=1000,
        help="max rows to request from the FCC (default: 1000)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="per-request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="dump every raw XML field instead of the curated view",
    )
    parser.add_argument(
        "--no-names",
        action="store_true",
        help="skip the per-product grant-form name lookup (faster)",
    )
    args = parser.parse_args()

    grantee_code = args.grantee_code.strip().upper()
    console = Console()
    show_names = not args.no_names

    engine = "curl_cffi (Chrome TLS impersonation)" if HAVE_CURL else "requests"
    console.print(f"[dim]::: opening FCC scraping session via {engine}...[/dim]")
    try:
        session = build_session(args.timeout)
    except ScrapingError as exc:
        console.print(f"[bold red]XXX:[/bold red] {exc}")
        sys.exit(1)

    console.print(f"[dim]::: querying products for grantee '{grantee_code}'...[/dim]")
    try:
        xml_text = fetch_grantee_xml(session, grantee_code, args.records, args.timeout)
        products, all_tags = parse_rows(xml_text)
    except ScrapingError as exc:
        console.print(f"[bold red]XXX:[/bold red] {exc}")
        sys.exit(1)

    if not products:
        console.print(
            f"[yellow]No products found for grantee '{grantee_code}'.[/yellow]"
        )
        sys.exit(0)

    if show_names:
        resolve_grant_details(
            session, products, grantee_code, args.records, args.timeout, console
        )

    if args.all:
        render_all(grantee_code, products, all_tags, console)
    else:
        render_table(grantee_code, products, console, show_names)


if __name__ == "__main__":
    main()
