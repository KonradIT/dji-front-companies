import requests
import xml.etree.ElementTree as ET
import pandas as pd
import re
import sys
from tabulate import tabulate
import logging
import time

from fake_useragent import UserAgent

# curl_cffi impersonates a real Chrome TLS/JA3 fingerprint, which is what gets us
# past Akamai Bot Manager on apps.fcc.gov. Without it, plain requests is tarpitted:
# it either hangs, or Akamai hands back an empty 200. It exposes a requests-like API.
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

# Engine-agnostic exception tuples. TIMEOUT must be caught before CONN, since the
# curl timeout is a subclass of the broad curl error in CONN.
TIMEOUT_EXC = (requests.exceptions.Timeout,) + ((CurlTimeout,) if HAVE_CURL else ())
HTTP_EXC = (requests.exceptions.HTTPError,) + ((CurlHTTPError,) if HAVE_CURL else ())
CONN_EXC = (requests.exceptions.ConnectionError,) + ((CurlError,) if HAVE_CURL else ())


# FrequencyPair is a utility class to store a high / low frequency pair belonging to a specific OcuSync 3/4 frequency band.
# OcuSync uses very specific frequency bands which stick out like a sore thumb on the FCC databases. Nobody other than DJI
# and their authorized shell companies make hardware that uses these bands.
class FrequencyPair:
    def __init__(self, low, high):
        self.low = low
        self.high = high


frequency_pairs = [
    # OcuSync 3/4 (Mavic Mini 4, Mavic 3, etc...) 5 GHz high-frequency non-telemetry bands:
    FrequencyPair("5745.5", "5829.5"),
    # Finding Lito 1 / Voomax Breeze
    # 2402.0 - 2480.0 MHz
    FrequencyPair("2402.0", "2480.0"),
    # unrelated:
    FrequencyPair("5730.5", "5844.5"),
    # trying to hunt down Skyrover S1 (not OcuSync, rather WiFi Enhanced (Mini 4K types)):
    # Cogito Specta Mini: VERIFIED:
    FrequencyPair("2405.5", "2476.5"),
    FrequencyPair("5728.5", "5846.12"),
    # Testing
    FrequencyPair("5732.5", "5844.5"),
    FrequencyPair("5735.5", "5839.5"),
    FrequencyPair("2410.5", "2472.5"),
    # DJI Mini 5 Pro (SS3-MT5MFND25, granted 2025-05-21) exact bands, for hunting
    # the unreleased Skyrover V1 clone. The 5730.5-5844.4 wideband (~114 MHz span) is
    # the signature OcuSync fingerprint. NOTE: upper is 5844.4, not 5844.5 above, so
    # freq_exact_match needs this exact value to catch a clone that rounds the same.
    FrequencyPair("5730.5", "5844.4"),
    FrequencyPair("5745.0", "5825.0"),
    FrequencyPair("5157.0", "5245.0"),
    # DJI Lito X1 family. IMPORTANT: these .48-decimal bands are a SHELL
    # signature, NOT a DJI-direct one. The Lito X1 has no FCC grant under DJI's
    # own grantee code SS3 -- product_code DGP14 returns nothing, and no SS3
    # filing ever declares a .48 band (DJI's own drones use .0/.5/.4, e.g. the
    # Mini 5 Pro at 5730.5-5844.4). The platform reaches the US ONLY via shells:
    # VOOMAX TECHNOLOGY LIMITED (2BRY8, 2025-12-02) and Odyssey Robot LLC
    # (2BSYT, 2026-03/04), both Fikaxo-cluster, both certified by TUV Rheinland.
    # That uniform .48 offset is exactly what hid this family from the .5-tuned
    # sweep above -- but nothing legitimate uses .48, so it's the cleanest tell.
    # .48 widebands seen only on the RCs (108 / 105 MHz):
    FrequencyPair("5732.48", "5840.48"),
    FrequencyPair("5733.48", "5838.48"),
    # 95 MHz .48 wideband on BOTH the drone and the RC -- catches the aircraft
    # directly, not just the controller. Best single fingerprint for this family.
    FrequencyPair("5735.48", "5830.48"),
]

