FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

# Data dictionary

## viewos_weekly_zone_metrics.csv — ViewOS weekly export, 11 May to 27 Sep 2026

One row per week × zone × camera cohort. Weeks start on Monday.

| Column | Meaning |
| --- | --- |
| week_start | Monday of the week |
| zone | packing, conveyor, kiln, raw_mill, cement_mill, gate_yard, stores |
| camera_cohort | pilot = the 40 cameras live from 11 May; scale = cameras added from 6 Jul (column added 27 Jul, back-filled) |
| cameras_live | Cameras of that cohort live in that zone during the week |
| camera_hours | Hours of usable video processed (outages reduce this) |
| persons_observed | Tracked persons per camera per 10-minute window (one person on two cameras counts twice) |
| ppe_compliant | Of those, persons with both helmet and vest |
| restricted_zone_breaches | Entries into restricted or hot-zone polygons longer than 2 seconds |
| alerts_raised | Alerts sent to the control room and area in-charge |
| alerts_false_verified | Alerts marked false in the EHS daily sample review, scaled to the week |
| median_ack_minutes | Median minutes from alert to acknowledgement |
| model_version | Detector release running that week |

## baseline_manual_safety_walks_2025Q4.csv — EHS manual safety walks, Oct–Dec 2025
Two announced walks a day (10:00 and 15:00), one area per walk. People counted by the auditor.

## ehs_register_monthly_2025_2026.csv — monthly EHS MIS, Jan 2025 to Sep 2026
Lost-time injuries, first-aid cases, near-miss reports, man-hours worked (employees + contract labour).

## gate_truck_turnaround_daily.csv — 1 Jun to 30 Sep 2026
Until 2 Aug: handwritten gate register, averages computed by security office, rounded to 5 minutes; some days missing.
From 3 Aug: ViewOS gate analytics from number-plate cameras at gates in and out.

## invoices_and_payments.csv — PredCo invoices to Ardent
## supervisor_survey_sep2026.csv — 18 shift supervisors, paper survey run by EHS, 14–16 Sep 2026 (1 = low, 5 = high)
