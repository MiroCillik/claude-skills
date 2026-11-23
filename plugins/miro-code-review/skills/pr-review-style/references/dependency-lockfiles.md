# Dependency and lock-file changes in a PR

Use when a PR change touches a dependency manifest or lock file. Read the general rules below, then the file for the package manager in the PR:

- PHP: Composer (`composer.json` / `composer.lock`): `dependency-lockfiles-composer.md`
- Go: Go modules (`go.mod` / `go.sum`): `dependency-lockfiles-go.md`
- Python: uv (`pyproject.toml` / `uv.lock`) or plain `requirements.txt`: `dependency-lockfiles-python.md`
- JavaScript: pnpm (`package.json` / `pnpm-lock.yaml`): `dependency-lockfiles-pnpm.md`

## General rules (any ecosystem)

### Pinning a transitive dependency

When a lock refresh pulls a transitive package to a major the framework does not test against, add it as a direct requirement in the repo's existing constraint style (same operator style, same ordering as its siblings), then update only that package. Each package manager file has the exact command.

### Keep the lock diff minimal

- Update only the target package, never the whole lock, unless the PR is a full refresh on purpose.
- Use a tool version at least as new as the one that wrote the lock. An older tool often rewrites every entry and the diff balloons to hundreds of lines.
- If the local tool is older, get a current one into a scratch directory instead of changing the global install.
- Check the result: the lock diff should show only the target package (plus any hash/checksum line). Expect a few dozen lines, not hundreds.

### Verify before pushing

1. The lock is in sync with the manifest (each package manager file has a check that fails if it is stale).
2. Install from the lock, so local dependencies match it.
3. Run the repo's lint, static analysis and build.
4. Run a security audit on the change and on the base (`git stash`); report only advisories the change introduces.
5. Tests that need services (databases, etc.) run in CI; check CI on the new head after pushing (`git ls-remote` confirms the push; `gh pr view` can lag a minute).
