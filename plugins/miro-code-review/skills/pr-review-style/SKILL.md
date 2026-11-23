---
name: pr-review-style
description: Use when writing code for a pull request, reviewing a PR, writing review comments, or addressing and replying to review comments on your own PR
---

# PR Review Style

## Overview

Code and review text should be short and plain, and should explain themselves. Readers are often not native English speakers.

**REQUIRED, by task** (the files are in this skill's directory):
- Reviewing a PR: read `reviewing.md` before you read the diff.
- Re-reviewing a PR you already reviewed: also read `references/re-reviewing.md`.
- Addressing review comments on your PR: read `addressing.md` before you change code or reply.
- Writing PR code: this file is enough.
- PR changes a dependency manifest or lock file (Composer, Go modules, uv/`requirements.txt`, pnpm): also read `references/dependency-lockfiles.md` (general rules + the ecosystem section).

Read the code around a diff in the user's local checkout (`~/Projects/<repo>`; pull main first if it's on a clean main, otherwise fetch and read `origin/main`), not in a fresh temp clone. Use `gh pr diff` for the change itself.

## Code in the PR

**No ticket references in code.** Source files, comments, test names, variable names and TODOs must not contain Linear/Jira IDs (`AJDA-123`), ticket URLs or "see ticket" notes.
- Commit messages, branch names and the PR description still follow git conventions, so ticket IDs are allowed there.

**Comments only when the code cannot say it.** Code should explain itself through names and structure.
- Allowed: *why* something is done in a way that is not obvious (workaround, outside constraint, surprising edge case).
- Allowed: phpstan doc-blocks for array shapes and types.
- Not allowed: comments that repeat what the code does, section dividers, commented-out code, change history ("added for X", "fixed bug").
- Before adding a comment, try a better name or extract a function first.

**Plain language everywhere.** This covers names, comments, log and error messages, and PR text.
- Use common words (`use`, not `utilize`; `check`, not `ascertain`).
- Avoid idioms, slang and clever names.
- Pick the standard term for a concept over a new one.

## Comment Shape

Inline review comments, review bodies and replies all use one shape: **one line** with the point, then **bullets** with the facts. Do not write paragraphs.

```
Null `config` crashes the export.
- `getConfig()` returns null when the row has no `configuration` key
- `export()` calls `$config->get('tables')` without a check
- the result is a TypeError for projects created before the migration
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| `// AJDA-123: handle empty list` | Delete the comment, or keep only the *why* without the ID |
| `// loop over users` above a `foreach ($users ...)` | Delete it |
| A review comment, review body or reply written as paragraphs | One line plus bullets |
