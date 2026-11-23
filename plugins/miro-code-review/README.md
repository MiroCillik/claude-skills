# miro-code-review

The two skills behind **Revi**, Miroslav's PR review bot: one that runs scheduled, unattended GitHub reviews, and one that sets how reviews and review replies are written.

| Skill | Use it for | Works in |
|---|---|---|
| `pr-review-style` | Reviewing a PR, writing review comments, answering review comments on your own PR, writing PR code | Claude Code, Hermes Agent, any agent that loads skills |
| `pr-review-agent` | Running the review queue on a schedule, relaying its results, ad-hoc and backlog reviews | [Hermes Agent](https://hermes-agent.nousresearch.com/docs) (cron + bot profiles) |

`pr-review-agent` drives the process and loads `pr-review-style` for every review, so install both.

## pr-review-style

Short, plain review text for readers who often aren't native English speakers.

- **Comment shape:** one line with the point, then bullets with the facts. No paragraphs.
- **Linear first:** read the linked issue, its comments and its parents before the diff. If Linear and the PR disagree, review against the PR and say so.
- **Verdicts:** `REQUEST_CHANGES` when something must be fixed before merge, `APPROVE` when nothing blocks (nits don't), `COMMENT` when checking isn't done, for questions only, or on your own PR.
- **`nit:`** marks style and naming only. Missing tests, bugs and behavior changes are never nits.
- **Verify "does not exist" findings** (branches, callers, PRs) before posting them.
- **Re-reviews** reply on each earlier thread (fixed in `<sha>` / still open) and post only new findings.
- **PR code:** no ticket IDs in code, comments only when the code can't explain itself.

| File | When it's read |
|---|---|
| `SKILL.md` | Always: code rules, comment shape |
| `reviewing.md` | Before reviewing a PR |
| `references/re-reviewing.md` | Re-reviewing a PR you already reviewed |
| `addressing.md` | Answering review comments on your own PR |
| `references/dependency-lockfiles.md` | PR touches a dependency manifest or lock file: general rules |
| `references/dependency-lockfiles-<manager>.md` | Same, per package manager: `composer`, `go`, `python`, `pnpm` |
| `scripts/collect-comments.sh` | Lists comments on your PR that still need an answer (`gh` + `jq`) |

`addressing.md` refers to `superpowers:receiving-code-review` and `superpowers:test-driven-development` from the [superpowers](https://github.com/obra/superpowers) plugin.

## pr-review-agent

Operates a scheduled reviewer that posts reviews as you, without asking.

**Flow per run**

1. `scripts/pr-review-queue.py` (cron pre-run gate) finds open, non-draft PRs where you or one of `TEAMS` is a requested reviewer, takes up to `MAX_PER_RUN = 3`, and wakes the agent only if there's work. A retry guard allows 2 attempts per head commit.
2. For each queued PR the agent loads `pr-review-style`, reads the PR, the Linear issue tree and the code (read-only `git worktree`, never runs PR code), runs the topic checks in `references/review-checks.md`, re-checks head SHA and review request right before posting, and posts one review with inline comments via `gh api`.
3. It ends with a per-PR run summary (verdict, link, finding count, notes) and lists skipped PRs.

The skill also covers checking what the bot did, verifying relayed cron reports against live GitHub state, ad-hoc and parallel backlog reviews, prompt-injection in PR content (treated as data), and known pitfalls.

**Setup (Hermes Agent)**

1. Create a bot profile (Revi runs as `revi`) and copy both skills into its skills dir, or point `skills.external_dirs` at this plugin's `skills/`.
2. Copy `skills/pr-review-agent/scripts/pr-review-queue.py` into the profile's `scripts/` dir. Edit `ME`, `TEAMS`, `GH` (path to `gh`) and `PROJECTS` (where local clones live).
3. Create the cron job with the script as its gate and both skills attached:

   ```bash
   hermes -p revi cron create "*/30 8-17 * * 1-5" \
     "Review the GitHub PRs listed in the queue JSON above (to_review). Follow the pr-review-agent skill step by step for each PR, using the pr-review-style skill and its reviewing.md for how to review, write comments, pick the verdict and post. Post each review on GitHub without asking. Finish with the run summary format from pr-review-agent." \
     --name "[bot:revi] PR review queue" \
     --script pr-review-queue.py \
     --skill pr-review-agent --skill pr-review-style \
     --deliver bot-chat:revi \
     --timezone Europe/Prague --catch-up off
   ```

   Exact flags can differ between Hermes versions; check `hermes cron create --help`.
4. Requirements: `gh` authenticated as the reviewing account, `jq`, and a Linear connector for the issue lookups.

**Adapting it**

The skill is Revi's live copy, so it names its own setup: the `revi` and `@pm` profiles, the `MiroCillik` account, the `keboola/ajda-swimlane` team, paths under `~/.hermes/profiles/revi/` and Keboola-specific checks (permission-checker roles, Composer consumers). Replace those with yours. The process itself (gate, guard, pre-post checks, verdict rules, summary format) is generic.
