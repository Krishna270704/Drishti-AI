
from pathlib import Path
import re


def get_library_root():
    return (
        Path(__file__).resolve().parent.parent
        / "uploads"
        / "project_library"
    )


def load_documents():
    root = get_library_root()
    documents = []

    if not root.exists():
        return documents

    supported = {".md", ".txt", ".csv"}

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in supported:
            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
                documents.append({
                    "source": str(path.relative_to(root)),
                    "content": content
                })
            except Exception:
                continue

    return documents


def find_evidence(documents, keywords, limit=3):
    results = []

    for doc in documents:
        content = doc["content"]
        lower_content = content.lower()

        if all(word.lower() in lower_content for word in keywords):
            for keyword in keywords:
                position = lower_content.find(keyword.lower())
                if position >= 0:
                    start = max(0, position - 180)
                    end = min(len(content), position + 350)

                    results.append({
                        "source": doc["source"],
                        "snippet": content[start:end].strip()
                    })
                    break

        if len(results) >= limit:
            break

    return results


def verify_claim(claim):
    documents = load_documents()

    if not documents:
        return {
            "claim": claim,
            "status": "NEEDS REVIEW",
            "reason": "Project library not found or no readable documents.",
            "evidence": []
        }

    text = claim.lower()

    # Rule 1: Pilot PPE result
    if (
        "91.1" in text
        and ("ppe" in text or "compliance" in text)
    ):
        evidence = find_evidence(
            documents,
            ["91.1%", "PPE"]
        )

        return {
            "claim": claim,
            "status": "SUPPORTED" if evidence else "NEEDS REVIEW",
            "reason": (
                "The signed pilot acceptance certificate reports "
                "91.1% PPE compliance for the pilot's final measurement period."
                if evidence else
                "The expected source text was not located."
            ),
            "evidence": evidence,
            "limitation": "This refers to the pilot acceptance period, not every later deployment period."
        }

    # Rule 2: 97% PPE claim
    if (
        ("97%" in text or "97 percent" in text)
        and ("ppe" in text or "compliance" in text)
    ):
        evidence = find_evidence(
            documents,
            ["91.1%", "PPE"]
        )

        return {
            "claim": claim,
            "status": "CONFLICTING" if evidence else "NEEDS REVIEW",
            "reason": (
                "The signed pilot acceptance certificate reports 91.1%, "
                "not 97%, for its stated pilot measurement period. "
                "A different period or cohort would need separate evidence."
            ),
            "evidence": evidence,
            "limitation": "Do not use 97% as the pilot acceptance result."
        }

    # Rule 3: Zero accidents caused by AI
    if (
        ("zero accident" in text or "zero accidents" in text
         or "zero lti" in text)
        and ("ai" in text or "project" in text or "drishti" in text)
    ):
        evidence = find_evidence(
            documents,
            ["lost_time_injuries"]
        )

        return {
            "claim": claim,
            "status": "UNSUPPORTED",
            "reason": (
                "The available records do not establish that AI caused "
                "zero accidents. A zero-LTI figure alone cannot prove causation."
            ),
            "evidence": evidence,
            "limitation": "Do not claim that the AI system prevented all accidents."
        }

    # Rule 4: Face recognition delivered
    if "face recognition" in text or "facial recognition" in text:
        evidence = find_evidence(
            documents,
            ["removed", "face"]
        )

        return {
            "claim": claim,
            "status": "CONFLICTING" if evidence else "NEEDS REVIEW",
            "reason": (
                "Project change records indicate that face recognition "
                "was removed following legal and privacy concerns."
                if evidence else
                "No clear source was found to establish delivery of face recognition."
            ),
            "evidence": evidence,
            "limitation": "Do not describe face recognition as a delivered feature."
        }

    # Generic evidence lookup
    words = [
        word for word in re.findall(r"[a-zA-Z0-9.%-]+", text)
        if len(word) > 3
    ]

    evidence = find_evidence(
        documents,
        words[:2] if len(words) >= 2 else words
    ) if words else []

    if evidence:
        status = "NEEDS REVIEW"
        reason = (
            "Related source text was found, but the claim has not "
            "been semantically or numerically verified."
        )
    else:
        status = "UNSUPPORTED"
        reason = (
            "No matching source evidence was found in the indexed project documents."
        )

    return {
        "claim": claim,
        "status": status,
        "reason": reason,
        "evidence": evidence,
        "limitation": "Keyword matches are leads for human review, not proof."
    }
