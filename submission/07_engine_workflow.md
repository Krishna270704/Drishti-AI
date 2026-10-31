# Agent Workflow and Process Design

## Sequence
1. Ingestion trigger: project library added to local workspace.
2. Orchestrator creates run ID, inventories files and calls specialist stages.
3. Evidence Agent extracts facts with source filename and excerpt.
4. Timeline Agent orders dated events, decisions and scope changes.
5. KPI Agent validates definitions, baselines, windows and formulas.
6. Privacy Agent detects direct/indirect identifiers and contract restrictions.
7. Case Study Agent drafts Gatekeeper, User and Buyer versions from validated facts.
8. Approval Agent prepares approval pack and blocks publication.
9. Human reviewer resolves conflicts and approves exact text/assets.
10. Release owner records approved version, approver, date and permitted channels.

## Responsibilities and refusal rules
| Agent | Job | Refuse/flag |
|---|---|---|
| Orchestrator | Coordinate stages and preserve status | Failed or missing stage |
| Evidence | Source-backed facts | Untraceable claims |
| Timeline | Chronology and decisions | Unsupported dates/owners |
| KPI | Definitions and calculations | Missing baseline/window or incompatible measures |
| Privacy | Exposure screening | Identifying/restricted details |
| Case Study | Three audience narratives | Unsupported claims or unapproved identity |
| Approval | Permission and release control | Publication without written approval |

## Human gates
A: Project owner validates evidence/timeline. B: KPI owner validates calculations. C: Privacy/legal reviewer approves anonymisation. D: Client Legal and Corporate Communications approve exact wording/assets in writing. E: Internal release owner checks version and channels.

## Exceptions and scaling
Conflicting sources are preserved and escalated. Missing KPI baselines are marked “not established”. Unresolved privacy risks are excluded. No permission means internal draft only. Store run ID, source inventory, evidence, calculations, agent outputs, human edits, approval decisions and released version.

For 50 projects/year: standard folder schema, reusable prompts/config, per-project run IDs, isolated client workspaces, role-based reviewers, versioned outputs and audit logs. Track throughput, review time, traceability, refusal rate and approval turnaround.
