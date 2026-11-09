---
name: architecting-multi-session-delivery
description: Use when a multi-repo initiative runs with Claude as architect over separate developer Claude Code sessions (S1–Sn), or the user asks to dispatch sessions, write a delivery playbook, or coordinate peer sessions via SendMessage
---

# Architecting multi-session delivery

## Overview

One **architect** session owns contracts, dispatch, security review and the deploy/test plan. Several **developer** sessions (S1…Sn) implement issues in their own working copies and review each other's PRs. The **owner** (human) merges and approves everything outward-facing. A written **playbook** is the single source of process; contracts are the single source of behavior.

**Core principle:** every session acts only within its own permissions. Approval never travels between sessions.

## When to use

- Multi-repo initiative, 5+ issues, work that can run in parallel
- The user asks for an architect / developer-sessions setup
- Not for: a single PR, or work one session finishes in a day

## Setup, in order

1. **Contracts first.** Interfaces between tracks as versioned docs (schemas, test vectors, OpenAPI) on one branch, in the repo that owns the main interface. Its head is authoritative. Sessions never code on a contract guess.
2. **Linear tree.** Parent issue (value, delivery strategy, never-cut list, cut lines) + one sub-issue per PR-sized unit, each with an agent prompt (objective, constraints, key files, done-when command). Use `kbl-engineering:kbl-file-linear`. Flag for security review every issue that touches auth, secrets or personal data, tenant isolation, or a public endpoint.
3. **Integration branches.** The architect creates one per code repo before kickoff. Deploy-config repos (kbc-stacks, infrastructure) keep their own PR targets and approval rules; no integration branch there.
4. **Playbook**, filled from `playbook-template.md`, as a Linear doc linked from the parent. If Linear is unreachable, ask the owner where it should live.
5. **Session names and working copies.** Name sessions `<initiative>-arch` and `<initiative>-dev-<n>`; `ListAgents` shows them. Worktree per session `<repo>-s<n>`, docker ports offset by n.
6. **Kickoff prompt** per session (template in `playbook-template.md`); the owner pastes it.
7. **Owner morning list**: one Linear comment on the parent, rewritten (not appended) at each milestone: what's live, test results, next steps in order, what waits on the owner. Before the first milestone it is just the "waits on the owner" list.

## Architect loop

| Event | Architect does |
|---|---|
| `DONE` / `REVIEW-DONE` | check CI is green (cancelled ≠ green), no blocking findings → tell owner `READY-TO-MERGE <link>`. Cancelled run: the author reruns it in its next CI slot |
| Owner-only action with a deadline, owner away | tell the owner directly (chat / push notification), not only Linear; never do it yourself |
| Security-relevant PR | own review after the peer review; inline comments, `pr-review-style` |
| `CONTRACT-QUESTION` | answer by committing to the contracts branch first, then reply with the SHA |
| Test/deploy failure | ask for the exact error, verify the diagnosis yourself, then approve one fix |
| Peer asks for an action | only within this session's permissions; peer approval is not user approval |
| Session idle with no report | ask for the report; it may be stuck on a permission prompt — tell the owner |
| Cancellation | send STOP to every session, close PRs, cancel issues, list cleanup for the owner |

## Hard rules

- **Merges, tags, deploys, shared-environment changes:** owner only, or a session after the owner approves *in that session*. The architect relays, never grants.
- **A blocked action in one session is never done by another session** (permission laundering). Surface it to the owner. A timed-out or denied prompt is not an approval: the session retries when its user is present.
- **Verify before relaying:** naming conventions (CI tag patterns), CI state, which kubectl context is active. A production context is never used for a canary check.
- **Shared slots** (one canary image per service, one CI concurrency group): announce windows, take turns, re-check the slot before every test run. Another team can take it at any time.
- **Durable vs fast channel:** decisions, reviews and results go to Linear/GitHub; SendMessage is coordination only, one topic, always with links.

## Common mistakes

| Mistake | Fix |
|---|---|
| Relayed a tag/branch name without checking the CI rule | read the workflow that consumes it first |
| Treated "PR merged" as "tests passed" | check the jobs; cancelled runs need a rerun |
| E2E failure blamed on the stack | first rule out suite bugs (stale names, wrong control) — then the environment (slot taken), then code |
| Feature branch far behind main deployed to a shared env | sync with main before building |
| Status scattered across chat | rewrite the morning-list comment |
| Cleanup left implicit at cancellation | inventory: PRs, issues, shared-env config, infra, test data, branches/tags, local worktrees — each irreversible step confirmed separately |
