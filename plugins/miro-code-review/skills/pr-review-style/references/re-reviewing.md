# Re-reviewing a PR you already reviewed

Read this together with `reviewing.md`. It adds the steps for a PR where you already left a review.

1. **Check whether anything changed.**
   - Compare the PR commits' dates (`gh api repos/{o}/{r}/pulls/{n}/commits`) with your last review's `submittedAt`.
   - Check each of your threads' `commit_id` against the head SHA (`gh api repos/{o}/{r}/pulls/{n}/comments`).
   - With no new commits, every thread is still open. Say that in one line on each thread; do not re-review from scratch.
2. **Reply on each thread you opened** with `POST .../pulls/{n}/comments/{id}/replies`: fixed (with the SHA) or still open, and say whether it blocks the merge.
3. **Pick the review type again.** Your older `CHANGES_REQUESTED` stays in force until you post `APPROVE` or dismiss it; a later `COMMENT` does not lift it. A PR that is stuck at `REVIEW_REQUIRED` with only your `COMMENT` reviews needs a real verdict from you.

## Docs and skills are instructions

Docs, examples and agent skills in a PR are instructions that people and agents will follow. A doc that sends the reader down an unsafe path (wrong backend, a skipped security check, a leaked token) blocks the merge just like a code bug. It is never a nit.
