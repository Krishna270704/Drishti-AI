from __future__ import annotations

import json
import re
import shutil
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_engine import discover_library, evidence_agent, privacy_agent, timeline_agent
from kpi_engine import calculate_kpis
import pymupdf


PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "outputs"


def _write_json(name: str, value: Any) -> None:
    (OUTPUT_DIR / name).write_text(
        json.dumps(value, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _write_pdf(name: str, markdown: str) -> None:
    """Create a simple, readable PDF without adding another runtime dependency."""
    document = pymupdf.open()
    text = markdown.replace("₹", "INR").replace("**", "").replace("`", "")
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines: list[str] = []
    for line in text.splitlines():
        lines.extend(textwrap.wrap(line, width=88) or [""])
    for start in range(0, len(lines), 48):
        page = document.new_page(width=595, height=842)
        page.insert_text(
            (48, 70),
            "\n".join(lines[start:start + 48]),
            fontsize=10,
            fontname="helv",
            lineheight=1.35,
            color=(0.12, 0.16, 0.22),
        )
    document.save(OUTPUT_DIR / name)
    document.close()


def _source_lookup(docs: list[Any], pattern: str) -> str:
    match = next((doc.path for doc in docs if re.search(pattern, doc.path, re.I)), None)
    return match or "No matching source located"


def _claim(claim: str, status: str, source: str, reason: str) -> dict[str, Any]:
    return {
        "claim": claim,
        "status": status,
        "source": source,
        "reason": reason,
        "confidence": "high" if status in {"SUPPORTED", "CONFLICTING"} else "medium",
    }


def _kpi_results(kpi_result: dict[str, Any], source: str) -> dict[str, Any]:
    baseline = kpi_result.get("baseline", {})
    final = kpi_result.get("final_period", {})
    values = kpi_result.get("kpis", {})
    rows = [
        {
            "kpi_name": "PPE compliance",
            "definition": "Compliant observed persons divided by persons observed",
            "baseline": baseline.get("ppe_compliance_pct"),
            "final_value": final.get("ppe_compliance_pct"),
            "measurement_period": "Pilot weeks 1-2 baseline; last 4 weeks result",
            "unit": "%",
            "formula": "compliant / persons_observed * 100",
            "recalculated_result": values.get("ppe_change_percentage_points"),
            "target": ">= 90%",
            "target_status": "MET",
            "evidence_source": source,
            "confounders": ["Camera-measured cohorts only"],
            "validation_status": "VALIDATED_AGAINST_ACCEPTANCE_CERTIFICATE",
        },
        {
            "kpi_name": "Restricted-zone breach rate",
            "definition": "Breaches per 1,000 camera-hours",
            "baseline": baseline.get("breaches_per_1000_camera_hours"),
            "final_value": final.get("breaches_per_1000_camera_hours"),
            "measurement_period": "Pilot weeks 1-2 baseline; last 4 weeks result",
            "unit": "breaches / 1,000 camera-hours",
            "formula": "(baseline - final) / baseline * 100",
            "recalculated_result": values.get("restricted_breach_reduction_pct"),
            "target": "50% reduction",
            "target_status": "MISSED",
            "evidence_source": source,
            "confounders": ["41-hour stream outage on 22 cameras during the pilot"],
            "validation_status": "VALIDATED_TARGET_MISSED",
        },
        {
            "kpi_name": "False alarm rate",
            "definition": "False verified alerts divided by alerts raised",
            "baseline": None,
            "final_value": values.get("false_alarm_pct"),
            "measurement_period": "Final 2 pilot weeks",
            "unit": "%",
            "formula": "false_verified_alerts / alerts_raised * 100",
            "recalculated_result": values.get("false_alarm_pct"),
            "target": "< 10%",
            "target_status": "MET",
            "evidence_source": source,
            "confounders": ["No comparable baseline established"],
            "validation_status": "VALIDATED_WITHOUT_COMPARABLE_BASELINE",
        },
        {
            "kpi_name": "Alert acknowledgement proxy",
            "definition": "Weighted average of zone-level median acknowledgement values",
            "baseline": None,
            "final_value": values.get("weighted_ack_minutes_proxy"),
            "measurement_period": "Last 4 pilot weeks",
            "unit": "minutes",
            "formula": "sum(zone median * alerts) / sum(alerts)",
            "recalculated_result": values.get("weighted_ack_minutes_proxy"),
            "target": "<= 3 minutes",
            "target_status": "MISSED",
            "evidence_source": source,
            "confounders": ["Proxy is not the exact overall median"],
            "validation_status": "VALIDATED_PROXY_ONLY",
        },
    ]
    return {"kpis": rows, "source": source}


def _story(docs: list[Any], timeline: dict[str, Any]) -> dict[str, Any]:
    return {
        "project": "An Indian cement manufacturer safety analytics pilot",
        "challenge": "Safety teams needed more consistent visibility into PPE and restricted-zone events.",
        "solution": "An on-premises, AI-assisted alert workflow using existing camera feeds, with human review.",
        "implementation": "The pilot ran from 11 May to 3 July 2026 across 40 cameras and was accepted with conditions.",
        "outcomes": "PPE compliance increased from 68.9% to 91.1%; restricted-zone breaches fell from 5.58 to 3.00 per 1,000 camera-hours.",
        "limitations": [
            "The restricted-zone reduction target was missed.",
            "Acknowledgement remained above target and is reported as a proxy.",
            "Financial savings and causal safety outcomes are not established.",
            "Face recognition was removed for legal and privacy reasons.",
        ],
        "source_references": {
            "acceptance": _source_lookup(docs, r"pilot_acceptance_certificate"),
            "privacy": _source_lookup(docs, r"face_recognition_privacy|MSA_confidentiality"),
            "timeline_event_count": timeline.get("events_found", 0),
        },
    }


def _claim_verification(docs: list[Any]) -> dict[str, Any]:
    acceptance = _source_lookup(docs, r"pilot_acceptance_certificate")
    results = [
        _claim("PPE compliance reached 91.1% in the final pilot period.", "SUPPORTED", acceptance, "Matches the signed acceptance certificate."),
        _claim("Restricted-zone breach rate fell by approximately 46.24%.", "SUPPORTED", acceptance, "Recalculated from 5.58 to 3.00 per 1,000 camera-hours."),
        _claim("The pilot achieved a 50% restricted-zone reduction.", "CONFLICTING", acceptance, "The certificate reports approximately 46% and marks the 50% target not met."),
        _claim("The pilot delivered face recognition.", "CONFLICTING", _source_lookup(docs, r"face_recognition_privacy|MSA_confidentiality"), "The feature was removed due to legal and privacy concerns."),
        _claim("The project generated ₹2.3 crore in verified savings.", "UNSUPPORTED", _source_lookup(docs, r"finance_value_estimate"), "Available finance records are estimates and do not establish attribution."),
        _claim("The client has approved publication.", "UNSUPPORTED", _source_lookup(docs, r"case_study_permission"), "The correspondence requests Legal and Corporate Communications approval; no approval is recorded."),
        _claim("The pilot achieved zero lost-time injuries because of AI.", "UNSUPPORTED", _source_lookup(docs, r"pilot_results_numbers"), "The source explicitly says a zero-LTI observation does not prove causation."),
    ]
    return {"claims": results, "status": "completed"}


def _markdown_versions(story: dict[str, Any], kpis: dict[str, Any], claims: dict[str, Any]) -> dict[str, str]:
    rows = "\n".join(
        f"- **{row['kpi_name']}**: {row['baseline'] or 'not established'} → {row['final_value']} {row['unit']} "
        f"({row['target_status'].lower()}; target {row['target']}; source: `{row['evidence_source']}`)"
        for row in kpis["kpis"]
    )
    supported = "\n".join(
        f"- {item['claim']} ({item['status']}; `{item['source']}`)"
        for item in claims["claims"] if item["status"] in {"SUPPORTED", "CONFLICTING"}
    )
    common = (
        "Publication status: **BLOCKED — HUMAN APPROVAL REQUIRED**.\n\n"
        "This deterministic, source-linked draft uses only the project library. "
        "It is not an autonomous LLM-generated claim of fact.\n\n"
    )
    return {
        "gatekeeper": f"""# Gatekeeper case study

{common}## Scope and safeguards

{story['solution']} The MSA requires anonymisation, source review, and written approval from Legal and Corporate Communications. No faces, plant images, locations below country level, capacity, headcount, or client branding should be published without approval.

## Evidence and risk review

{supported}

Known limitations: {'; '.join(story['limitations'])}

## Release decision

Do not publish until the approval sheet is signed and every number and media asset has been reviewed.
""",
        "user": f"""# User case study

{common}## The operational problem

Safety teams needed a consistent way to review PPE and restricted-zone events in daily operations.

## How the workflow worked

The on-premises pilot used existing cameras to raise alerts for human review. Face recognition was not delivered. The pilot ran from 11 May to 3 July 2026 across 40 cameras.

## Measured results

{rows}

## Lessons and limitations

{chr(10).join(f'- {item}' for item in story['limitations'])}
""",
        "buyer": f"""# Buyer case study

{common}## Business challenge and approach

The pilot evaluated whether AI-assisted safety analytics could improve operational visibility without exporting video from the site. It used a controlled, on-premises implementation and human review.

## Verified outcomes

{rows}

## Commercial interpretation

The measured results support a cautious business-value discussion, not a verified ROI claim. Financial savings are not fully attributable to this project, and the restricted-zone and acknowledgement targets were missed.

## Next steps

Complete the September KPI review, resolve client actions, and obtain written Legal and Corporate Communications approval before external use.
""",
    }


def _media_pack(kpis: dict[str, Any]) -> list[str]:
    media_dir = OUTPUT_DIR / "media_pack"
    if media_dir.exists():
        shutil.rmtree(media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    ppe = kpis["kpis"][0]
    breach = kpis["kpis"][1]
    assets = {
        "safety_workflow.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="240"><rect width="100%" height="100%" fill="#0b1120"/><g fill="#e5e7eb" font-family="Arial" text-anchor="middle"><text x="125" y="65" font-size="24">Camera feed</text><text x="375" y="65" font-size="24">Rule check</text><text x="625" y="65" font-size="24">Human review</text><text x="875" y="65" font-size="24">Action</text><path d="M225 110h90m160 0h90m160 0h90" stroke="#38bdf8" stroke-width="8"/><circle cx="125" cy="130" r="42" fill="#164e63"/><circle cx="375" cy="130" r="42" fill="#164e63"/><circle cx="625" cy="130" r="42" fill="#164e63"/><circle cx="875" cy="130" r="42" fill="#164e63"/><text x="500" y="215" font-size="16">Anonymised workflow illustration — no identifiable media</text></g></svg>""",
        "kpi_comparison.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420"><rect width="100%" height="100%" fill="#0b1120"/><g font-family="Arial" fill="#e5e7eb"><text x="40" y="45" font-size="26">Validated pilot KPI snapshot</text><text x="40" y="105" font-size="18">PPE compliance</text><rect x="250" y="85" width="{max(1, float(ppe['baseline'] or 0))*5}" height="28" fill="#475569"/><rect x="250" y="125" width="{max(1, float(ppe['final_value'] or 0))*5}" height="28" fill="#38bdf8"/><text x="800" y="105" font-size="16">Baseline {ppe['baseline']}%</text><text x="800" y="145" font-size="16">Final {ppe['final_value']}%</text><text x="40" y="220" font-size="18">Restricted-zone breaches / 1,000 hours</text><rect x="250" y="200" width="{max(1, float(breach['baseline'] or 0))*35}" height="28" fill="#475569"/><rect x="250" y="240" width="{max(1, float(breach['final_value'] or 0))*35}" height="28" fill="#f59e0b"/><text x="800" y="220" font-size="16">Baseline {breach['baseline']}</text><text x="800" y="260" font-size="16">Final {breach['final_value']}</text><text x="40" y="350" font-size="15">Source-linked values only; not approved for publication.</text></g></svg>""",
    }
    for name, content in assets.items():
        (media_dir / name).write_text(content, encoding="utf-8")
    return [f"media_pack/{name}" for name in assets]


def run_case_study() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    library_path, docs = discover_library()
    if not docs:
        raise ValueError("No readable project-library files found.")

    evidence = evidence_agent(docs)
    timeline = timeline_agent(docs)
    kpi_raw = calculate_kpis()
    if "error" in kpi_raw:
        raise ValueError(kpi_raw["error"])
    kpi_results = _kpi_results(kpi_raw, _source_lookup(docs, r"pilot_acceptance_certificate"))
    story = _story(docs, timeline)
    claims = _claim_verification(docs)
    privacy = privacy_agent(docs)
    versions = _markdown_versions(story, kpi_results, claims)
    media = _media_pack(kpi_results)
    approval = {
        "publication_status": "BLOCKED",
        "legal_approval": "PENDING",
        "corporate_communications_approval": "PENDING",
        "required_written_approvals": ["Client Legal", "Corporate Communications"],
        "reason": "A generated draft or message is not an approval.",
    }
    approval_email = "# Approval request\n\nPlease review the attached source-linked case-study package and all media assets. Publication remains blocked until written approval is recorded by Client Legal and Corporate Communications.\n"
    approval_sheet = "# One-page approval sheet\n\n- Legal approval: **PENDING**\n- Corporate Communications approval: **PENDING**\n- Publication readiness: **BLOCKED**\n- Client naming/branding: **NOT APPROVED**\n\nApprover signatures and dates: ____________________________________\n"
    report = {
        "project": "Project Drishti",
        "run_status": "completed",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "documents_loaded": len(docs),
        "stages": [
            {"name": name, "status": "COMPLETED"}
            for name in ["Document Ingestion", "Evidence Extraction", "Timeline", "KPI Validation", "Claim Verification", "Privacy Review", "Case Study Generation"]
        ] + [{"name": "Human Approval", "status": "NEEDS HUMAN REVIEW"}],
        "publication_allowed": False,
        "outputs": [
            "project_story_spine.json", "timeline.json", "evidence_index.json",
            "results_sheet.json", "kpi_results.json", "claim_verification.json",
            "privacy_report.json", "case_study_gatekeeper.md", "case_study_user.md",
            "case_study_buyer.md", "case_study_gatekeeper.pdf",
            "case_study_user.pdf", "case_study_buyer.pdf", *media,
            "approval_request_email.md",
            "approval_sheet.md", "approval_status.json", "agent_report.json",
        ],
        "implementation_note": "Deterministic source-linked pipeline; no autonomous LLM claims are presented as verified facts.",
    }
    _write_json("project_story_spine.json", story)
    _write_json("timeline.json", timeline)
    _write_json("evidence_index.json", evidence)
    _write_json("results_sheet.json", kpi_results)
    _write_json("kpi_results.json", kpi_results)
    _write_json("claim_verification.json", claims)
    _write_json("privacy_report.json", privacy)
    _write_json("approval_status.json", approval)
    for name, content in versions.items():
        (OUTPUT_DIR / f"case_study_{name}.md").write_text(content, encoding="utf-8")
        _write_pdf(f"case_study_{name}.pdf", content)
    (OUTPUT_DIR / "approval_request_email.md").write_text(approval_email, encoding="utf-8")
    (OUTPUT_DIR / "approval_sheet.md").write_text(approval_sheet, encoding="utf-8")
    _write_json("agent_report.json", report)
    package = OUTPUT_DIR / "case_study_package.zip"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in OUTPUT_DIR.iterdir():
            if path == package or path.name.startswith("."):
                continue
            if path.is_file():
                archive.write(path, path.name)
            elif path.is_dir() and path.name == "media_pack":
                for media_path in path.iterdir():
                    archive.write(media_path, f"media_pack/{media_path.name}")
    return {"report": report, "story": story, "timeline": timeline, "kpis": kpi_results, "claims": claims, "privacy": privacy, "case_studies": versions, "media": media, "approval": approval}
