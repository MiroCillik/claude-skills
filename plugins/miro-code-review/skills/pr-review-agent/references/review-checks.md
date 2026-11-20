# Extra checks during a review (step 5)

Run these on top of `reviewing.md` when the PR touches the area named in each heading.

## Anything that issues credentials or tokens, or grants write access

- Check every role against the repo's permission rules (Keboola `permission-checker`, e.g.
  `CanModifyAuthorization`): `readOnly`, `guest`, `share`, `reviewer`, `developer`, admin.
- Check projects with a protected default branch especially: `reviewer`/`developer` must not get
  write access to the repository production deploys from.
- A guard that only blocks `readOnly` is a blocking finding. "Same checks as the old path" proves
  nothing, because the old path can have the same hole.
- If the PR depends on a permission-checker change, read the rule's code on the branch or release
  it pins. A dependency pinned to a branch (`dev-<branch> as X`) blocks the merge.
- A loosened rule the owning team chose on purpose (e.g. no protected-branch mapping because the
  feature isn't supported in those projects yet) is not a blocker. Send @pm one FYI so it becomes
  a condition on the future work that enables the feature there.

## CI actually ran

- Read the check output, not just its color (`gh pr checks`, then the job log or the CI timeline API).
- A check that fails within seconds at the image-build step (e.g. exit code 127 = command not found
  in the pipeline script) means the tests never ran, so test claims in the PR description are unverified.
- "No checks reported on the branch" also means nothing ran.
- Compare with the last green build on main. For a library about to be tagged, a broken pipeline is
  a blocking finding, and the fix is in the pipeline file.
- Tools that kill the test run on any stderr output (e.g. Infection after PHPUnit) turn a passing
  suite red. If the PR adds logging to stderr in tests, that is the cause.

## Shared library fix: state the release scope

- Find the consumers and the version they lock:
  `gh search code '"<org>/<lib>"' --owner keboola --filename composer.json`, then grep each repo's
  `composer.lock` (`gh api "repos/<org>/<r>/contents/composer.lock" --jq .content | base64 -d`).
- If the PR fixes a regression in a released version, list every consumer on that version. Each
  needs its own lock bump, which a plan of "tag the next version" alone misses.

## Changes that drop a fallback or input

- If the PR stops reading an env var, secret or config key that the issue and description don't
  mention, name who breaks on upgrade (e.g. apps that set only the deprecated variable). Ask for it
  in the description and release notes, and send @pm one FYI to accept the break. If a later push
  restores the fallback, send @pm a correction.