known_dji_entities = [
    "SZ DJI TECHNOLOGY CO., LTD".upper(),
    "SZ DJI Osmo Technology Co.,Ltd.".upper(),
    "Skycatch, Inc".upper(),  # thse guys are ok. https://www.dji.com/newsroom/news/skycatch-and-dji-announce-global-agreement-to-deliver-high-precision-custom-drones-for-komatsu
]


class ScrapingExceptionDueToTimeout(Exception):
    pass


class ScrapingExceptionDueToHTTPError(Exception):
    pass


# A requests-like session to scrape FCC data.
class ScrapingSession:
    def __init__(self):
        self.log = logging.getLogger("fcc-scraper")

        self.__base_url = (
            "https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm?calledFromFrame=N"
        )

        self.__caller_timeout = 20  # seconds

        if HAVE_CURL:
            # Impersonate Chrome's TLS stack and let curl_cffi own the browser
            # headers (User-Agent, Accept, sec-ch-ua, ...). Overriding them with a
            # random fake UA would break the fingerprint Akamai checks, so we only
            # add the form's provenance headers.
            self.session = curl_requests.Session(impersonate="chrome")
            self.headers = {
                "Origin": "https://apps.fcc.gov",
                "Referer": self.__base_url,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        else:
            # Fallback: plain requests with a random UA. Beware Akamai tarpitting.
            self.session = requests.Session()
            self.__ua_generator = UserAgent()
            self.headers = {
                "User-Agent": self.__ua_generator.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://apps.fcc.gov",
                "DNT": "1",
                "Connection": "keep-alive",
                "Referer": self.__base_url,
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "Priority": "u=0, i",
            }

        # The index of the frequency pair to use.
        # Index 13 = VooMax/Odyssey/Lito X1 95 MHz wideband 5735.48-5830.48 (drone+RC).
        self.__frequency_key = 13

        init_status_code = 0
        tries = 0
        # Hydrate session, put cookies in place.
        while init_status_code != 200 and tries <= 10:
            try:
                response = self.session.get(
                    self.__base_url, headers=self.headers, timeout=self.__caller_timeout
                )
                init_status_code = response.status_code
                if init_status_code == 200:
                    break
            except TIMEOUT_EXC + CONN_EXC:
                self.log.debug(">>> Initialization failed. Retrying...")
                time.sleep(1)
                tries += 1

            if init_status_code != 200:
                time.sleep(1)
                tries += 1

        if init_status_code != 200:
            if tries > 10:
                raise ScrapingExceptionDueToTimeout()
            else:
                raise ScrapingExceptionDueToHTTPError()

        self.log.debug(">>> Scraping session initialized.")
        self.log.debug(">>> FCC.gov response status code: " + str(response.status_code))
        self.log.debug(
            ">>> Using frequency pair: "
            + frequency_pairs[self.__frequency_key].low
            + " - "
            + frequency_pairs[self.__frequency_key].high
            + " MHz"
        )

    # get() returns an XML string.
    def get(self) -> str:
        params = {
            "RequestTimeout": "500",
        }

        data = {
            "grantee_code": "",
            "product_code": "",
            "applicant_name": "",
            "grant_date_from": "",
            "grant_date_to": "",
            "comments": "",
            "application_purpose": "O",
            "application_purpose_description": "Original Grant",
            "grant_code_1": "",
            "grant_code_2": "",
            "grant_code_3": "",
            "test_firm": "",
            "application_status": "",
            "application_status_description": "",
            "equipment_class": "",
            "equipment_class_description": "",
            "lower_frequency": frequency_pairs[self.__frequency_key].low,
            "upper_frequency": frequency_pairs[self.__frequency_key].high,
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
            "outputformat": "XML",
            "show_records": "10",
            "fetchfrom": "0",
            "calledFromFrame": "N",
        }

        try:
            response = self.session.post(
                "https://apps.fcc.gov/oetcf/eas/reports/GenericSearchResult.cfm",
                params=params,
                headers=self.headers,
                data=data,
                timeout=self.__caller_timeout,
            )
            response.raise_for_status()
        except TIMEOUT_EXC:
            raise ScrapingExceptionDueToTimeout()
        except HTTP_EXC + CONN_EXC:
            raise ScrapingExceptionDueToHTTPError()

        return response.text


def sanitize_fcc_xml(text: str) -> str:
    """The FCC's XML export leaves ampersands unescaped (e.g. 'CC&C Technologies',
    'Science&Technology Park', '17&18/F'), which makes a strict XML parser choke.
    Escape any '&' that isn't already the start of a valid entity."""
    return re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)


