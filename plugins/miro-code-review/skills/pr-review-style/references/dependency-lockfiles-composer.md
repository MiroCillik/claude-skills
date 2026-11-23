# PHP: Composer (`composer.json` / `composer.lock`)

Read `dependency-lockfiles.md` (general rules) first.

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
