"""Critic agent for validating HelpMate RCA drafts.

Validates required sections, citation IDs, inline citations, and unsafe content.
This is a validation layer, not a substitute for action-time security guardrails.
"""

import ast
import re
from datetime import datetime, timezone

REQUIRED = [
    "Summary:",
    "Affected Scope & Environment:",
    "Diagnosis & Root Cause:",
    "Resolution / Recommended Fix:",
    "Verification:",
    "Preventive Action / KB Update:",
    "References:",
]

CITATION_PATTERN = re.compile(r"\[([A-Za-z0-9_-]+(?:\s*,\s*[A-Za-z0-9_-]+)*)\]")
KNOWLEDGE_CLAIM_PATTERN = re.compile(
    r"\b(root cause|caused by|because|restart|reset|reinstall|certificate|"
    r"configuration|workaround|resolution|diagnos|should check|verify|"
    r"update|repair|known issue|kb article|recommended fix|preventive action)\b",
    re.I,
)
UNSAFE_PATTERNS = [
    re.compile(
        r"\b(reveal|print|display|expose|send|exfiltrate)\b.{0,50}"
        r"\b(api keys?|secrets?|credentials?|passwords?|tokens?)\b",
        re.I,
    ),
    re.compile(
        r"\b(disable|bypass|turn off)\b.{0,50}"
        r"\b(security|authentication|authorization|approval|guardrails?)\b",
        re.I,
    ),
    re.compile(
        r"\b(reset all administrator passwords|reveal credentials|"
        r"passwords have been reset|credentials were revealed)\b",
        re.I,
    ),
    re.compile(
        r"\b(ignore all (previous|prior|safety) instructions|"
        r"override (the )?(system|security) prompt)\b",
        re.I,
    ),
]

# These phrases explicitly distinguish a reported symptom or a proposed action
# from an independently established technical fact.
NON_FACTUAL_PREFIXES = (
    "ticket-reported and not independently verified:",
    "unverified ticket-reported possibility:",
    "unverified hypothesis (not established by retrieved evidence):",
    "proposed action for technician validation (not confirmed by retrieved evidence):",
    "insufficient evidence to determine",
    "the exact root cause is unknown",
    "the cause is not established",
    "the ticket reports",
    "the user reports",
    "according to the ticket",
)


