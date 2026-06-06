# Odyssey Robot LLC — apparent FCC Covered-List evasion

> The following serves as a "memory" file for researching with Claude.

**Compiled:** 2026-06-05 · **Source:** FCC Equipment Authorization System (EAS), public exhibits

> **TL;DR** — Odyssey Robot LLC obtained FCC equipment authorizations (2026) for a
> drone + controller by certifying the equipment is **"not covered"** under the FCC
> Covered List and that it was **designed and manufactured in California**. The
> company's **own test report in the same filing** shows the device was tested in
> **Shenzhen, China**, and its **RF fingerprint is identical to the VooMax Breeze**
> (`2BRY8`) — built on the same OcuSync radio. The "not covered equipment" attestation
> therefore appears **materially false**, resting on a **provably false**
> US-manufacture declaration.

---

## 1. Subject

| Field | Value |
|---|---|
| Applicant | **Odyssey Robot LLC** |
| FCC grantee code | **2BSYT** |
| Drone | **2BSYT-FMAWZOD** ("Unmanned Aircraft"), granted **2026-03-24** |
| Controller | **2BSYT-YMAWZOD** ("Remote Controller"), granted **2026-04-20** |
| TCB (grants the cert) | TÜV Rheinland of North America, Inc., Pleasanton CA *(Form 731 grant "By:" field)* — note: **testing** was done by TÜV Rheinland **(Shenzhen)**, see §4 |
| Signer on all attestations | **Randolph Howard Eason**, "Compliance Director" |
| Contact | 21 Miller Alley Suite 210, Pasadena, CA 91103 · contact@flyondrone.com · +1 702-266-3242 |

Public mirrors: <https://fccid.io/2BSYT-FMAWZOD> · <https://fccid.io/2BSYT-YMAWZOD>

---

## 2. The Covered List context

