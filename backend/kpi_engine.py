
from pathlib import Path
import pandas as pd


def calculate_kpis():
    root = (
        Path(__file__).resolve().parent.parent
        / "uploads"
        / "project_library"
    )

    matches = list(root.rglob("viewos_weekly_zone_metrics.csv"))

    if not matches:
        return {"error": "ViewOS weekly metrics CSV not found"}

    path = matches[0]
    df = pd.read_csv(path)

    required = [
        "week_start",
        "camera_cohort",
        "camera_hours",
        "persons_observed",
        "ppe_compliant",
        "restricted_zone_breaches",
        "alerts_raised",
        "alerts_false_verified",
        "median_ack_minutes"
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        return {"error": f"Missing columns: {missing}"}

    # Convert date and numeric columns
    df["week_start"] = pd.to_datetime(
        df["week_start"], errors="coerce"
    )

    numeric_columns = [
        "camera_hours",
        "persons_observed",
        "ppe_compliant",
        "restricted_zone_breaches",
        "alerts_raised",
        "alerts_false_verified",
        "median_ack_minutes"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Keep pilot cohort only
    df = df[
        df["camera_cohort"].astype(str).str.strip().str.lower()
        == "pilot"
    ].copy()

    # Signed pilot acceptance period only
    df = df[
        (df["week_start"] >= pd.Timestamp("2026-05-11")) &
        (df["week_start"] <= pd.Timestamp("2026-07-03"))
    ].copy()

    df = df.sort_values("week_start")

    weeks = sorted(df["week_start"].dropna().unique())

    if len(weeks) < 6:
        return {
            "error": (
                f"Insufficient weekly pilot data: "
                f"found {len(weeks)} weeks in acceptance period."
            )
        }

    # Measurement windows
    baseline_weeks = weeks[:2]
    result_weeks = weeks[-4:]
    false_alarm_weeks = weeks[-2:]

    # Aggregate selected weeks
    def aggregate(selected_weeks):
        subset = df[
            df["week_start"].isin(selected_weeks)
        ].copy()

        persons = subset["persons_observed"].sum()
        compliant = subset["ppe_compliant"].sum()
        hours = subset["camera_hours"].sum()
        breaches = subset["restricted_zone_breaches"].sum()
        alerts = subset["alerts_raised"].sum()
        false_alerts = subset["alerts_false_verified"].sum()

        return {
            "weeks": [
                str(pd.Timestamp(w).date())
                for w in selected_weeks
            ],
            "rows": int(len(subset)),
            "persons_observed": int(persons),
            "ppe_compliant": int(compliant),

            "ppe_compliance_pct": round(
                compliant / persons * 100, 2
            ) if persons else None,

            "camera_hours": round(float(hours), 2),

            "restricted_breaches": int(breaches),

            "breaches_per_1000_camera_hours": round(
                breaches / hours * 1000, 2
            ) if hours else None,

            "alerts_raised": int(alerts),
            "false_verified_alerts": int(false_alerts),

            "false_alert_pct": round(
                false_alerts / alerts * 100, 2
            ) if alerts else None
        }

    # Calculate all three periods
    baseline = aggregate(baseline_weeks)
    final_period = aggregate(result_weeks)
    false_period = aggregate(false_alarm_weeks)

    # Calculate percentage reduction
    def reduction(old, new):
        if old is None or old == 0 or new is None:
            return None

        return round((old - new) / old * 100, 2)

    # Acknowledgement proxy: weighted average of zone-level medians
    ack_data = df[
        df["week_start"].isin(result_weeks)
    ].copy()

    total_alerts = ack_data["alerts_raised"].sum()

    ack_weighted = (
        (
            ack_data["median_ack_minutes"]
            * ack_data["alerts_raised"]
        ).sum() / total_alerts
    ) if total_alerts else None

    # Final report
    return {
        "source": path.name,

        "measurement_method": (
            "Aggregated pilot cohort rows from the ViewOS weekly export. "
            "Acceptance-period data is restricted to 11 May–3 July 2026. "
            "This calculated summary is not a replacement for the "
            "signed acceptance certificate."
        ),

        "baseline": baseline,
        "final_period": final_period,
        "false_alarm_period": false_period,

        "kpis": {
            "ppe_change_percentage_points": (
                round(
                    final_period["ppe_compliance_pct"]
                    - baseline["ppe_compliance_pct"],
                    2
                )
                if (
                    final_period["ppe_compliance_pct"] is not None
                    and baseline["ppe_compliance_pct"] is not None
                )
                else None
            ),

            "restricted_breach_reduction_pct": reduction(
                baseline["breaches_per_1000_camera_hours"],
                final_period["breaches_per_1000_camera_hours"]
            ),

            "false_alarm_pct": false_period["false_alert_pct"],

            "weighted_ack_minutes_proxy": (
                round(float(ack_weighted), 2)
                if ack_weighted is not None
                else None
            ),

            "ack_metric_warning": (
                "Weighted average of zone-level medians; "
                "not the exact overall median."
            )
        },

        "limitations": [
            "Compare calculated results with the signed acceptance certificate.",
            "Do not mix manual safety-walk baseline with camera-measured baseline.",
            "Do not claim causation from before/after differences alone.",
            "The outage may affect weekly results.",
            "The calculated acknowledgement proxy is not an exact median."
        ]
    }
