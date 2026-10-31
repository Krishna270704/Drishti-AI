FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

# Incident report INC-0611 — Loss of video streams on 22 pilot cameras

Prepared by: Vivek Anand (Field Engineer, PredCo), reviewed by Farhan Siddiqui (Ardent IT & OT) | 12 Jun 2026

## Summary

From 9 Jun 2026 18:40 to 11 Jun 2026 11:55 (about 41 hours), 22 of the 40 pilot cameras (packing 9, conveyor 7, raw mill 6)
sent no usable stream to the ViewOS edge servers. No safety alerts were raised for those cameras during that time.
The control room was not told until the morning of 10 Jun.

## Cause

The client's CCTV maintenance contractor applied a firmware update to NVR-2 and NVR-3 on 9 Jun evening. The update reset
RTSP sub-stream settings to a codec the edge decoder did not accept. The ViewOS software showed the cameras as "connected"
because the network link was up; it did not check that frames were actually arriving.

## Impact

- About 900 camera-hours with no detection (22 cameras × 41 hours).
- Median alert acknowledgement time rose that week, as in-charges were reassigned to manual rounds.
- No safety incident occurred during the gap.

## What we changed

1. Stream health monitor (release v1.4): alarms when a camera delivers no frames for 5 minutes, separate from network status.
2. Change-control rule agreed with Ardent IT: the CCTV contractor informs PredCo 24 hours before any NVR firmware change.
3. Daily 08:00 health message to the control room listing any camera offline.

## Responsibility

Root cause on the client's contractor side; detection gap on PredCo's side. Both parties accepted actions above.