On **2025-12-22** the FCC released **DA-25-1086** ("FCC Updates Covered List to Add
Certain UAS and UAS Components"), adding to the Covered List:

> *"UAS and UAS critical components produced in a foreign country"*

with **UAS critical components** defined to include *data-transmission devices,
communications systems, flight controllers, ground control stations and UAS
controllers, navigation systems, sensors and cameras, batteries and battery
management systems, and motors.*

- The listing is **category-based** — it does **not name DJI** (or any company) for UAS.
- Under **47 CFR § 2.903** + **§ 1.50002**, the FCC will **not grant** equipment
  authorization to covered equipment.
- The only lawful path for a foreign-made UAS is a **DoD/DHS** determination that it
  "does not pose unacceptable risks."

Sources: <https://www.fcc.gov/document/fcc-updates-covered-list-add-certain-uas-and-uas-components-0>
· <https://docs.fcc.gov/public/attachments/DA-25-1086A1.txt>
· The Verge, 2025-12-22: <https://www.theverge.com/news/849460/fcc-foreign-drone-ban-dji-congress-deadline>

---

## 3. The attestations (the statements at issue)

All dated **2026-01-12**, signed by Randolph Howard Eason. Verbatim:

**Not Covered Equipment Attestation** — drone exhibit id `9153467`, RC exhibit id `9224213` (§ 2.911(d)(5)(i)):

> "[Odyssey Robot LLC] ('the applicant') certifies that the equipment for which
> authorization is sought is not 'covered' equipment prohibited from receiving an
> equipment authorization pursuant to section § 2.903 of the FCC rules."

**Not Covered Entity Applicant Attestation** — drone exhibit id `9153466`, RC exhibit id `9224212` (§ 2.911(d)(5)(ii)):

> "[Odyssey Robot LLC] ('the applicant') certifies that, as of the date of the
> filing of the application, the applicant is not identified on the Covered List (as
> a specifically named entity or any of its subsidiaries or affiliates) as an entity
> producing 'covered' equipment."

**Declaration of "Produced in US"** — drone exhibit id `9153462` (dated **2026-02-06**), RC exhibit id `9224208`:

> "We, Odyssey Robot LLC, hereby declare that the product Unmanned Aircraft, with FCC
> ID 2BSYT-FMAWZOD, has been developed, designed, manufactured, and assembled by …
> Designed by: Odyssey Robot LLC (Pasadena, CA); Manufactured by: Odyssey Robot LLC
> (Pasadena, CA); Assembled by: **ETak Worldwide Corporation** (901 Avenue S., Suite
> A, Grand Prairie, TX); Developed by: Odyssey Robot LLC (Pasadena, CA)."

---

## 4. The contradiction inside Odyssey's own filing

The same application package contains its **test report**, exhibit id `9153518`
("CN26JC9X 002_2.4G SDR BLE 2.4G WIFI_DTS"):

- Drone: [fccid.io mirror](https://fccid.io/2BSYT-FMAWZOD/Test-Report/CN26JC9X-002-2-4G-SDR-BLE-2-4G-WIFI-DTS-9153518) another report from same lab:  [fccid.io mirror](https://fccid.io/2BSYT-FMAWZOD/RF-Exposure-Info/RF-Exposure-Info-9155315)
- RC: [fccid.io mirror](https://fccid.io/2BSYT-YMAWZOD/Test-Report/Test-Report-2-4G-DTS-9224249)

- **Tested by:** *TÜV Rheinland (Shenzhen) Co., Ltd.*, test facility at *No.2, Nuclear
  Power Industrial Park, Fuming Community, Fucheng Street, Longhua District, Shenzhen
  518000, People's Republic of China* (FCC Accreditation Designation No. 694916). *(This is
  the China test lab — a separate TÜV Rheinland entity from the US TCB that issued the grant,
  TÜV Rheinland of North America, §1. The grant was issued on Shenzhen-performed testing.)*
- **Report number `CN26JC9X`** — a China-lab designation.
- **EUT spec table:** *Kind of Equipment: Unmanned Aircraft · Type Designation:
  FMAWZOD · FCC ID: 2BSYT-FMAWZOD · supports Bluetooth, 2.4GHz Wi-Fi, 5.8GHz Wi-Fi,
  2.4GHz Band and 5.8GHz Band · Battery DC 7.3V.*

**A drone "designed and manufactured in California" is not shipped to Shenzhen for
its FCC compliance testing.** This contradiction is self-contained — it needs no
external evidence to impeach the "produced in US" declaration, and the "not covered
equipment" attestation rests on that declaration.

**The named US "assembler" is an electronics recycler.** The "produced in US"
declaration (§3) lists the drone as *"Assembled by: ETak Worldwide Corporation, 901
Avenue S, Suite A, Grand Prairie, TX."* But ETak Worldwide is an **R2-certified IT-asset-
disposition / e-waste recycling company** (founded 2020; on-site dismantling, asset
recovery, secure recycling of *end-of-life* electronics) — categorized publicly as a
"Computer & Electronics Recycling Company," with **no public evidence of any drone or UAS
manufacturing**. An e-waste *recycler* — whose business is taking electronics apart — being
the "assembler" of a brand-new DJI-class OcuSync drone is implausible on its face, and
reads as a US address-of-convenience to prop up the false origin claim. Even if ETak
performed final kitting/repackaging, that would not make a Shenzhen-built drone
"US-manufactured." *(Sources: ScrapMonster, CB Insights, D&B company listings;
ETak's own LinkedIn.)*

**How unusual is this?** Naming an e-waste recycler as a product's US "assembler" is very uncommon. **ETak Worldwide appears on no other FCC authorization** — the
fccid.io / fcc.report mirrors full-text-index exhibit PDFs, and ETak surfaces nowhere else
— and it is not an EMS / contract manufacturer of any kind. Genuine "produced in US"
declarations name real assemblers: an EMS house (Flex, Jabil, Benchmark, …) or the OEM's
own US plant — not an ITAD firm whose business is *taking electronics apart*. A new
OcuSync drone "assembled" by a Texas recycler that has never appeared on another filing
reads as an attempt to launder Chinese drones as US-manufactured. ETak's web presence is minimal, not only it doesn't appear on the FCC mirrors/FCC.gov website but it also doesn't appear to have clients stating they manufacture their products via ETak.

**The "California design/manufacture" address is a coworking space.** The declaration's
designer/manufacturer — *Odyssey Robot LLC, 21 Miller Alley, Suite 210, Pasadena, CA* — sits
at an **Industrious coworking / virtual-office** location. Suite 210 *is* the Industrious
floor; it sells a [~$99/month **virtual-office (mailbox)** plan](https://www.coworkingcafe.com/coworking-property/us/ca/pasadena/21-miller-alley/)
and hosts unrelated tenants (a labor-compliance consultancy, a speech coach). A drone
cannot be "designed and manufactured" at a shared coworking suite. The same filing also
pairs this *California* company with a **702 (Las Vegas) area-code phone**. *(Sources:
[Industrious — 21 Miller Alley Suite 210](https://www.industriousoffice.com/locations/21-miller-alley-suite-210)
· [CoworkingCafe pricing for 21 Miller Alley](https://www.coworkingcafe.com/coworking-property/us/ca/pasadena/21-miller-alley/).)*

**The antenna is Chinese-made — and identical to VooMax's supplier.** Odyssey's own
*Antenna Gain Info* exhibit (id `9162293`) names the antenna **Manufacturer: INPAQ
TECHNOLOGY (SUZHOU) CO., LTD.**, *Kexing Science Park, Nanshan District, Shenzhen, China*.

Here is the [document for antenna gain info](https://fccid.io/2BSYT-FMAWZOD/Test-Report/Antenna-Gain-Info-9162293)

The antenna is a UAS **critical component** (§2), so a Chinese-made antenna directly
undercuts "manufactured in California." The **VooMax** drone's Antenna Gain Info
(`2BRY8-FMAWZVM`, id `8836722`) names the **identical** manufacturer at the same Shenzhen
address — a shared Chinese supplier corroborating that the two are the same hardware (§5).

**Net:** every US role in the "produced in US" declaration is hollow — a coworking mailbox
(design/manufacture) and an e-waste recycler (assembly) — while the device was **tested in
Shenzhen** and even its **antenna is Chinese-made** (INPAQ, Shenzhen). The declaration, and
the "not covered" attestation that rests on it, are false.

---

## 5. OcuSync hardware lineage (technical)

Odyssey's drone shares the **VooMax Breeze's exact OcuSync radio** (`2BRY8`, VOOMAX
TECHNOLOGY LIMITED) — established from FCC data alone:

- **Identical RF fingerprint = same radio module** — both declare the same OcuSync
  `.48`-decimal widebands (`5732.48–5840.48`, `5733.48–5838.48`, `5735.48–5830.48`) and the
  same `.48` 2.4 GHz bands. Those exact, unusual edges
  imply the **same OcuSync transceiver/firmware** — not merely a similar drone.
- **Paired product-code grammar** — `FMAWZOD`/`YMAWZOD` (Odyssey) vs `FMAWZVM`/`YMAWZVM`
  (VooMax): matching drone/RC codes from a common origin.
- **Same antenna supplier** — both Antenna Gain Info exhibits name the identical Chinese
  antenna maker, **INPAQ Technology (Suzhou) Co., Ltd.** (Nanshan District, Shenzhen) — see §4.
- **OcuSync = DJI** — those `.48` widebands are OcuSync, DJI's proprietary drone
  protocol; no non-DJI hardware is known to declare them. DJI's own grantee (SS3) uses
  round/`.5`/`.4` edges (e.g. Mini 5 Pro `5730.5–5844.4`) and **never `.48`**; DJI did
  file OcuSync drones (Lito X1 `SS3-DGP14`, granted 2025-12-11, and Lito 1 `SS3-DGN12`)
  under its own name, both later **delisted** (see §6).

**Same radio, different airframes — a family of variants, not 1:1 clones.** The shells are
*not* exact copies of one DJI model; they ride the same OcuSync platform but differ in
camera, LiDAR, battery and flight time:

| Drone | Filer | Sensor | Reported Flight Time | LiDAR |
|---|---|---|---|---|
| DJI Lito 1 (`SS3-DGN12`) | DJI | 1/2″ | ~36 min | No |
| DJI Lito X1 (`SS3-DGP14`) | DJI | 1/1.3″ | ~36 min | No |
| VooMax Breeze 8K (`2BRY8`) | shell | 1/1.32″ | 30 min | **Yes** |
| Skyrover S1 (`2BPFE`, WaveGo) | shell | 1/2″ | — | **Yes** |
| **Odyssey / Galiview Pro (`2BSYT`)** | shell | **1/2.3″** | **~25 min** | **No** |

So Odyssey's drone (retailed as **Galiview Pro**) matches **none** of the others exactly:
the smallest sensor (1/2.3″), the shortest flight (~25 min), and **no LiDAR** (like the DJI
Litos, unlike VooMax/Skyrover). It is its own variant on the shared DJI OcuSync radio — a
sibling, not a 1:1 copy of any single model.

> Note: no *public* FCC document prints the word "DJI." The DJI attribution rests on (a)
> the OcuSync `.48` RF fingerprint, (b) the FCC-verified shared OcuSync radio with VooMax,
> and (c) the Shenzhen test origin — strong and technical, but circumstantial on the public
> record.

---

## 6. The DJI source filings — and the laundering timeline

DJI filed both Lito models under its own grantee code (SS3) in **December 2025** (Lito X1
`SS3-DGP14` granted **2025-12-11**). After the Dec 2025 Covered-List action they were
**delisted from FCC search** — the grant records are now scrubbed (no date or notes
survive in the grant form), though the exhibits remain reachable by direct
`application_id` URL:

| | DJI Lito X1 | DJI Lito 1 |
|---|---|---|
| FCC ID | `SS3-DGP14` | `SS3-DGN12` |
| Internal models | DGP14C / DGP14D | DGN12C / DGN12D |
| Grant date | 2025-12-11 | (pulled; not in public record) |
| FCC search status | **delisted (pulled)** | **delisted (pulled)** |
| 2.4 GHz | 2400–2483 | 2400–2483 |
| 5 GHz | 5150–5250, 5725–5850 | 5150–5250, 5725–5850 |
| Exhibits `application_id` | `loKflqNyoqaPmd0HYadaWw==` | `dh2YkDBdTZ21Cdrr9w7PQA==` |

**Timeline**

1. **2025-12-02** — VooMax shell (`2BRY8`) granted — an OcuSync drone (9 days *before*
   DJI's own filing below).
2. **2025-12-11** — DJI's own **Lito X1** (`SS3-DGP14`) granted under grantee SS3.
3. **2025-12-22** — FCC adds foreign-made UAS to the Covered List (DA-25-1086).
4. **(after)** — DJI's Lito grant is **delisted/pulled** from FCC search.
5. **2026-03/04** — Odyssey shell (`2BSYT`) granted **post-ban** with the false "not
   covered" + "produced in US" attestations (§3–4) — entering a market DJI's own
   (delisted) filing no longer could.

**Frequency comparison — and an honest limit.** DJI's Lito and the shells operate in
the **same nominal bands** (2400–2483, 5150–5250, 5725–5850). The `.48` edges that evade
exact-frequency watchdogs appear in the **shell EAS records** (tested 2025–26 by TÜV
Rheinland Shenzhen), not in DJI's readable reports (which state round edges).

> **Conclusion:** deliberate RF-frequency modification is **not proven** — the `.48` is
> most consistent with measurement/lab variance, not a spectrum spoof. The evasion is at
> the **filing/entity level**, not the frequency level. *Operational takeaway:*
> exact-frequency matching is fragile to this variance — use **tolerance matching**
> (`tolerance_scan.py`) so `.48`-type drift is caught automatically.

**Model mapping (unresolved on the public record).** VooMax and Odyssey share the same
OcuSync radio (identical `.48` bands, §5) but are **different drone models** at retail
(different camera/LiDAR/flight — see §5 table). FCC frequency data also **cannot** pin
either to a specific DJI model: Lito X1 (`DGP14`) and Lito 1 (`DGN12`) declare **identical**
nominal bands (2400–2483 / 5150–5250 / 5725–5850).

VooMax Breeze 8K [is made in China](https://fccid.io/2BRY8-FMAWZVM/Label/ID-Label-and-Location-8836922)

Critically, the labels for both the [Odyssey / Galiview drone](https://fccid.io/2BSYT-FMAWZOD/Label/ID-Label-and-Location-9155307) and [Remote Controller](https://fccid.io/2BSYT-YMAWZOD/Label/ID-Label-and-Location-9224307) lack the "Made in (country)" text.

---

## 7. Galiview

**Odyssey Robot LLC** is the registered owner of:

| Trademark | Serial(s) | Filed | Goods |
|---|---|---|---|
| GALIVIEW | 99505077, 99632451, 99633298, 99634050 | 2025-11-19 → 2026-02-04 | cameras |
| GALIVIEW VENUS | 99633886 | 2026-02-04 | (Galiview line) |
| GALIVIEW TITAN | 99633939 | 2026-02-04 | "Drones; Delivery drones; Civilian drones; Photography drones" |
| GALIVIEW NOVA | 99633961, 99634002, 99634029 | 2026-02-04 | (Galiview line) |
| FLYON | 99457648 | 2025-10-22 | → `flyondrone.com` (Odyssey's FCC contact domain) |

So **galiviewtech.com → Galiview = Odyssey Robot LLC = FCC grantee `2BSYT`**, and the
`FLYON` mark maps to the `contact@flyondrone.com` address on the attestations (§3).

**Spec / band match.** The galiviewtech.com "Galiview Pro" drone is unmistakably DJI-class
and its radios match Odyssey's FCC grant:

| | Galiview Pro (retail) | Odyssey FCC `2BSYT` |
|---|---|---|
| Radio | 2.4 GHz + **5.725–5.850 GHz** | 2.4 GHz + 5.8 GHz OcuSync (`.48` bands within 5725–5850) |
| Weight | 249 g | sub-250 g |
| Gimbal | 3-axis mechanical | — |
| Obstacle avoid. | 4-directional vision + infrared | — |
| Transmission | 10 km CE / 6 km FCC | — |
| Battery | 3850 mAh | (confidential) |

A 3-axis mechanical gimbal + multi-directional vision/IR sensing + 5.725–5.850 GHz + DJI's
dual CE/FCC transmission format is a **DJI OcuSync signature** (no-name drones don't ship
it). Galiview Pro is a **mid model** (1/2.3″ sensor, 25 min, no LiDAR) — *not* the higher
VooMax "Breeze 8K" spec — consistent with Galiview being a multi-model line (Pro / VENUS /
TITAN / NOVA); the FCC-filed `2BSYT-FMAWZOD` is one model within it.

Source: USPTO via <https://uspto.report/company/Odyssey-Robot-L-L-C>.

---

## 8. Analysis

**Q: Is the "not covered equipment" attestation false?**
Yes — it appears **materially false**. As of 2025-12-22, a foreign-produced UAS is
covered equipment. The device is a foreign-made (Shenzhen-tested, Chinese-componented,
OcuSync) drone built on the same OcuSync radio as the VooMax Breeze. The 2026-01-12 certification
that it is "not covered" stands on the 2026-02-06 US-manufacture declaration, which the
company's own Shenzhen test report contradicts.

(The companion *Entity* attestation is more defensible: the UAS listing names no
companies, so "Odyssey is not a named entity" is literally true. The shell structure
appears designed to exploit exactly that gap.)

**Q: How does the Covered List affect Odyssey?**
- § 2.903 / § 1.50002 bar authorizing covered equipment; the grants (2026-03-24 /
  2026-04-20) appear to have issued only because the TCB relied on these attestations.
- Potential exposure: **47 CFR § 1.17** (false/misleading statements to the FCC),
  **§ 2.903** (prohibited authorization of covered equipment), **18 U.S.C. § 1001**
  (false statements to a federal agency — criminal).
- The FCC has asserted **retroactive authority to revoke** authorizations for covered
  drones, so these grants are revocable.

---

## 9. Leads for follow-up

- **Odyssey contacts:** `contact@flyondrone.com` (domain `flyondrone.com`); signer
  **Randolph Howard Eason**, "Compliance Director," 21 Miller Alley Suite 210, Pasadena CA.
- **VooMax contacts:** **Yao Ma** · `jack@voomaxtech.com`; US Agent for Service
  **Benjamin Smith, VP — JOC Inc** (`sales@jocinc.org`).
- **ETak Worldwide Corporation**, Grand Prairie TX — Odyssey's claimed drone "assembler,"
  but actually an **R2-certified e-waste recycler / ITAD firm** (see §4). Worth probing the
  relationship: is ETak a knowing front, or just a US address on the paperwork?
- **US Agent for Service of Process** is the one cross-shell link FCC data *can* expose:
  Odyssey's agent attestation is exhibit id `9153478`, VooMax's is `8833814` (JOC Inc).
  Checking whether one US agent recurs across grantees is the strongest provable linkage.


---

## 10. How to reproduce

1. FCC EAS search by grantee code `2BSYT` (or applicant "Odyssey Robot") →
   `https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm`.
2. Open each FCC ID's **Exhibits** list (`ViewExhibitReport.cfm?mode=Exhibits`).
3. Attachments are at `https://apps.fcc.gov/eas/GetApplicationAttachment.html?id=<ID>`
   (must be reached via the exhibit page / referer), or mirrored on fccid.io / fcc.report.

| Document | Drone (FMAWZOD) | RC (YMAWZOD) |
|---|---|---|
| Not Covered Entity Attestation | 9153466 | 9224212 |
| Not Covered Equipment Attestation | 9153467 | 9224213 |
| Declaration "Produced in US" | 9153462 | 9224208 |
| Test report (CN26JC9X 002) | 9153518 | 9224249 |
| ID Label and Location | 9153464 | 9224210 |
| Attestation of US Agent | 9153478 | 9224205 |

---

## 11. Caveats

- "Materially false" reflects the documentary record; intent/"lying" is a legal
  determination for the FCC/DOJ, not established here.
- The DJI attribution is technical inference (OcuSync RF fingerprint + FCC-verified
  shared OcuSync radio with VooMax + Shenzhen test origin); no public document names DJI.
- **No specific DJI model is asserted.** FCC data confirms VooMax and Odyssey share the
  same OcuSync radio (identical `.48` bands), but they are **different drone models** at
  retail (camera/LiDAR/flight differ, §5); FCC data also cannot distinguish DJI Lito X1
  from Lito 1 (identical nominal bands).
- **Registered-agent addresses are not links.** Odyssey's Delaware addresses —
  *3422 Old Capitol Trail Ste 700* (**Delaware Business Incorporators, Inc.**) and
  *1209 Orange St* (**Corporation Trust Center**) — are generic registered-agent /
  virtual-office services shared by thousands of unrelated entities (Paxful, etc.), so the
  overlap with Xtra Technology LLC's address is **not** a tie. The `702` phone is a VoIP
  number with no web footprint, and **no Nevada registration exists** — Odyssey is a
  Delaware LLC. (Treat any registered-agent/address overlap as noise, like `1209 Orange St`.)
