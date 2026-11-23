# Dependency and lock-file changes in a PR

Use when a PR change touches a dependency manifest or lock file. Read the general rules first, then the section for the ecosystem in the PR.

## General rules (any ecosystem)

### Pinning a transitive dependency

When a lock refresh pulls a transitive package to a major the framework does not test against, add it as a direct requirement in the repo's existing constraint style (same operator style, same ordering as its siblings), then update only that package. Each ecosystem section below has the exact command.

### Keep the lock diff minimal

- Update only the target package, never the whole lock, unless the PR is a full refresh on purpose.
- Use a tool version at least as new as the one that wrote the lock. An older tool often rewrites every entry and the diff balloons to hundreds of lines.
- If the local tool is older, get a current one into a scratch directory instead of changing the global install.
- Check the result: the lock diff should show only the target package (plus any hash/checksum line). Expect a few dozen lines, not hundreds.

### Verify before pushing

1. The lock is in sync with the manifest (each section has a check that fails if it is stale).
2. Install from the lock, so local dependencies match it.
3. Run the repo's lint, static analysis and build.
4. Run a security audit on the change and on the base (`git stash`); report only advisories the change introduces.
5. Tests that need services (databases, etc.) run in CI; check CI on the new head after pushing (`git ls-remote` confirms the push; `gh pr view` can lag a minute).

## PHP: Composer (`composer.json` / `composer.lock`)

- Constraint style example: `"symfony/validator": "^6.4|^7.4"`, alphabetical with its siblings.
- Update one package, lock only:

  ```bash
  composer update <vendor/pkg> --no-install --no-scripts --no-plugins --no-interaction
  ```

  `--no-install` touches only the lock, so it is fast and cannot leave `vendor/` half-written.
- Tool version: compare `plugin-api-version` at the bottom of `composer.lock` with `composer --version`. An older Composer drops `published-time` and downgrades `plugin-api-version` on every entry. If yours is older, fetch a current phar into scratch: `curl -sSL -o ~/.hermes/cache/scratch/composer.phar https://getcomposer.org/download/latest-stable/composer.phar` and run `php .../composer.phar ...`.
- Diff check: `git diff composer.lock | grep -E '^[-+] +"(name|version)"'` should show only the target package (plus `content-hash`).
- Verify:
  1. `composer validate --no-check-all --strict` (fails if the lock is stale).
  2. `composer install --no-scripts`.
  3. phpcs, phpstan, and for Symfony apps `APP_ENV=dev php bin/console lint:container` (catches service wiring that breaks with the other package version).
  4. `composer audit --locked`.

## Go: Go modules (`go.mod` / `go.sum`)

- Go has no separate "lock only" mode: `go.mod` holds the exact versions (minimal version selection) and `go.sum` holds checksums.
- Pin a transitive module: `go get <module>@<version>` adds or changes its line in `go.mod`. Go marks it `// indirect` if no package imports it directly; that is fine.
- Update one module: `go get <module>@<version>`, then `go mod tidy`. Do not run `go get -u ./...`, it upgrades everything.
- Tool version: the `go` (and `toolchain`) line in `go.mod` sets the minimum. A newer local Go may bump `toolchain`; drop that change unless the PR is about it.
- Diff check: `git diff go.mod` should show only the target module (and maybe modules it pulls in). `go.sum` changes follow from it and need no review line by line.
- Verify:
  1. `go mod tidy && git diff --exit-code go.mod go.sum` (fails if they are stale), and `go mod verify`.
  2. `go build ./...`.
  3. `go vet ./...` plus the repo's linter (usually `golangci-lint run`).
  4. `govulncheck ./...` (reports only vulnerabilities in code the module really calls).

## Python: uv (`pyproject.toml` / `uv.lock`), legacy `requirements.txt`

- Respect the folder's own toolchain. The standard is uv with `uv.lock` next to `pyproject.toml`. Many older components still use a plain `requirements.txt` with no lock. Moving a component to uv is its own PR, never part of a fix PR.
- Pin a transitive package: add it to `dependencies` in `pyproject.toml` with `uv add "<pkg>>=x.y,<z"` (repo's constraint style), or use `[tool.uv] constraint-dependencies` if it must not become a direct dependency.
- Update one package, lock only:

  ```bash
  uv lock --upgrade-package <pkg>
  ```

  Use `uv add <pkg>==<ver>` only when the constraint in `pyproject.toml` must change. Do not run `uv lock --upgrade`, it upgrades everything. Legacy `requirements.txt`: change only that one line.
- Tool version: `uv.lock` has a `version`/`revision` at the top. An older uv may refuse the lock or rewrite it; update uv (`uv self update`) instead.
- Diff check: `git diff uv.lock | grep -E '^[-+](name|version) = '` should show only the target package (and packages it pulls in).
- Verify:
  1. `uv lock --check` (fails if the lock is stale), then `uv sync --frozen`.
  2. `uv run --frozen ruff check` and `ruff format --check`; `ty check` only if the component already runs it.
  3. `uv run --frozen pytest` (unittest on older components). Legacy components: `docker compose run --rm test`.
  4. Security audit: CI has none; if you want one, `uvx pip-audit` on the change and on the base. In `keboola/components`, `tools/component verify <folder>` runs steps 1–3.

## JavaScript (UI): pnpm (`package.json` / `pnpm-lock.yaml`)

Based on `keboola/ui` (pnpm workspace with `apps/*` and `packages/*`). Its `AGENTS.md` is the source of truth; read it if anything here disagrees.

- Constraint style: follow the repo. Change the `package.json` of the workspace that uses the dependency, not the root. Syncpack keeps the same dependency on the same range across workspaces, so match the range other workspaces already use.
- Pin a transitive package: add it to `overrides` in `pnpm-workspace.yaml`, scoped to the affected major or range only (e.g. `'uuid@9': '^11.1.1'`), with a comment that names the advisory and why. Keep the target within the same major unless the comment explains the cross-major jump.
- Update one package:

  ```bash
  pnpm update <pkg> --filter <workspace> --lockfile-only
  ```

  Do not run `pnpm update` without a package name, it updates everything. When removing a dependency, do not commit what a plain `pnpm install` produces: it churns unrelated lock entries. Trim `pnpm-lock.yaml` to the package's own blocks (`importers`, `packages:`, `snapshots:`).
- Supply-chain gates in `pnpm-workspace.yaml`: `minimumReleaseAge` (versions newer than a day do not resolve) and `trustPolicy: no-downgrade` (a version published with weaker provenance than an earlier one is refused). If resolving fails because of them, do not add an exclude to get around it; wait, or pick an older version. An exclude needs its own justification in review.
- Tool version: use the pnpm from `packageManager` in the root `package.json` (Corepack picks it up). A different pnpm major changes `lockfileVersion` and rewrites the whole lock.
- Diff check: `git diff pnpm-lock.yaml | grep -E '^[-+] +/?<pkg>@'` should show only the target package and its own sub-dependencies.
- Verify:
  1. `pnpm install --frozen-lockfile` (fails if the lock is stale; for a removal it must report the expected `Packages: -N` and leave the file unchanged).
  2. `pnpm deps:check` (Syncpack, singleton deps, `pnpm dedupe --check`; `pnpm deps:fix` fixes) and `pnpm knip:check`.
  3. `pnpm lint`, `pnpm type-check`, `pnpm test`, `pnpm build` (turbo runs only what the change affects).
  4. `pnpm audit --prod` on the change and on the base.
