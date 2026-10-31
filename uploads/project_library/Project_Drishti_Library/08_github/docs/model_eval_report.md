FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

# Detector evaluation — site test set

Test set: 1,250 frames from Bhadrapur cameras, labelled by PredCo annotators and spot-checked by EHS (10%). Frames from
day and night shifts, all pilot areas. Same test set for every version (kiln frames added in v1.1).

| Class | v0.9 precision / recall | v1.1 | v1.3 | v2.0 |
| --- | --- | --- | --- | --- |
| Person | 0.94 / 0.91 | 0.94 / 0.92 | 0.96 / 0.94 | 0.96 / 0.95 |
| Helmet | 0.86 / 0.80 | 0.87 / 0.81 | 0.94 / 0.90 | 0.95 / 0.91 |
| Hi-vis vest | 0.78 / 0.88 | 0.79 / 0.88 | 0.93 / 0.89 | 0.94 / 0.90 |
| Face shield (kiln) | — | 0.71 / 0.64 | 0.80 / 0.73 | 0.82 / 0.75 |

Notes:
- v0.9 vest precision was low because reflective strips on sack pallets were detected as vests.
- Night frames: helmet recall is about 6 points lower than day across all versions.
- Gate-yard cameras (added v2.0) are not in this test set; resolution is lower (704×576), and drivers' helmets are often missing entirely.
- Metric is per frame. Compliance in reports is per tracked person per camera per 10 minutes (see README), so these numbers do not convert directly into compliance accuracy.
