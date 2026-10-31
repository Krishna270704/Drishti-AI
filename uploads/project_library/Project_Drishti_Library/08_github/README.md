FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

# ardent-drishti-edge

Site deployment of ViewOS for Ardent Cement Works, Bhadrapur ("Project Drishti").
Private repository: github.com/predco-delivery/ardent-drishti-edge

## What runs where

- 3 × edge GPU servers (10.20.4.11–13) in the Bhadrapur server room, OT VLAN 40
- `detector/` — person, helmet, hi-vis vest, face-shield models (YOLO-family, site-tuned)
- `zones/` — restricted-zone and hot-zone polygons per camera (`configs/zones_bhadrapur.yaml`)
- `alerts/` — alert bus, WhatsApp text gateway (text only, no images), control-room console at 10.20.4.15:8080
- `health/` — stream health monitor (added v1.4 after INC-0611)
- `gate/` — CR-03 gate turnaround: ANPR events G1–G4 joined with SAP weighbridge feed (via PredCo Data Core connector)

## Counting rules (agreed with EHS, 22 Apr 2026)

- A "person observed" is one tracked person in one camera within a 10-minute window. The same person seen by two cameras counts twice.
- Compliance = tracked persons with both helmet and vest detected in at least 70% of their frames.
- Restricted-zone breach = a tracked person whose feet point enters a zone polygon for more than 2 seconds.
- Persons in EHS hi-vis jackets with a white helmet on inspection rounds are not excluded (known issue, see #142).

## Deploy

Releases are signed packages installed by Ardent IT through the jump host. No outbound network access from edge servers.
