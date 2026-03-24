#!/usr/bin/env node
/**
 * Pre-commit Contract Validator:Structural Example
 *
 * All schema paths, validation library references, and business logic are
 * represented as placeholders. This file illustrates the validation structure
 * and enforcement points only.
 *
 * Install: copy or symlink to .git/hooks/pre-commit and make executable
 *   chmod +x .git/hooks/pre-commit
 *
 * Exits 0 (commit allowed) or 1 (commit blocked)
 *
 * Runs two checks on every modified workflow file:
 *   1. Version bump:modified workflows must carry a version increment
 *   2. Contract compliance:output node structure must conform to declared contract schema
 */

// const Ajv = require('ajv');              // npm: ajv
// const addFormats = require('ajv-formats'); // npm: ajv-formats
// const semver = require('semver');          // npm: semver
// const { execSync } = require('child_process'); // built-in
// const fs = require('fs');                  // built-in
// const path = require('path');              // built-in

const PATHS = {
  workflows:       'examples/scheduling-assistant/workflows',
  contractSchemas: 'examples/scheduling-assistant/specs',
  governance:      'governance',
};

// ─────────────────────────────────────────────
// Step 1:Identify modified workflow files
// ─────────────────────────────────────────────

/**
 * Returns file paths of .json workflow files staged in this commit.
 * Uses git diff --cached --name-only --diff-filter=M internally.
 */
function getStagedWorkflowFiles() {
  // REDACTED: exec('git diff --cached --name-only --diff-filter=M')
  // REDACTED: filter for files matching PATHS.workflows pattern
  // Returns: string[]:relative paths of modified workflow files
}

// ─────────────────────────────────────────────
// Step 2:Version bump check
// ─────────────────────────────────────────────

/**
 * Compares the versionId field in each staged workflow file
 * against the last committed version of the same file.
 *
 * A workflow is considered modified if any node parameter, connection,
 * or settings field changed. Modified workflows without a version increment
 * are blocked.
 *
 * Returns array of violation messages (empty = all pass).
 */
function checkVersionBumps(stagedFiles) {
  const violations = [];

  for (const file of stagedFiles) {
    // REDACTED: read staged version from git index
    //   const stagedVersion = JSON.parse(execSync(`git show :${file}`)).versionId;

    // REDACTED: read committed version from HEAD
    //   const headVersion = JSON.parse(execSync(`git show HEAD:${file}`)).versionId;

    // REDACTED: compare semver:staged must be strictly greater than HEAD
    //   if (!semverGt(stagedVersion, headVersion)) {
    //     violations.push(`${file}: versionId not incremented (${headVersion} → ${stagedVersion})`);
    //   }
  }

  return violations;
}

// ─────────────────────────────────────────────
// Step 3:Contract compliance check
// ─────────────────────────────────────────────

/**
 * Loads the JSON Schema for the agent's declared output contract and validates
 * the response-formatter node's output_fields against it.
 *
 * Validation points:
 *   - All guaranteed output fields are present in the node definition
 *   - No guaranteed output fields have been renamed or removed
 *   - Error shape fields match the declared error_shape contract
 *
 * Returns array of violation messages (empty = all pass).
 */
function checkContractCompliance(stagedFiles) {
  const violations = [];

  for (const file of stagedFiles) {
    // REDACTED: load staged workflow JSON
    //   const workflow = JSON.parse(execSync(`git show :${file}`));

    // REDACTED: resolve agent ID from workflow metadata
    //   const agentId = workflow.metadata?.agent_id;

    // REDACTED: load corresponding contract schema
    //   const schema = loadSchema(`${PATHS.contractSchemas}/${agentId}.contract.schema.json`);

    // REDACTED: find response-formatter node in workflow
    //   const formatterNode = workflow.nodes.find(n => n.type === 'response-formatter');

    // REDACTED: validate node output_fields against schema.output.guaranteed
    //   const result = ajv.validate(schema.output, formatterNode.parameters.output_fields);
    //   if (!result) {
    //     violations.push(`${file}: contract violation:${ajv.errorsText()}`);
    //   }
  }

  return violations;
}

// ─────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────

function main() {
  const staged = getStagedWorkflowFiles();

  if (!staged || staged.length === 0) {
    // No workflow files in this commit:nothing to validate
    process.exit(0);
  }

  const versionViolations  = checkVersionBumps(staged);
  const contractViolations = checkContractCompliance(staged);

  const allViolations = [...versionViolations, ...contractViolations];

  if (allViolations.length > 0) {
    console.error('\n[pre-commit] BLOCKED:resolve the following before committing:\n');
    allViolations.forEach(v => console.error(`  ✗  ${v}`));
    console.error('\n');
    process.exit(1);
  }

  console.log('[pre-commit] All contract and version checks passed.');
  process.exit(0);
}

main();
