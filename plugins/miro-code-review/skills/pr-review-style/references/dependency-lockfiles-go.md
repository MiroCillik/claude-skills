# Go: Go modules (`go.mod` / `go.sum`)

Read `dependency-lockfiles.md` (general rules) first.

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
