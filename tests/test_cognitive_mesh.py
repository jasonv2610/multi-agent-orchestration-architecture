#!/usr/bin/env python3
"""
Unit tests for JVI Cognitive Tier Translator & Pod Mesh Router.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from cognitive_tier_translator import (
    UniversalMeshMessage,
    Tier1OperatorView,
    Tier2BuilderView,
    Tier3ArchitectView,
    explain_system_concept
)
from pod_mesh_router import PodMeshRouter


from scientific_verification_gate import (
    ScientificClaim,
    VerifiedCitation,
    SourceTier,
    StudyDesign,
    ClaimStatus,
    BiasAudit,
    FindingStory
)


class TestCognitiveMesh(unittest.TestCase):

    def setUp(self):
        self.router = PodMeshRouter()
        self.msg = UniversalMeshMessage.create(
            sender_pod="Pod 2: Core Engineering",
            sender_agent="AGENT-TECHDIR-014",
            target_pod="Pod 1: Sovereign Orchestration",
            target_recipient="HUMAN-FOUNDER",
            subject="Test Multi-Tier Message",
            t1=Tier1OperatorView(
                summary="System operates at 100% health.",
                business_impact="Zero downtime for customers.",
                action_required="None"
            ),
            t2=Tier2BuilderView(
                flow_summary="Ingest -> Parse -> Validate -> Emit",
                components_involved=["Parser", "Validator", "Emitter"],
                configurations={"timeout_ms": 5000},
                remediation_steps=["Run test suite"]
            ),
            t3=Tier3ArchitectView(
                mathematical_model="Convergence in O(1) time steps.",
                complexity_bounds="Space O(N), Time O(N log N)",
                formal_invariants=["Deterministic state recovery"],
                kernel_metrics={"latency_p99_ms": 1.5}
            ),
            teaching=explain_system_concept("RAG")
        )

    def test_tier_1_rendering(self):
        rendered = self.msg.render("Tier 1: Non-Technical")
        self.assertIn("SUMMARY:", rendered)
        self.assertIn("BUSINESS IMPACT:", rendered)
        self.assertIn("WHAT TO DO NEXT:", rendered)
        self.assertIn("System operates at 100% health.", rendered)

    def test_tier_2_rendering(self):
        rendered = self.msg.render("Tier 2: Intermediate")
        self.assertIn("WORKFLOW & PIPELINE FLOW:", rendered)
        self.assertIn("COMPONENTS INVOLVED:", rendered)
        self.assertIn("Parser, Validator, Emitter", rendered)

    def test_tier_3_rendering(self):
        rendered = self.msg.render("Tier 3: Advanced/PhD")
        self.assertIn("MATHEMATICAL & THEORETICAL FORMALISM:", rendered)
        self.assertIn("ASYMPTOTIC & COMPUTATIONAL COMPLEXITY:", rendered)
        self.assertIn("FORMAL SYSTEM INVARIANTS:", rendered)
        self.assertIn("Space O(N), Time O(N log N)", rendered)

    def test_pod_mesh_broadcast(self):
        broadcast_output = self.router.broadcast(self.msg)
        self.assertEqual(len(broadcast_output), 3)
        self.assertIn("Non-Technical / Executives (Tier 1)", broadcast_output)
        self.assertIn("Developers & Automators (Tier 2)", broadcast_output)
        self.assertIn("Architects & Researchers (Tier 3)", broadcast_output)

    def test_didactic_teacher(self):
        module = explain_system_concept("RAG")
        self.assertEqual(module.concept_name, "Retrieval-Augmented Generation (RAG)")
        self.assertIn("librarian", module.metaphor)


class TestScientificVerificationGate(unittest.TestCase):

    def test_valid_double_checked_claim(self):
        claim = ScientificClaim(
            claim_id="CLAIM-101",
            statement="Vector indexing latency scales logarithmically with HNSW graph depth.",
            citations=[
                VerifiedCitation(
                    ref_id="REF-001",
                    source_title="Efficient and robust approximate nearest neighbor using HNSW",
                    publisher="IEEE TPAMI",
                    date="2020-03-01",
                    url_or_doi="https://doi.org/10.1109/TPAMI.2018.2889473",
                    tier=SourceTier.TIER_2,
                    study_design=StudyDesign.RCT,
                    verbatim_evidence="Search complexity exhibits logarithmic scaling with dataset size."
                ),
                VerifiedCitation(
                    ref_id="REF-002",
                    source_title="Faiss: A library for efficient similarity search",
                    publisher="IEEE Transactions on Big Data",
                    date="2021-02-15",
                    url_or_doi="https://doi.org/10.1109/TBDATA.2019.2921572",
                    tier=SourceTier.TIER_2,
                    study_design=StudyDesign.RCT,
                    verbatim_evidence="HNSW graph traversal maintains bounded search latency."
                )
            ],
            verification_level="Double-Checked",
            status=ClaimStatus.VERIFIED,
            confidence="HIGH",
            is_causal_claim=True,
            story=FindingStory(
                number="Logarithmic search time O(log N)",
                business_logic="Guarantees query response under 10ms at 10M scale",
                market_mechanism="Graph partitioning avoids linear brute-force scan",
                actionable_implication="Configure HNSW indexing across multi-agent vector stores"
            )
        )
        res = claim.validate_gate()
        self.assertTrue(res["gate_passed"])
        self.assertEqual(res["grade_rating"], "HIGH")
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(res["upper_management_approval"], "STAGED_FOR_CEO_APPROVAL")
        self.assertIsNotNone(res["finding_story"])

    def test_prohibited_tier_rejection(self):
        claim = ScientificClaim(
            claim_id="CLAIM-102",
            statement="Unvetted social claim",
            citations=[
                VerifiedCitation(
                    ref_id="REF-003",
                    source_title="Random Reddit Post",
                    publisher="Social Media",
                    date="2026-01-01",
                    url_or_doi="https://reddit.com/r/test",
                    tier=SourceTier.PROHIBITED,
                    verbatim_evidence="trust me bro"
                )
            ],
            verification_level="Single-Checked",
            status=ClaimStatus.VERIFIED,
            confidence="LOW"
        )
        res = claim.validate_gate()
        self.assertFalse(res["gate_passed"])
        self.assertTrue(any("prohibited tier" in err for err in res["errors"]))

    def test_causal_claim_ladder_violation(self):
        claim = ScientificClaim(
            claim_id="CLAIM-103",
            statement="Color blue causes 50% conversion increase.",
            citations=[
                VerifiedCitation(
                    ref_id="REF-004",
                    source_title="Observational Blog Survey",
                    publisher="Blog",
                    date="2026-02-01",
                    url_or_doi="https://example.com/blog",
                    tier=SourceTier.TIER_3,
                    study_design=StudyDesign.OBSERVATIONAL_UNCONTROLLED,
                    verbatim_evidence="We saw higher conversion when blue."
                ),
                VerifiedCitation(
                    ref_id="REF-005",
                    source_title="Second Survey",
                    publisher="Blog 2",
                    date="2026-02-05",
                    url_or_doi="https://example.com/blog2",
                    tier=SourceTier.TIER_3,
                    study_design=StudyDesign.OBSERVATIONAL_UNCONTROLLED,
                    verbatim_evidence="Blue was correlated with sales."
                )
            ],
            verification_level="Double-Checked",
            status=ClaimStatus.VERIFIED,
            confidence="HIGH",
            is_causal_claim=True
        )
        res = claim.validate_gate()
        self.assertFalse(res["gate_passed"])
        self.assertTrue(any("Causal claim made without RCT" in err for err in res["errors"]))


if __name__ == "__main__":
    unittest.main()
