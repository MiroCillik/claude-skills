# Dependency and lock-file changes in a PR

Use when a PR change touches `composer.json`/`composer.lock` (same ideas apply to npm/yarn locks).

## Pinning a transitive dependency

When a lock refresh pulls a transitive package to a major the framework does not test against, add it as a direct requirement in the repo's existing constraint style (e.g. `"symfony/validator": "^6.4|^7.4"`, alphabetical with its siblings), then update only that package:

```bash
composer update <vendor/pkg> --no-install --no-scripts --no-plugins --no-interaction
```

`--no-install` touches only the lock, so it is fast and cannot leave `vendor/` half-written.

## Keep the lock diff minimal

- Use a Composer at least as new as the one that wrote the lock (compare `plugin-api-version` at the bottom of `composer.lock` with `composer --version`). An older Composer rewrites every package entry (drops `published-time`, downgrades `plugin-api-version`) and the diff balloons to hundreds of lines.
- If the local one is older, fetch a current phar into scratch instead of changing the global install: `curl -sSL -o ~/.hermes/cache/scratch/composer.phar https://getcomposer.org/download/latest-stable/composer.phar` and run `php .../composer.phar ...`.
- Check the result: `git diff composer.lock | grep -E '^[-+] +"(name|version)"'` should show only the target package (plus `content-hash`). Expect a few dozen lines, not hundreds.

## Verify before pushing

1. `composer validate --no-check-all --strict` (fails if the lock is stale).
2. `composer install --no-scripts` so `vendor/` matches the lock.
3. phpcs, phpstan, and `APP_ENV=dev php bin/console lint:container` (catches service wiring that breaks with the other package version).
4. `composer audit --locked` on the change and on the base (`git stash`); report only advisories the change introduces.
5. PHPUnit suites needing MySQL run in CI; check CI on the new head after pushing (`git ls-remote` confirms the push; `gh pr view` can lag a minute).
