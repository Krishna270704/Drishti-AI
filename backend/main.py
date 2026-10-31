
import os
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
import pymupdf
from docx import Document
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from analysis_engine import run_analysis
from kpi_engine import calculate_kpis
from claim_engine import verify_claim

from agent_engine import run_drishti
from case_study_engine import run_case_study


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
LIBRARY_DIR = UPLOAD_DIR / "project_library"
FRONTEND_DIR = BASE_DIR / "frontend"

load_dotenv(BACKEND_DIR / ".env")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED = {".pdf", ".docx", ".txt", ".md", ".csv"}

app = FastAPI(
    title="Project Drishti - AI Case Study Engine",
    description="Evidence-backed project case study generation",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# PROJECT STATE
# --------------------------------------------------

PROJECT_DATA = {
    "project_name": "Project Drishti",
    "files": [],
    "evidence": [],
    "timeline": [],
    "kpis": [],
    "privacy_risks": [],
    "case_studies": {},
    "approval": {
        "status": "PENDING",
        "approved_by": None
    }
}


class ClaimRequest(BaseModel):
    claim: str


class ApprovalRequest(BaseModel):
    approved_by: str
    decision: str


class AgentRunRequest(BaseModel):
    project_name: str = "Project Drishti"


# --------------------------------------------------
# DOCUMENT EXTRACTION
# --------------------------------------------------

def extract_file(file_path):
    extension = file_path.suffix.lower()

    try:
        if extension == ".pdf":
            with pymupdf.open(file_path) as doc:
                return "\n".join(page.get_text() for page in doc)

        if extension == ".docx":
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

        if extension in [".txt", ".md"]:
            return file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        if extension == ".csv":
            df = pd.read_csv(file_path)
            return df.to_string(index=False)

    except Exception as error:
        return f"EXTRACTION ERROR: {error}"

    return ""


def save_evidence(file_path, content, relative_path=None):
    record = {
        "source": relative_path or file_path.name,
        "content": content[:50000],
        "extracted_at": datetime.now().isoformat(),
        "verified": False
    }

    PROJECT_DATA["evidence"].append(record)
    return record


def process_directory(directory):
    processed = []

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED:
            continue

        content = extract_file(file_path)

        if not content or content.startswith("EXTRACTION ERROR"):
            continue

        relative_path = str(file_path.relative_to(directory))

        PROJECT_DATA["files"].append({
            "filename": relative_path,
            "type": file_path.suffix.lower(),
            "characters": len(content),
            "status": "PROCESSED"
        })

        save_evidence(file_path, content, relative_path)
        processed.append(relative_path)

    return processed


# --------------------------------------------------
# SAFE ZIP EXTRACTION
# --------------------------------------------------

def extract_project_zip(zip_path):
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    # Validate every ZIP member before extracting.
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            target = (LIBRARY_DIR / member.filename).resolve()

            if not target.is_relative_to(LIBRARY_DIR.resolve()):
                raise ValueError("Unsafe ZIP path detected.")

        archive.extractall(LIBRARY_DIR)


# --------------------------------------------------
# AUTOMATIC LIBRARY LOADING
# --------------------------------------------------

def load_project_library():
    zip_path = UPLOAD_DIR / "Project_Drishti_Library.zip"

    if not zip_path.exists():
        print("WARNING: Project_Drishti_Library.zip not found.")
        return False

    # Clear in-memory state before loading.
    PROJECT_DATA["files"] = []
    PROJECT_DATA["evidence"] = []

    try:
        extract_project_zip(zip_path)

        processed = process_directory(LIBRARY_DIR)

        summary = {
            "filename": zip_path.name,
            "processed_files": len(processed),
            "evidence_records": len(PROJECT_DATA["evidence"]),
            "files": processed,
            "loaded_at": datetime.now().isoformat()
        }

        (OUTPUT_DIR / "ingestion_report.json").write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8"
        )

        print(
            f"Project library loaded successfully: "
            f"{len(processed)} files, "
            f"{len(PROJECT_DATA['evidence'])} evidence records"
        )

        return True

    except Exception as error:
        print(f"Library auto-load failed: {error}")
        return False


@app.on_event("startup")
def startup_event():
    load_project_library()


# --------------------------------------------------
# HOME AND STATUS
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Project Drishti API is running",
        "project": PROJECT_DATA["project_name"],
        "status": "READY"
    }


@app.get("/api/status")
def get_status():
    return {
        "project": PROJECT_DATA["project_name"],
        "files_processed": len(PROJECT_DATA["files"]),
        "evidence_records": len(PROJECT_DATA["evidence"]),
        "approval_status": PROJECT_DATA["approval"]["status"],
        "groq_configured": bool(os.getenv("GROQ_API_KEY"))
    }


# --------------------------------------------------
# UPLOAD API - OPTIONAL MANUAL UPLOAD
# --------------------------------------------------

@app.post("/api/upload")
async def upload_project(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Please upload a ZIP file.")

    zip_path = UPLOAD_DIR / "Project_Drishti_Library.zip"

    try:
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        PROJECT_DATA["files"] = []
        PROJECT_DATA["evidence"] = []

        # Remove previous extracted content.
        if LIBRARY_DIR.exists():
            shutil.rmtree(LIBRARY_DIR)

        LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

        extract_project_zip(zip_path)
        processed = process_directory(LIBRARY_DIR)

        summary = {
            "filename": zip_path.name,
            "processed_files": len(processed),
            "evidence_records": len(PROJECT_DATA["evidence"]),
            "files": processed
        }

        (OUTPUT_DIR / "ingestion_report.json").write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8"
        )

        return summary

    except zipfile.BadZipFile:
        raise HTTPException(400, "Invalid ZIP file.")

    except Exception as error:
        raise HTTPException(500, str(error))

    finally:
        await file.close()


