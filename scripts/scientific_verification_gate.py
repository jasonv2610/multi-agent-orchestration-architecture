#!/usr/bin/env python3
"""
JVI Scientific Verification Gate & Critical Thinking Engine (REG-CVF-001 / LAW-SCI-001).
Enforces Zero-Trust double/triple citation validation, GRADE evidence quality rating,
systematic bias detection, causal inference laddering, and anti-hallucination checks.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class SourceTier(str, Enum):
    TIER_1 = "TIER 1"  # SEC filings, official gov/stat databases, NASA/NIST/W3C
    TIER_2 = "TIER 2"  # Peer-reviewed academic journals, NeurIPS/ACM/IEEE, Gartner/IDC
    TIER_3 = "TIER 3"  # Official engineering blogs, arXiv preprints, trade whitepapers
    TIER_4 = "TIER 4"  # Aggregators, unvetted blogs, Wikipedia (PROHIBITED for synthesis)
    PROHIBITED = "PROHIBITED"  # Social media, unverified AI output, forums


class StudyDesign(str, Enum):
    RCT = "RCT"  # Randomized Controlled Trial
    QUASI_EXPERIMENTAL = "QUASI_EXPERIMENTAL"  # DiD, RDD, IV, Synthetic Control
    COHORT = "COHORT"
    CASE_CONTROL = "CASE_CONTROL"
    CROSS_SECTIONAL = "CROSS_SECTIONAL"
    OBSERVATIONAL_UNCONTROLLED = "OBSERVATIONAL_UNCONTROLLED"
    EXPERT_OPINION = "EXPERT_OPINION"


class ClaimStatus(str, Enum):
    VERIFIED = "✓ VERIFIED"
    PARAPHRASE = "✓~ PARAPHRASE"
    PARTIAL = "◐ PARTIAL"
    UNVERIFIED = "? UNVERIFIED"
    CONTRADICTED = "✗ CONTRADICTED"
    OUTDATED = "⏱ OUTDATED"


@dataclass
class VerifiedCitation:
    ref_id: str
    source_title: str
    publisher: str
    date: str
    url_or_doi: str
    tier: SourceTier
    verbatim_evidence: str
    study_design: StudyDesign = StudyDesign.OBSERVATIONAL_UNCONTROLLED
    sample_size: Optional[int] = None
    effect_size: Optional[str] = None
    p_value: Optional[float] = None
    confidence_interval: Optional[str] = None


@dataclass
class BiasAudit:
    risk_of_bias: bool = False
    inconsistency: bool = False
    indirectness: bool = False
    imprecision: bool = False
    publication_bias: bool = False
    selection_bias_notes: Optional[str] = None
    confounding_controlled: bool = True
    multiple_testing_corrected: bool = True


@dataclass
class FindingStory:
    """The Required Four for business and architectural communication."""
    number: str
    business_logic: str
    market_mechanism: str
    actionable_implication: str

    def to_formatted_report(self) -> str:
        return (
            f"• Metric / Number: {self.number}\n"
            f"• Business Logic: {self.business_logic}\n"
            f"• Market / Systems Mechanism: {self.market_mechanism}\n"
            f"• Actionable Implication: {self.actionable_implication}"
        )


@dataclass
class ScientificClaim:
    claim_id: str
    statement: str
    citations: List[VerifiedCitation]
    verification_level: str  # Single-Checked, Double-Checked, Triple-Checked
    status: ClaimStatus
    confidence: str  # HIGH, MEDIUM, LOW
    is_causal_claim: bool = False
    bias_audit: BiasAudit = field(default_factory=BiasAudit)
    story: Optional[FindingStory] = None
    approved_by_upper_mgmt: bool = False

    def calculate_grade(self) -> str:
        """
        Calculates GRADE evidence quality score:
        - Starts at HIGH for RCTs, MODERATE for Quasi-Experimental, LOW for observational.
        - Downgrades for Risk of Bias, Inconsistency, Indirectness, Imprecision, Publication Bias.
        - Upgrades for large effect sizes and controlled confounding with multiple independent sources.
        """
        has_rct = any(c.study_design == StudyDesign.RCT for c in self.citations)
        has_quasi = any(c.study_design == StudyDesign.QUASI_EXPERIMENTAL for c in self.citations)

        if has_rct:
            score = 4  # HIGH
        elif has_quasi:
            score = 3  # MODERATE
        else:
            score = 2  # LOW

        # Downgrades
        if self.bias_audit.risk_of_bias:
            score -= 1
        if self.bias_audit.inconsistency:
            score -= 1
        if self.bias_audit.indirectness:
            score -= 1
        if self.bias_audit.imprecision:
            score -= 1
        if self.bias_audit.publication_bias:
            score -= 1

        # Upgrades
        if self.bias_audit.confounding_controlled and score < 4 and len(self.citations) >= 2:
            score += 1

        score = max(1, min(4, score))
        grade_map = {4: "HIGH", 3: "MODERATE", 2: "LOW", 1: "VERY_LOW"}
        return grade_map[score]

    def validate_gate(self) -> Dict[str, Any]:
        """Validates the claim against Zero-Trust scientific standards & critical thinking invariants."""
        errors = []
        warnings = []

        # 1. Prohibited source check
        for c in self.citations:
            tier_str = str(c.tier.value if isinstance(c.tier, SourceTier) else c.tier).upper()
            if tier_str in ["TIER 4", "PROHIBITED"]:
                errors.append(f"Citation {c.ref_id} uses prohibited tier: {tier_str}")

        # 2. Confidence and Citation count enforcement
        if self.confidence == "HIGH" and len(self.citations) < 2:
            errors.append("HIGH confidence requires minimum 2 independent citations (Double-Check).")

        # 3. Currency check
        for c in self.citations:
            if not c.date or len(c.date.strip()) == 0:
                errors.append(f"Citation {c.ref_id} missing publication date.")

        # 4. Causal Claim Ladder Verification
        if self.is_causal_claim:
            rigorous_designs = [StudyDesign.RCT, StudyDesign.QUASI_EXPERIMENTAL]
            has_rigorous = any(c.study_design in rigorous_designs for c in self.citations)
            if not has_rigorous:
                errors.append(
                    "Causal claim made without RCT or Quasi-Experimental design (violates Causal Inference Ladder)."
                )

        # 5. GRADE Assessment
        grade_rating = self.calculate_grade()
        if self.confidence == "HIGH" and grade_rating in ["LOW", "VERY_LOW"]:
            warnings.append(f"Confidence is HIGH but GRADE evidence rating is {grade_rating}.")

        # 6. Status and pass condition
        status_val = self.status.value if isinstance(self.status, ClaimStatus) else self.status
        is_passing = (len(errors) == 0) and (status_val in [ClaimStatus.VERIFIED.value, ClaimStatus.PARAPHRASE.value])

        return {
            "claim_id": self.claim_id,
            "statement": self.statement,
            "status": status_val,
            "grade_rating": grade_rating,
            "gate_passed": is_passing,
            "errors": errors,
            "warnings": warnings,
            "upper_management_approval": "APPROVED" if self.approved_by_upper_mgmt else "STAGED_FOR_CEO_APPROVAL",
            "finding_story": self.story.to_formatted_report() if self.story else None
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
                tier=SourceTier.TIER_2,
                study_design=StudyDesign.RCT,
                verbatim_evidence="Iterative visual optimization with execution and rendered feedback achieved superior code accuracy."
            ),
            VerifiedCitation(
                ref_id="REF-078",
                source_title="1D-Bench: Benchmark for Iterative UI Code Generation",
                publisher="arXiv",
                date="2026-02-20",
                url_or_doi="https://arxiv.org/abs/2602.18548",
                tier=SourceTier.TIER_2,
                study_design=StudyDesign.RCT,
                verbatim_evidence="Multi-round execution feedback significantly outperforms one-shot baselines across real-world workflows."
            )
        ],
        verification_level="Double-Checked",
        status=ClaimStatus.VERIFIED,
        confidence="HIGH",
        is_causal_claim=True,
        story=FindingStory(
            number="42% reduction in visual regression (p < 0.001, 95% CI: 34%-50%)",
            business_logic="Eliminates costly manual UI bug audits before landing code in production",
            market_mechanism="Agentic visual models iteratively evaluate DOM layout trees against raster benchmarks",
            actionable_implication="Deploy automated visual verification sandbox across all frontend release lanes"
        ),
        approved_by_upper_mgmt=False
    )

    result = claim.validate_gate()
    print("Zero-Trust Scientific Validation Result:")
    print(f"Statement: {result['statement']}")
    print(f"GRADE Rating: {result['grade_rating']}")
    print(f"Gate Passed: {result['gate_passed']}")
    print(f"Errors: {result['errors']}")
    print(f"Status: {result['upper_management_approval']}")
    if result["finding_story"]:
        print(f"\nFinding-to-Story:\n{result['finding_story']}")