class Parser:
    @staticmethod
    def get_fcc_gov_url(fcc_id: str) -> str:
        return "https://gov.fccid.io/" + fcc_id

    def __init__(self, response):
        self.__readme_insert_line = 52  # Where to insert the table

        self.root = ET.fromstring(sanitize_fcc_xml(response))
        rows = []
        for row in self.root.findall("Row"):
            applicant_name = row.findtext("applicant_name")

            if applicant_name and applicant_name.upper() not in known_dji_entities:
                data = {
                    child.tag: child.text
                    for child in row
                    if child.tag in ["fcc_id", "applicant_name", "grant_date"]
                }
                data["fcc_gov_url"] = Parser.get_fcc_gov_url(data["fcc_id"].strip())

                rows.append(data)

        # No non-DJI devices on this band (either the FCC returned nothing, or every
        # hit was DJI itself and got filtered). Bail out before pandas chokes on an
        # empty frame; display()/write_to_readme() handle the None.
        self.parsed = None
        if not rows:
            return

        as_dataframe = pd.DataFrame(rows)

        as_dataframe["grant_date"] = pd.to_datetime(
            as_dataframe["grant_date"], format="%m/%d/%Y"
        )
        as_dataframe["grant_date"] = as_dataframe["grant_date"].dt.date

        df_unique_earliest = as_dataframe.drop_duplicates(
            subset=["fcc_id"], keep="first"
        )

        df_sorted = df_unique_earliest.sort_values(by="grant_date", ascending=False)
        self.parsed = df_sorted

    def has_results(self) -> bool:
        return self.parsed is not None and not self.parsed.empty

    def display(self) -> str:
        if not self.has_results():
            return "No non-DJI devices found for this frequency band."
        return tabulate(self.parsed, headers="keys", tablefmt="grid", showindex=False)

    def markdown(self) -> str:
        return self.parsed.to_markdown(index=False)

    @staticmethod
    def replace_line(file_name: str, line_num: int, text: str) -> None:
        lines = open(file_name, "r").readlines()
        lines = lines[0 : line_num + 1]
        lines[line_num] = text
        with open(file_name, "w") as out:
            out.writelines(lines)

    def write_to_readme(self) -> None:
        if not self.has_results():
            return
        Parser.replace_line("README.md", self.__readme_insert_line, self.markdown())


logging.basicConfig(level=logging.DEBUG)

print("::: scraping session...")
try:
    scraper = ScrapingSession()
except ScrapingExceptionDueToTimeout:
    print("XXX: starting scraping session timed out. Exiting...")
    sys.exit(1)


print("::: attempting to get data from FCC...")
try:
    data = scraper.get()
except ScrapingExceptionDueToTimeout:
    print("XXX: scraping session timed out.")
    sys.exit(1)
except ScrapingExceptionDueToHTTPError:
    print("XXX: scraping session received an HTTP error.")
    sys.exit(1)

print("::: parsing data...")
parser = Parser(data)
print(parser.display())
if parser.has_results():
    parser.write_to_readme()
else:
    print("::: no non-DJI matches; README left unchanged.")
