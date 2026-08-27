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


if __name__ == "__main__":
    unittest.main()