# --------------------------------------------------
# EVIDENCE AND FILES
# --------------------------------------------------

@app.get("/api/evidence")
def get_evidence():
    return {
        "count": len(PROJECT_DATA["evidence"]),
        "evidence": [
            {
                "source": item["source"],
                "characters": len(item["content"]),
                "preview": item["content"][:300]
            }
            for item in PROJECT_DATA["evidence"]
        ]
    }


@app.get("/api/files")
def get_files():
    return {
        "count": len(PROJECT_DATA["files"]),
        "files": PROJECT_DATA["files"]
    }


# --------------------------------------------------
# EXISTING ANALYSIS ENGINE
# --------------------------------------------------

@app.post("/api/analyze")
def analyze():
    result = run_analysis()

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


@app.get("/api/report")
def get_report():
    report_path = OUTPUT_DIR / "analysis_report.json"

    if not report_path.exists():
        raise HTTPException(404, "Run analysis first.")

    return json.loads(
        report_path.read_text(encoding="utf-8")
    )


# --------------------------------------------------
# KPI ENGINE
# --------------------------------------------------

@app.get("/api/kpis")
def get_kpis():
    result = calculate_kpis()

    if "error" in result:
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )

    return result


# --------------------------------------------------
# CLAIM VERIFICATION
# --------------------------------------------------

@app.post("/api/verify-claim")
def verify_claim_api(request: ClaimRequest):
    if not request.claim.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide a claim."
        )

    return verify_claim(request.claim)


# --------------------------------------------------
# HUMAN APPROVAL GATE
# --------------------------------------------------

@app.get("/api/approval")
def get_approval():
    return PROJECT_DATA["approval"]


@app.post("/api/approval")
def record_approval(data: ApprovalRequest):
    approver = data.approved_by.strip()
    decision = data.decision.upper()

    if not approver or decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(
            400,
            "Valid approver and decision required."
        )

    PROJECT_DATA["approval"] = {
        "status": decision,
        "approved_by": approver,
        "recorded_at": datetime.now().isoformat()
    }

    return {
        "message": "Internal decision recorded. No external publication performed.",
        "approval": PROJECT_DATA["approval"]
    }


# --------------------------------------------------
# PUBLICATION SAFETY CHECK
# --------------------------------------------------

@app.post("/api/publication-check")
def publication_check():
    approval = PROJECT_DATA["approval"]

    if approval["status"] != "APPROVED":
        return {
            "publication_allowed": False,
            "reason": "Human approval is required before publication."
        }

    return {
        "publication_allowed": True,
        "reason": "Internal approval recorded. External client permissions must still be respected."
    }


# --------------------------------------------------
# GROQ CONFIGURATION CHECK
# --------------------------------------------------

@app.get("/api/ai-status")
def ai_status():
    key_exists = bool(os.getenv("GROQ_API_KEY"))

    return {
        "provider": "Groq",
        "configured": key_exists,
        "message": (
            "Groq API key detected."
            if key_exists
            else "GROQ_API_KEY missing from backend/.env"
        )
    }


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.get("/dashboard")
def dashboard():
    index_path = FRONTEND_DIR / "index.html"

    if not index_path.exists():
        raise HTTPException(404, "Dashboard file not found.")

    return FileResponse(index_path)


# --------------------------------------------------
# AGENT WORKFLOW
# --------------------------------------------------

@app.post("/api/run-agents")
def run_agents(request: AgentRunRequest | None = None):
    try:
        result = run_case_study()
        return result["report"]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent workflow failed: {str(error)}"
        )


@app.get("/api/case-study-drafts")
def get_case_study_drafts():
    drafts = {}
    for audience in ("gatekeeper", "user", "buyer"):
        path = OUTPUT_DIR / f"case_study_{audience}.md"
        if path.exists():
            drafts[audience] = path.read_text(encoding="utf-8")
    if not drafts:
        raise HTTPException(404, "Run the case-study generator first.")
    return {"drafts": drafts}


@app.get("/api/output-files")
def get_output_files():
    if not OUTPUT_DIR.exists():
        return {"files": []}
    files = []
    for path in sorted(OUTPUT_DIR.rglob("*")):
        if path.is_file() and path.name != "case_study_package.zip":
            files.append(str(path.relative_to(OUTPUT_DIR)).replace("\\", "/"))
    return {"files": files}


@app.get("/api/publication-check")
def get_publication_check():
    approval_path = OUTPUT_DIR / "approval_status.json"
    if not approval_path.exists():
        return {"publication_allowed": False, "reason": "Generate the case-study package first."}
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    return {
        "publication_allowed": approval.get("publication_status") == "APPROVED",
        "reason": approval.get("reason", "Written approvals are required."),
        "approval": approval,
    }


@app.get("/api/download/{file_path:path}")
def download_output(file_path: str):
    requested = (OUTPUT_DIR / file_path).resolve()
    if not requested.is_relative_to(OUTPUT_DIR.resolve()) or not requested.is_file():
        raise HTTPException(404, "Output file not found.")
    return FileResponse(requested)


@app.get("/api/download-package")
def download_package():
    package = OUTPUT_DIR / "case_study_package.zip"
    if not package.exists():
        raise HTTPException(404, "Generate the case-study package first.")
    return FileResponse(package, filename=package.name, media_type="application/zip")


@app.get("/api/agent-report")
def get_agent_report():
    path = OUTPUT_DIR / "agent_report.json"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Run the agent workflow first."
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )