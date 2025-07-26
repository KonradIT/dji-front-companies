"""
This is the original script I wrote to scrape the FCCID.io, FAA and Justia websites to find 
DJI's shell companies and their associated frequencies.

I'm keeping it here for historical purposes.
"""
from bs4 import BeautifulSoup
import requests

browserstorage = {
	"fccid.io": {
		"headers": {
			
		}
	},
	"justia.com": {
		"cookies": {
			
		},

		"headers": {
			
		}
	},
	"faa.gov": {
		"cookies": {
		},

		"headers": {
			
		}
	}
}

def get_faa_remoteid(company_name):
	splitted = company_name.split(" ")

	company_name_clean = ""
	for part in splitted:
		if len(part) > 2:
			company_name_clean = part
			break

	response = requests.get(
		'https://uasdoc.faa.gov/api/v1/publicDOCRev?itemsPerPage=8&pageIndex=0&search=' + company_name_clean,
		cookies=browserstorage.get("faa.gov").get("cookies"),
		headers=browserstorage.get("faa.gov").get("headers")
	)

	got = response.json().get("data")

	if got.get("currentItemCount") == 0:
		return "N"
	else:
		return "Y"

def fccfreqs():
	"""
	Known DJI frequencies:
	- 5ghz OcuSync v2
	lower = "5745.5"
	upper = "5829.5"


	lower = "5730.5"
	upper = "5844.5"

	-
	"""
	lower = "5745.5"
	upper = "5829.5"

	known_dji_entities = [
		"SZ DJI TECHNOLOGY CO., LTD",
		"SZ DJI Osmo Technology Co.,Ltd."
	]

	response = requests.get(f"https://fccid.io/frequency.php?lower={lower}&upper={upper}&exact", cookies=browserstorage.get("fccid.io").get("cookies"), headers=browserstorage.get("fccid.io").get("headers"))
	html_content = response.text
	soup = BeautifulSoup(html_content, 'lxml')

	data = []

	for row in soup.select("table tr")[1:]:  # skipping the header row with [1:]
		cols = row.select("td")
		if len(cols) > 0 and (cols[0].contents[2].text.strip() not in known_dji_entities):
			data.append({
				"id": cols[0].find("a").text.strip(),
				"company": cols[0].contents[2].text.strip(),
				"date": cols[0].contents[5].text.strip(),
			})

	print("{:<20} {:<50} {:<15} {:<5}".format("FCC ID", "Company", "Date", "FAA RID"))
	for hit in data:
		print("{:<20} {:<50} {:<15} {:<5}".format(hit.get("id"), hit.get("company"), hit.get("date"), get_faa_remoteid(hit.get("company"))))

def trademarks():
	response = requests.get(
		'https://trademarks.justia.com/owners/cogito-tech-company-limited-5648351/',
		cookies=browserstorage.get("justia.com").get("cookies"),
		headers=browserstorage.get("justia.com").get("headers")
	)
	html_content = response.text
	soup = BeautifulSoup(html_content, 'lxml')
	h4_elements = soup.find_all('h4', class_='has-no-margin')
	data = []
	for h4 in h4_elements:
		# Find all <a> elements within the current <h4>
		a_elements = h4.find_all('a')

		# Extract the text from each <a> element and add it to the list
		for a in a_elements:
			data.append(a.text)

	print("Name")
	for hit in data:
		print(hit)

print("FCC search of known frequencies:")
fccfreqs()

print("Trademark search:")
trademarks()