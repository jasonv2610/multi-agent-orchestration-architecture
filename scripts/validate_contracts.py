"""
validate_contracts.py
---------------------
Validates agent contract YAML files against required schema fields.
Mirrors the pre-commit gate logic in governance/pre-commit-contract-validator.js
for environments where Node.js is unavailable.

Usage:
    python scripts/validate_contracts.py
    python scripts/validate_contracts.py --path examples/redacted-agent-contract.yaml
"""

import argparse
import sys
import yaml
from pathlib import Path

# Required top-level fields for every agent contract
REQUIRED_FIELDS = [
    "agent_id",
    "name",
    "version",
    "status",
    "expected_input_schema",
    "output_schema",
    "failure_modes",
]

# Required subfields within input/output schemas
SCHEMA_REQUIRED = ["type", "required", "properties"]

VALID_STATUSES = {"draft", "review", "production", "deprecated"}


def validate_contract(path: Path) -> list[str]:
    """Validate a single agent contract. Returns a list of violations."""
    violations = []

    try:
        with open(path) as f:
            contract = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(contract, dict):
        return ["Contract root must be a YAML mapping"]

    # Check required top-level fields
    for field in REQUIRED_FIELDS:
        if field not in contract:
            violations.append(f"Missing required field: '{field}'")

    # Validate status enum
    status = contract.get("status")
    if status and status not in VALID_STATUSES:
        violations.append(f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}")

    # Validate input schema structure
    input_schema = contract.get("expected_input_schema", {})
    for subfield in SCHEMA_REQUIRED:
        if subfield not in input_schema:
            violations.append(f"expected_input_schema missing: '{subfield}'")

    # Validate output schema structure
    output_schema = contract.get("output_schema", {})
    for subfield in SCHEMA_REQUIRED:
        if subfield not in output_schema:
            violations.append(f"output_schema missing: '{subfield}'")

    # Validate failure_modes is a non-empty list with code + message
    failure_modes = contract.get("failure_modes", [])
    if not isinstance(failure_modes, list) or len(failure_modes) == 0:
        violations.append("failure_modes must be a non-empty list")
    else:
        for i, fm in enumerate(failure_modes):
            if not isinstance(fm, dict):
                violations.append(f"failure_modes[{i}] must be a mapping")
                continue
            for key in ("code", "message"):
                if key not in fm:
                    violations.append(f"failure_modes[{i}] missing '{key}'")

    return violations


def run(paths: list[Path]) -> bool:
    """Validate all contracts. Returns True if all pass."""
    all_passed = True

    for path in paths:
        violations = validate_contract(path)
        if violations:
            print(f"\n  FAIL  {path}")
            for v in violations:
                print(f"        - {v}")
            all_passed = False
        else:
            print(f"  PASS  {path}")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Validate agent contract YAML files")
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Path to a single contract file (default: scan examples/ and governance/)",
    )
    args = parser.parse_args()

    if args.path:
        paths = [args.path]
    else:
        root = Path(__file__).parent.parent
        paths = sorted(root.glob("**/*.yaml"))
        # Exclude GitHub Actions workflows
        paths = [p for p in paths if ".github" not in p.parts]

    if not paths:
        print("No YAML files found.")
        sys.exit(0)

    print(f"\nValidating {len(paths)} contract(s)...\n")
    passed = run(paths)

    if passed:
        print("\n  All contracts valid.\n")
        sys.exit(0)
    else:
        print(f"\n  Validation failed. Fix violations before committing.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
