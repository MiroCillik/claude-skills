# Reviewing a PR

All comments use the Comment Shape from `SKILL.md`.

## 1. Read the Linear issue first

- Find the linked issue: the ticket ID in the PR title, branch or description, or the Linear link in the PR.
- Read the issue and its comments, then its parent issue (and the parent's parent, if there is one). `get_issue` does not return comments; call `list_comments` too.
- Note what they ask for: scope, expected behavior, constraints, acceptance criteria.

When Linear and the PR description disagree, review against the PR description, but say so in the review body.
```
The PR differs from the Linear issue; I reviewed against the PR description.
- Linear (AJDA-123) asks for X
- the PR does Y
```
If there is no linked issue, review against the PR description and do not mention the missing issue.

## 2. Write the comments

- Start style or naming comments with `nit:`. Missing tests, bugs and behavior changes are never nits.
- Add a code suggestion only when the fix is not obvious.
- A finding that something does not exist (a branch, PR, caller or code path) is the easiest one to get wrong. Before posting it, look up the exact name (`gh api repos/{owner}/{repo}/branches/{name}`: 404 means absent) and search PRs in every state (`gh search prs <ticket-id> --owner keboola`).

## 3. Post the review

**Post the review on GitHub as inline comments. Do not ask for confirmation first.** If the command that started the review decides whether to post (e.g. `/code-review` without `--comment`), follow that command; this skill then sets only how the comments look.
- Pick the review type:
  - `REQUEST_CHANGES`: at least one finding must be fixed before merge.
  - `APPROVE`: no finding blocks the merge (nits and follow-ups do not block).
  - `COMMENT`: you could not finish checking, you only ask questions, or it is your own PR (GitHub allows only `COMMENT` there).
- Anchor each finding to its line in the diff, and check that the line is inside a diff hunk.
- The review body's first line is the verdict, and short praise is welcome there. The bullets hold only what is not inline: what you checked and found correct, findings with no line in the diff, release or merge order, and where the PR description or Linear is out of date. Do not list the inline findings again.
- On a re-review, reply on each thread you opened (fixed with the commit SHA, or what is still open), and post new findings as new inline comments.
