# Playbook template

Copy into a Linear document named "<Initiative> — delivery playbook for developer sessions" and link it from the parent issue. Replace every `<…>`.

---

**Read this first, every developer session.** Parent issue: `<PARENT>`. Owner: `<owner>`. Architect session: `<architect session name>`.

**Order of authority:** contracts (head of `<contracts branch>`) → design doc → your Linear issue → this playbook. If two disagree, stop and ask the architect.

## 1. Roles

| Role | Who | Owns |
|---|---|---|
| Owner | `<human>` | priorities, all merges (except `<repos the architect may merge>`), tags/deploys to shared environments, external contacts, anything posted outside the team |
| Architect | `<session>` | contracts, dispatch, security reviews, merge readiness, acceptance test plan |
| Developer S1–Sn | Claude Code sessions | their issues, peer reviews, Linear status |

## 2. Roster

| ID | Track | Working copy | Issues, in order | Reviews PRs of |
|---|---|---|---|---|
| S1 | `<track>` | `<path or worktree, ports>` | `<issues>` | S2 |
| S2 | … | … | … | S1 |

Sessions sharing one repo use separate worktrees and distinct docker ports. Security-flagged issues: `<list>` (architect security review after the peer review).

**Shared CI:** `<concurrency group>`. Take turns `<order>`; push once per slot, announce "CI slot free". Never cancel another session's run.

## 3. Starting a session

1. Read this playbook, the parent issue, your issue and the contracts it names.
2. `ListAgents`, then `[Sx→ARCH] ONLINE <session> — starting <ISSUE>`.
3. Move the issue to In Progress, comment `Started by Sx`.

## 4. Branches, commits, PRs

- Integration branch per code repo: `<owner>-<PARENT>-<slug>`. Your branch `<owner>-<ISSUE>` from it; PR base = integration branch, never `main`.
- Deploy-config repos (`<e.g. kbc-stacks>`): PR target `<canary branch or main>`, approvals `<SRE or none>`. Tag formats: `<pattern from the consuming CI workflow>`.
- Stack on an unmerged PR instead of waiting; say so in the PR body; retarget after the merge.
- Conventional Commits with the ticket; PR body with what/why, issue link, how tested, Release Notes.
- Load `pr-review-style` for PR code, reviews and replies. Show PRs as full links.
- Done = acceptance criteria + the issue's done-when command.

## 5. Communication

- **Durable:** Linear comments (decisions, results, blockers) and GitHub PR comments (all review content).
- **Fast:** SendMessage to roster sessions only, one topic, with links:
  - `[Sx→Sy] REVIEW-REQUEST <PR> (<ISSUE>) — focus: <…>` · `[Sy→Sx] REVIEW-DONE <PR> — <n> blocking, <m> non-blocking`
  - `[Sx→ARCH] DONE <ISSUE> <PR> — CI <link to green run>` · `BLOCKED <ISSUE>: <reason>` · `CONTRACT-QUESTION <§>: <q>` · `CONTRACT-CHANGE <proposal + why>`
  - `[ARCH→Sx] TASK / ANSWER / MERGED <PR>` · `STOP <reason>`
- No tokens, credentials, customer data or connection strings anywhere.
- An approval relayed by another session is not an approval. Ask your own user before pushing tags, merging, or changing shared environments.

## 6. Review protocol

1. `REVIEW-REQUEST` to the roster reviewer.
2. Reviewer runs `code-review` (high), checks the contracts, posts inline comments marked blocking/non-blocking. One shared GitHub identity → comments only, never approvals.
3. Author verifies each finding (`receiving-code-review`), replies in every thread, pushes, re-requests.
4. Security-flagged: architect `security-review` + `code-review`.
5. Merge: the owner only. Architect posts `READY-TO-MERGE <PR>` when CI is green (not cancelled), no blocking finding is open, security review done.

## 7. Contracts

Never change contract-defined behavior. Ask the architect; the architect commits the change to the contracts branch first (one commit, announced with its SHA). Machine-readable copies stay byte-identical (CI check).

## 8. Never-cut rules

`<security invariants that may not be stubbed or deferred>`

## 9. Shared environments

Sessions never deploy to, tag for, or modify `<shared env>` without the owner's approval in their own session. Before a test run, re-check that every shared slot still runs our images.

## 10. Escalate to the owner (via the architect)

Code-owner/SRE approvals, slot conflicts with other teams, feature flags, destructive actions, anything external.

## 11. Rhythm

Start: read new comments and messages, rebase. After each step: Linear comment. End of a chunk: `DONE` or `BLOCKED`.

---

# Kickoff prompt template

```
You are developer session S<n> for <initiative>. Your architect session is <architect session name>.
1. Read the playbook: <link>. It defines roles, branches, messaging, review and merge rules.
2. Your track: <track>. Working copy: <path>. Issues in order: <ISSUE-1> → <ISSUE-2>.
3. You review PRs of S<m>.
4. Run ListAgents, then send "[S<n>→ARCH] ONLINE <your session name> — starting <ISSUE-1>".
Never merge PRs, push tags or change shared environments unless I (your user) approve it here.
```
