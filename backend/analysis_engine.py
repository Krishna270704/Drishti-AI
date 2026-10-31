
import re
import json
from pathlib import Path
from datetime import datetime

import pandas as pd


SUPPORTED_DATE = re.compile(r"20\d{2}[-_]\d{2}[-_]\d{2}")

PRIVACY_TERMS = [
    "confidential",
    "client name",
    "plant name",
    "employee name",
    "face recognition",
    "facial recognition",
    "biometric",
    "camera location",
    "signboard",
    "uniform",
    "personal data",
    "nda",
    "non-disclosure"
]

IMPORTANT_TERMS = [
    "scope", "baseline", "target", "acceptance",
    "incident", "change request", "delay",
    "payment", "approval", "delivered",
    "false alarm", "acknowledgement",
    "turnaround", "ppe", "restricted-zone"
]


def get_library_path():
    return Path(__file__).resolve().parent.parent / "uploads" / "project_library"


def read_text_file(path):
    try:
        suffix = path.suffix.lower()

        if suffix in [".txt", ".md"]:
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".pdf":
            import pymupdf
            doc = pymupdf.open(path)
            return "\n".join(page.get_text() for page in doc)

        if suffix == ".docx":
            from docx import Document
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs)

    except Exception as error:
        return f"READ ERROR: {error}"

    return ""


def build_timeline():
    root = get_library_path()
    events = []

    if not root.exists():
        return events

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        match = SUPPORTED_DATE.search(path.name)

        if not match:
            continue

        date_text = match.group(0).replace("_", "-")

        try:
            date = datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            continue

        events.append({
            "date": date.strftime("%Y-%m-%d"),
            "event": path.stem.replace("_", " "),
            "source": str(path.relative_to(root)),
            "status": "DATE FROM FILENAME"
        })

    events.sort(key=lambda x: x["date"])
    return events


def analyze_csv_files():
    root = get_library_path()
    results = []

    if not root.exists():
        return results

    for path in root.rglob("*.csv"):
        try:
            df = pd.read_csv(path)

            numeric = df.select_dtypes(include="number")

            summary = {
                "filename": str(path.relative_to(root)),
                "rows": int(len(df)),
                "columns": list(df.columns),
                "missing_values": int(df.isna().sum().sum()),
                "numeric_summary": {}
            }

            for column in numeric.columns:
                summary["numeric_summary"][column] = {
                    "mean": round(float(numeric[column].mean()), 3)
                    if numeric[column].notna().any() else None,
                    "min": round(float(numeric[column].min()), 3)
                    if numeric[column].notna().any() else None,
                    "max": round(float(numeric[column].max()), 3)
                    if numeric[column].notna().any() else None
                }

            results.append(summary)

        except Exception as error:
            results.append({
                "filename": path.name,
                "error": str(error)
            })

    return results


def analyze_privacy():
    root = get_library_path()
    risks = []

    if not root.exists():
        return risks

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in [".txt", ".md", ".pdf", ".docx"]:
            continue

        content = read_text_file(path).lower()

        if not content:
            continue

        for term in PRIVACY_TERMS:
            if term in content:
                risks.append({
                    "source": str(path.relative_to(root)),
                    "matched_term": term,
                    "risk": "REVIEW REQUIRED",
                    "recommendation": (
                        "Check contract permissions and remove or "
                        "anonymize identifying information before use."
                    )
                })

    return risks


def build_evidence_index():
    root = get_library_path()
    evidence = []

    if not root.exists():
        return evidence

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in [".txt", ".md", ".pdf", ".docx"]:
            continue

        content = read_text_file(path)

        if not content or content.startswith("READ ERROR"):
            continue

        matched = [
            term for term in IMPORTANT_TERMS
            if term in content.lower()
        ]

        if matched:
            evidence.append({
                "source": str(path.relative_to(root)),
                "matched_topics": matched,
                "preview": content[:1200]
            })

    return evidence


def generate_case_studies(evidence):
    sources = [item["source"] for item in evidence]

    return {
        "gatekeeper": {
            "audience": "Procurement, IT Security, Legal and Compliance",
            "headline": "A controlled AI safety analytics pilot",
            "focus": [
                "Contractual permissions",
                "Data privacy and security",
                "System limitations",
                "Incident handling",
                "Evidence and approval"
            ],
            "evidence_sources": sources,
            "status": "DRAFT - HUMAN REVIEW REQUIRED"
        },
        "user": {
            "audience": "Plant managers, engineers and operators",
            "headline": "Supporting safer and more visible operations",
            "focus": [
                "Operational workflow",
                "Safety monitoring",
                "Alert acknowledgement",
                "User feedback",
                "Adoption and limitations"
            ],
            "evidence_sources": sources,
            "status": "DRAFT - HUMAN REVIEW REQUIRED"
        },
        "buyer": {
            "audience": "CXOs and business decision makers",
            "headline": "Evaluating the business value of AI-enabled safety analytics",
            "focus": [
                "Measured outcomes",
                "Investment and costs",
                "Operational efficiency",
                "ROI evidence",
                "Scalability"
            ],
            "evidence_sources": sources,
            "status": "DRAFT - HUMAN REVIEW REQUIRED"
        }
    }


def run_analysis():
    root = get_library_path()

    if not root.exists():
        return {"error": "Project library not found. Upload a ZIP first."}

    timeline = build_timeline()
    csv_analysis = analyze_csv_files()
    privacy = analyze_privacy()
    evidence = build_evidence_index()
    case_studies = generate_case_studies(evidence)

    result = {
        "project": "Project Drishti",
        "analysis_timestamp": datetime.now().isoformat(),
        "timeline": timeline,
        "csv_analysis": csv_analysis,
        "privacy_risks": privacy,
        "evidence_index": evidence,
        "case_studies": case_studies,
        "publication_status": "BLOCKED - APPROVAL REQUIRED",
        "disclaimer": (
            "CSV summaries are descriptive statistics, not validated KPIs. "
            "Timeline dates are taken from filenames. All case studies "
            "require source-level verification and human review."
        )
    }

    output = Path(__file__).resolve().parent.parent / "outputs"
    output.mkdir(exist_ok=True)

    (output / "analysis_report.json").write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8"
    )

    return result
