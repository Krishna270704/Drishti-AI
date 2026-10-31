FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

# Changelog — ardent-drishti-edge

## v2.0 — 2026-08-03
- Plant-wide: 146 camera configs; third edge server; load balancing across servers.
- CR-03 gate turnaround: ANPR ingest (G1–G4), weighbridge join, queue view, alerts at >25 trucks waiting or any truck >120 min.
- Pre-zone warning (2 m) for conveyor tail pulleys (acceptance condition for K2).

## v1.4 — 2026-07-20
- Stream health monitor: alarm if no frames for 5 minutes (INC-0611).
- Daily 08:00 camera health message to control room.
- Escalation hook: control-room call if alert not acknowledged in 5 minutes (enabled 4 Aug).

## v1.3 — 2026-06-15
- Retrained detector on 4,200 labelled site frames (on-premise training box).
- Fixes false vests from reflective strips on sack pallets; better helmets under dust at packer spouts.
- Kiln face-shield class precision still low in heat shimmer.

## v1.2 — 2026-06-02
- REMOVED face module (`attendance/`), its model files and the `face_attendance.enabled` key (CR-02). Not just disabled.

## v1.1 — 2026-05-25
- Kiln platform hot-zone rule with face-shield class (CR-01).

## v1.0 — 2026-05-11
- Pilot: 40 cameras, two edge servers, alerts to control room and WhatsApp (text only).

## v0.9 — 2026-03-19
- PoC: 12 cameras, helmet, vest, tail-pulley zone.
