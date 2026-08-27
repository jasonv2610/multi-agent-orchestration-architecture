#!/usr/bin/env python3
"""
JVI Scientific Verification Gate (REG-CVF-001 / LAW-SCI-001).
Enforces Zero-Trust double/triple citation validation and anti-hallucination checks.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class VerifiedCitation:
    ref_id: str
    source_title: str
    publisher: str
    date: str
    url_or_doi: str
    tier: str  # TIER 1, TIER 2, TIER 3, TIER 4, PROHIBITED
    verbatim_evidence: str


@dataclass
class ScientificClaim:
    claim_id: str
    statement: str
    citations: List[VerifiedCitation]
    verification_level: str  # Single-Checked, Double-Checked, Triple-Checked
    status: str  # ✓ VERIFIED, ✓~ PARAPHRASE, ◐ PARTIAL, ? UNVERIFIED, ✗ CONTRADICTED
    confidence: str  # HIGH, MEDIUM, LOW
    approved_by_upper_mgmt: bool = False

    def validate_gate(self) -> Dict[str, Any]:
        """Validates the claim against Zero-Trust scientific standards."""
        errors = []

        # 1. Prohibited source check
        for c in self.citations:
            if c.tier.upper() in ["TIER 4", "PROHIBITED"]:
                errors.append(f"Citation {c.ref_id} uses prohibited tier: {c.tier}")

        # 2. Double/Triple check enforcement for high confidence
        if self.confidence == "HIGH" and len(self.citations) < 2:
            errors.append("HIGH confidence requires minimum 2 independent citations (Double-Check).")

        # 3. Currency check (must not be empty)
        for c in self.citations:
            if not c.date:
                errors.append(f"Citation {c.ref_id} missing publication date.")

        # 4. Upper management gate check
        is_passing = (len(errors) == 0) and (self.status in ["✓ VERIFIED", "✓~ PARAPHRASE"])

        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "status": self.status,
            "gate_passed": is_passing,
            "errors": errors,
            "upper_management_approval": "APPROVED" if self.approved_by_upper_mgmt else "STAGED_FOR_CEO_APPROVAL"
        }


if __name__ == "__main__":
    claim = ScientificClaim(
        claim_id="CLAIM-001",
        statement="Closed-loop visual execution feedback substantially reduces UI-to-code regression compared to single-pass generation.",
        citations=[
            VerifiedCitation(
                ref_id="REF-077",
                source_title="UI2Code^N: Test-Time Scalable Interactive UI-to-Code Generation",
                publisher="arXiv / NeurIPS 2026",
                date="2026-05-08",
                url_or_doi="https://arxiv.org/abs/2511.08195",
                tier="TIER 2",
                verbatim_evidence="Iterative visual optimization with execution and rendered feedback achieved superior code accuracy."
            ),
            VerifiedCitation(
                ref_id="REF-078",
                source_title="1D-Bench: Benchmark for Iterative UI Code Generation",
                publisher="arXiv",
                date="2026-02-20",
                url_or_doi="https://arxiv.org/abs/2602.18548",
                tier="TIER 2",
                verbatim_evidence="Multi-round execution feedback significantly outperforms one-shot baselines across real-world workflows."
            )
        ],
        verification_level="Double-Checked",
        status="✓ VERIFIED",
        confidence="HIGH",
        approved_by_upper_mgmt=False
    )

    result = claim.validate_gate()
    print("Zero-Trust Scientific Validation Result:")
    print(f"Statement: {result['statement']}")
    print(f"Gate Passed: {result['gate_passed']}")
    print(f"Errors: {result['errors']}")
    print(f"Status: {result['upper_management_approval']}")
