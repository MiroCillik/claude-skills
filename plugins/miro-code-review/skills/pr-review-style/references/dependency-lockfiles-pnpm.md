# JavaScript: pnpm (`package.json` / `pnpm-lock.yaml`)

Read `dependency-lockfiles.md` (general rules) first.

- Constraint style: follow the repo. In a workspace, change the `package.json` of the workspace that uses the dependency, not the root, and match the range other workspaces already use for the same package.
- Pin a transitive package: add it to `overrides` (in `pnpm-workspace.yaml` or `pnpm.overrides` in the root `package.json`, wherever the repo keeps them), scoped to the affected version range (e.g. `'<pkg>@<2.1.3': '^2.1.3'`), with a comment that says why. Stay within the same major unless the comment explains the jump.
- Update one package, lock only:

  ```bash
  pnpm update <pkg> --lockfile-only
  ```

  Add `--filter <workspace>` in a workspace. Do not run `pnpm update` without a package name, it updates everything. When removing a dependency, a plain `pnpm install` can churn unrelated lock entries; keep only the removed package's blocks in the diff.
- Supply-chain gates (`minimumReleaseAge`, `trustPolicy`): if resolving fails because of them, do not add an exclude to get around it. Wait or pick an older version; an exclude needs its own justification.
- Tool version: use the pnpm from `packageManager` in the root `package.json` (Corepack picks it up). A different pnpm major changes `lockfileVersion` and rewrites the whole lock.
- Diff check: `git diff pnpm-lock.yaml | grep -E '^[-+] +/?<pkg>@'` should show only the target package and its own sub-dependencies.
- Verify:
  1. `pnpm install --frozen-lockfile` (fails if the lock is stale).
  2. The repo's dependency checks if it has them (e.g. `pnpm dedupe --check`, syncpack, knip).
  3. The repo's lint, type-check, test and build scripts.
  4. `pnpm audit --prod`.
