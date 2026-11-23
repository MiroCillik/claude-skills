# Python: uv (`pyproject.toml` / `uv.lock`) or plain `requirements.txt`

Read `dependency-lockfiles.md` (general rules) first.

- Respect the toolchain the project already uses. Moving a project to another tool (e.g. from `requirements.txt` to uv) is its own PR, never part of a fix PR.
- Pin a transitive package: add it to `dependencies` in `pyproject.toml` with `uv add "<pkg>>=x.y,<z"` in the repo's constraint style, or use `[tool.uv] constraint-dependencies` if it must not become a direct dependency.
- Update one package, lock only:

  ```bash
  uv lock --upgrade-package <pkg>
  ```

  Use `uv add <pkg>==<ver>` only when the constraint in `pyproject.toml` must change. Do not run `uv lock --upgrade`, it upgrades everything. Plain `requirements.txt`: change only that one line.
- Tool version: an older uv may refuse the lock or rewrite it; update uv (`uv self update`) instead.
- Diff check: `git diff uv.lock | grep -E '^[-+](name|version) = '` should show only the target package (and packages it pulls in).
- Verify:
  1. `uv lock --check` (fails if the lock is stale), then `uv sync --frozen`.
  2. The project's linter and type checker through `uv run --frozen` (e.g. `ruff check`, `ruff format --check`).
  3. The test suite (`uv run --frozen pytest` or what the project uses).
  4. `uvx pip-audit`.