class CriticAgent:
    """Validate a drafted RCA note against retrieved evidence."""

    def review(self, draft, evidence, ticket):
        """Return approval status, issues, valid source IDs, and UTC review time."""
        del ticket
        issues = []
        evidence_list = list(evidence or [])
        valid_ids = {
            str(item["id"]).strip()
            for item in evidence_list
            if isinstance(item, dict) and item.get("id") is not None
        }

        note_value = draft.get("note", draft) if isinstance(draft, dict) else draft
        note = self._normalize_note(note_value)
        if not note.strip():
            issues.append("RCA note is empty.")

        missing = self._missing_sections(note)
        if missing:
            issues.append("Missing required sections: " + ", ".join(missing))

        claims = draft.get("claims", []) if isinstance(draft, dict) else []
        if claims is None:
            claims = []
        if not isinstance(claims, list):
            issues.append("Draft claims must be a list.")
            claims = []

        for claim in claims:
            if not isinstance(claim, dict):
                issues.append("A claim entry is not a dictionary.")
                continue

            claim_text = str(claim.get("text", "")).strip()
            source_ids = claim.get("source_ids", [])
            if not isinstance(source_ids, list):
                issues.append("Claim source_ids must be a list: " + claim_text[:100])
                continue
            source_ids = [str(source_id).strip() for source_id in source_ids]

            if not claim_text:
                issues.append("An empty claim was supplied.")
            elif (
                self._knowledge_claim(claim_text)
                and not source_ids
                and not self._is_explicitly_non_factual(claim_text)
            ):
                issues.append("Claim has no retrieved source: " + claim_text[:100])

            invalid_ids = [source_id for source_id in source_ids if source_id not in valid_ids]
            if invalid_ids:
                issues.append(
                    "Claim cites source ID(s) not present in retrieved evidence: "
                    + ", ".join(invalid_ids)
                    + " | Claim: " + claim_text[:100]
                )

        cited_ids = set()
        for match in CITATION_PATTERN.finditer(note):
            cited_ids.update(
                source_id.strip()
                for source_id in match.group(1).split(",")
                if source_id.strip()
            )

        invalid_note_ids = cited_ids - valid_ids
        if invalid_note_ids:
            issues.append(
                "Note contains citation IDs not present in retrieved evidence: "
                + ", ".join(sorted(invalid_note_ids))
            )

        for heading in (
            "Diagnosis & Root Cause:",
            "Resolution / Recommended Fix:",
            "Preventive Action / KB Update:",
        ):
            for sentence in self._sentences(self._section(note, heading)):
                sentence = sentence.strip()
                if (
                    len(sentence) > 35
                    and self._knowledge_claim(sentence)
                    and not CITATION_PATTERN.search(sentence)
                    and not self._is_explicitly_non_factual(sentence)
                ):
                    issues.append(
                        "Technical sentence lacks inline citation: " + sentence[:100]
                    )

        # Flag harmful instructions/actions, but do not flag a neutral summary
        # merely because the original ticket is quoted in the input. The worker
        # should avoid reproducing the malicious instruction in the RCA note.
        if any(pattern.search(note) for pattern in UNSAFE_PATTERNS):
            issues.append(
                "Potentially unsafe instruction or secret-disclosure content detected."
            )

        issues = list(dict.fromkeys(issues))
        return {
            "approved": not issues,
            "issues": issues,
            "valid_source_ids": sorted(valid_ids),
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _is_explicitly_non_factual(text):
        """Check for explicit attribution, uncertainty, or proposal wording."""
        lowered = re.sub(r"\s+", " ", text.strip()).casefold()
        return any(lowered.startswith(prefix) for prefix in NON_FACTUAL_PREFIXES)

    @staticmethod
    def _normalize_note(note):
        """Convert text or section dictionaries into consistent RCA text."""
        if isinstance(note, dict):
            section_dict = note
        elif isinstance(note, str):
            stripped = note.strip()
            section_dict = None
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    parsed = ast.literal_eval(stripped)
                    if isinstance(parsed, dict):
                        section_dict = parsed
                except (ValueError, SyntaxError):
                    section_dict = None
            if section_dict is None:
                return note
        elif note is None:
            return ""
        else:
            return str(note)

        parts = []
        for heading, body in section_dict.items():
            heading_text = str(heading).strip().rstrip(":")
            if heading_text:
                parts.append(f"{heading_text}:\n{str(body).strip()}")
        return "\n\n".join(parts)

    @staticmethod
    def _missing_sections(note):
        """Return required headings absent from the normalized note."""
        normalized = re.sub(r"\s+", " ", note).casefold()
        return [
            heading for heading in REQUIRED
            if re.sub(r"\s+", " ", heading).casefold() not in normalized
        ]

    @staticmethod
    def _knowledge_claim(text):
        """Identify likely technical claims."""
        return bool(KNOWLEDGE_CLAIM_PATTERN.search(text))

    @staticmethod
    def _section(note, heading):
        """Extract one RCA section until the next required heading."""
        heading_pattern = re.escape(heading.rstrip(":"))
        match = re.search(rf"(?im)^\s*{heading_pattern}\s*:\s*", note)
        if not match:
            match = re.search(rf"(?i){heading_pattern}\s*:\s*", note)
        if not match:
            return ""

        start = match.end()
        next_heading_pattern = re.compile(
            r"(?im)^\s*(?:"
            + "|".join(re.escape(item.rstrip(":")) for item in REQUIRED)
            + r")\s*:\s*"
        )
        next_match = next_heading_pattern.search(note, start)
        return note[start:next_match.start()] if next_match else note[start:]

    @staticmethod
    def _sentences(text):
        """Split section text into approximate sentences."""
        return re.split(r"(?<=[.!?])\s+|\n+", text)
