FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

# Business Requirements Document — Project Drishti

Version 2.0 (signed) | 5 Mar 2026 | Supersedes v1.0 (27 Feb 2026)
Client: Ardent Cement Works Ltd, Bhadrapur Unit | Vendor: PredCo
Project name chosen by client: "Drishti" (Hindi: sight)

## Change history

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 27 Feb | Draft from proposal PC/PROP/2026/019 |
| 2.0 | 5 Mar | KPI targets revised after EHS review: PPE target 95% → 90%; restricted zone −70% → −50%; response time 2 → 3 min; false alarms 5% → 10%. Baseline changed from manual safety walks to camera-measured weeks 1–2 (see §4). Face-recognition option retained as optional pending Legal. |

## 1. Objective

Raise real-world PPE compliance and cut restricted-zone entries at Bhadrapur before the group safety audit in October 2026,
using existing CCTV, with alerts that reach area in-charges fast enough to act.

## 2. Stakeholders

| Name | Role | Interest |
| --- | --- | --- |
| Rajiv Bhandari | Unit Head (sponsor, capex approver) | Audit rating, no LTIs, cost |
| Arvind Rao | Head EHS (business owner) | Compliance, contractor behaviour |
| Farhan Siddiqui | Head IT & OT Security | Network isolation, data handling |
| Lokesh Jain | Procurement | Terms, GRN |
| Shift in-charges (8) | Users | Alerts they can act on |

## 3. In scope (pilot)

40 cameras: packing plant 14, conveyor gallery 10, raw mill 8, and an area to be confirmed after PoC (8).
Detection classes: person, helmet, high-visibility vest, restricted-zone polygon entry.
Alerts: control room screen and WhatsApp to the area in-charge, with snapshot.
Reports: daily shift report; weekly compliance by area.

## 4. KPIs and how they are measured

The manual safety-walk score for Q4 2025 (EHS MIS: 73.8%, 882 people observed over 2 announced walks a day) is recorded for
reference only. It is not comparable with camera measurement: walks are announced, short, and cover one area at a time.

| ID | KPI | Definition | Baseline | Target | Window |
| --- | --- | --- | --- | --- | --- |
| K1 | PPE compliance | Persons observed wearing both helmet and vest ÷ persons observed, on pilot cameras | Camera-measured, pilot weeks 1–2 | ≥ 90% | Average of last 4 pilot weeks |
| K2 | Restricted-zone breaches | Breaches per 1,000 camera-hours, pilot cameras | Pilot weeks 1–2 | −50% | Last 4 pilot weeks |
| K3 | Alert acknowledgement | Median minutes from alert to acknowledgement by area in-charge | n/a | ≤ 3.0 min | Last 4 pilot weeks |
| K4 | False alarms | Share of alerts marked false in EHS daily sample review | n/a | < 10% | Last 2 pilot weeks |

## 5. Acceptance

The pilot is accepted if K1 and K4 are met. If K2 or K3 is missed, the vendor submits a remediation plan, and acceptance
may be granted with conditions by the Head EHS and Unit Head.

## 6. Constraints

On premise only; no internet egress; access via jump host; footage stays on site (MSA Annexure D).
Face recognition (R8) only after written clearance from Corporate Legal.

Signed: Rajiv Bhandari (Unit Head) · Arvind Rao (Head EHS) · Farhan Siddiqui (IT & OT) · Aarav Malhotra (PredCo)
