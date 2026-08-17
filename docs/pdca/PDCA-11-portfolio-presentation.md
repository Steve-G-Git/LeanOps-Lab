# PDCA 11: Portfolio Presentation and Architecture

## Summary

Cycle 11 improved how LeanOps-Lab communicates its verified technical work. The server remained powered off and unchanged. The cycle added a current-state architecture document, network and monitoring-flow diagrams, a condition-lifecycle view, role-based README navigation, a concise Lean-to-IT mapping, and a recruiter-facing summary of the eleven completed cycles.

The update also corrected stale eleven-source backup references to the verified fifteen-source scope and moved the planned notification improvement to Cycle 12. Link targets, Mermaid blocks, cycle counts, terminology, current-state claims, and public identifiers were reviewed before publication.

## Plan

### Current condition and problem

After ten technical cycles, the repository contained strong evidence and detailed records, but the main README required a reader to work through a long file list before understanding the system. The architecture, event thresholds, recovery behavior, retention boundary, and relationship between Lean principles and technical controls were distributed across multiple documents.

### Expected result

- Explain the project and current state in approximately two minutes.
- Give readers clear paths to architecture, PDCA records, runbooks, change history, security controls, and evidence.
- Show the network, monitor workflow, and condition lifecycle visually.
- Map Lean principles to specific, verified technical controls.
- Preserve honest lab framing and distinguish completed work from planned work.
- Correct stale counts and roadmap statements without changing server configuration.
- Publish only sanitized, text-based evidence.

### Risks and rollback

- Simplification could overstate what the lab does.
- New navigation could introduce broken links.
- Diagrams could conflict with the detailed PDCA records.
- Repository terminology or cycle numbering could drift.
- Rollback is the Git branch or the pre-Cycle-11 main commit. No VM snapshot is required because the server was not changed.

## Do

### Reorganized the README

The README now begins with current state and role-based navigation, followed by a concise explanation of LeanOps, two architecture diagrams, condition behavior, verified outcomes, repository structure, skills, evidence policy, and planned work.

### Added architecture documentation

`docs/architecture.md` documents:

- the network boundary and independent test point;
- monitoring and evidence component responsibilities;
- the warning, failure, evidence, and recovery lifecycle;
- protected data and 180-day retention boundaries;
- fifteen-source backup and layered recovery;
- direct mappings between Lean objectives and technical controls;
- current limitations and future work.

### Corrected current-state drift

- Replaced two stale eleven-source references with the verified fifteen-source backup scope.
- Moved the previously planned notification improvement from Cycle 11 to Cycle 12.
- Kept snapshot `21-PDCA10-HealthEventProcessingComplete` as the current server recovery point because this cycle is documentation-only.

## Check

### Before and after

| Before | After |
|---|---|
| Detailed work was available but spread across many records | One architecture document connects the major components and controls |
| README navigation was a long file-by-file list | Role-based links direct readers to the right documentation area |
| Lean principles were implied throughout the cycles | Lean principles are mapped directly to verified technical controls |
| Monitoring logic required reading Cycle 10 in detail | The warning, failure, recovery, and pipeline-error behavior is summarized visually and in a table |
| Two security statements retained an obsolete eleven-source count | Current-state documentation consistently uses the verified fifteen-source scope |
| Notification was listed as Cycle 11 | Notification is correctly retained as planned Cycle 12 work |

### Validation

The reusable public validation excerpt is stored at [`../../evidence/sanitized/pdca-11-documentation-validation.txt`](../../evidence/sanitized/pdca-11-documentation-validation.txt).

| Check | Result |
|---|---|
| Internal Markdown link targets | Passed |
| Mermaid block structure | Passed |
| Cycle numbering and completion count | Passed |
| Fifteen-source backup terminology | Passed |
| Warning and failure threshold descriptions | Passed |
| 180-day retention description | Passed |
| Notification described only as future work | Passed |
| Username, credentials, private addressing, fingerprints, and unique identifiers | No unnecessary identifiers published |
| Server configuration or runtime state | Unchanged |

## Act

### Adopted standard

- Keep a short reader path at the beginning of the README.
- Maintain one architecture document as the current-state system view.
- Use diagrams only when they clarify topology, flow, state, or ownership.
- Keep detailed proof in PDCA and evidence records instead of overloading the README.
- Update cycle counts, architecture, change history, security notes, and planned work together when the system changes.
- Audit public documentation for stale quantities and unnecessary identifiers before publishing.

### Next improvement

Cycle 12 can implement a controlled notification path without weakening the current access, monitoring, evidence, backup, or retention controls.
