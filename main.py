import requests
import xml.etree.ElementTree as ET
import pandas as pd
import sys
from tabulate import tabulate
import logging

from fake_useragent import UserAgent

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
    FrequencyPair("5730.5", "5844.5"),

    # trying to hunt down Skyrover S1 (not OcuSync, rather WiFi Enhanced (Mini 4K types)):
    
    # Cogito Specta Mini: VERIFIED:
    FrequencyPair("2405.5", "2476.5"),
    FrequencyPair("5728.5", "5846.12"),

    # Testing
    FrequencyPair("5732.5", "5844.5"),
    FrequencyPair("5735.5", "5839.5"),
    FrequencyPair("2410.5", "2472.5")
]

known_dji_entities = [
    "SZ DJI TECHNOLOGY CO., LTD".upper(),
    "SZ DJI Osmo Technology Co.,Ltd.".upper(),
    "Skycatch, Inc".upper() # thse guys are ok. https://www.dji.com/newsroom/news/skycatch-and-dji-announce-global-agreement-to-deliver-high-precision-custom-drones-for-komatsu
]

class ScrapingExceptionDueToTimeout(Exception):
    pass

class ScrapingExceptionDueToHTTPError(Exception):
    pass

# A requests-like session to scrape FCC data.
class ScrapingSession:
    def __init__(self): 
        self.session = requests.Session()

        self.log = logging.getLogger("fcc-scraper")

        self.__base_url = "https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm?calledFromFrame=N"

        self.__ua_generator = UserAgent()
        
        # Shared headers for all requests.
        self.headers = {
            "User-Agent": self.__ua_generator.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            # "Accept-Encoding": "gzip, deflate, br, zstd",
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
        # Using 0 for now.
        self.__frequency_key = 0

        # Hydrate session, put cookies in place.
        response = self.session.get(self.__base_url, headers=self.headers, timeout=10)
        self.log.debug(">>> Scraping session initialized.")
        self.log.debug(">>> FCC.gov response status code: " + str(response.status_code))
        self.log.debug(">>> Using frequency pair: " + frequency_pairs[self.__frequency_key].low + " - " + frequency_pairs[self.__frequency_key].high + " MHz")

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


        response = self.session.post(
            "https://apps.fcc.gov/oetcf/eas/reports/GenericSearchResult.cfm",
            params=params,
            headers=self.headers,
            data=data,
            timeout=10
        )
        try:
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise ScrapingExceptionDueToTimeout()
        except requests.exceptions.HTTPError:
            raise ScrapingExceptionDueToHTTPError()

        return response.text

class Parser:
    @staticmethod
    def get_fcc_gov_url(fcc_id: str) -> str:
        return "https://gov.fccid.io/" + fcc_id

    def __init__(self, response):
        self.__readme_insert_line = 52 # Where to insert the table

        self.root = ET.fromstring(response)
        rows = []
        for row in self.root.findall("Row"):
            applicant_name = row.findtext("applicant_name")

            if applicant_name.upper() not in known_dji_entities:
                data = {child.tag: child.text for child in row if child.tag in ["fcc_id","applicant_name", "grant_date"]}
                data["fcc_gov_url"] = Parser.get_fcc_gov_url(data["fcc_id"].strip())

                rows.append(data)

        as_dataframe = pd.DataFrame(rows)

        as_dataframe["grant_date"] = pd.to_datetime(as_dataframe["grant_date"], format="%m/%d/%Y")
        as_dataframe["grant_date"] = as_dataframe["grant_date"].dt.date

        df_unique_earliest = as_dataframe.drop_duplicates(subset=["fcc_id"], keep="first")

        df_sorted = df_unique_earliest.sort_values(by="grant_date", ascending=False)
        self.parsed = df_sorted

    def display(self) -> str:
        return tabulate(self.parsed, headers="keys", tablefmt="grid", showindex=False)

    def markdown(self) -> str:
        return self.parsed.to_markdown(index=False)

    @staticmethod
    def replace_line(file_name: str, line_num: int, text: str) -> None:
        lines = open(file_name, "r").readlines()
        lines = lines[0:line_num+1]
        lines[line_num] = text
        with open(file_name, "w") as out:
            out.writelines(lines)

    def write_to_readme(self) -> None:
        Parser.replace_line(
            "README.md",
            self.__readme_insert_line,
            self.markdown()
        )

logging.basicConfig(level=logging.DEBUG)

print("::: scraping session...")
scraper = ScrapingSession()
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
parser.write_to_readme()