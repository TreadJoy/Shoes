# Dependency Management

## Runtime policy

TreadJoy targets CPython 3.12. Development and deployment use the latest
security-patched 3.12 micro release available from the selected platform. The
current verification used CPython 3.12.14, the current 3.12 security release
on 2026-08-26. The tracked `.python-version` records the supported minor; it
does not replace a managed origin's runtime selection.

`requirements.in` is the reviewed source of runtime dependencies.
`requirements.txt` is its generated, hash-locked install file. Production
installs only `requirements.txt`; it contains no development tools.

| Direct package | Deployment use | Reason | Constraint | Source / reported license |
| --- | --- | --- | --- | --- |
| Django | Both modes | Server-rendered web application and admin framework. | `>=5.2.12,<5.3` retains the current LTS line. | djangoproject.com / BSD-3-Clause |
| django-allauth | Commerce only | Account workflows, verification, recovery, and login. Research excludes it at startup. | `>=65.18,<66` retains the current major line. | allauth.org / MIT |
| holidays | Commerce | United States business-day calculations for order operations. | `>=0.102,<1` accepts compatible pre-1.0 fixes. | github.com/vacanza/holidays / MIT |
| Pillow | Both modes | Image metadata validation in the release-content check. | `>=12.1.1,<13` retains the current major line. | python-pillow.github.io / MIT-CMU |
| psycopg[binary] | Both modes | PostgreSQL database adapter with reproducible binary wheels. | `>=3.3.4,<4` retains the current major line. | psycopg.org / LGPL-3.0-only, owner review required |
| PyJWT[crypto] | Private research POC | Verifies Cloudflare Access RS256 application tokens, including signature, issuer, audience, lifetime, and owner identity. | `>=2.13,<3` starts at the 2.13 security release and retains the current major line. | pyjwt.readthedocs.io / MIT; `cryptography` extra uses Apache-2.0 OR BSD-3-Clause |
| python-decouple | Both modes | Environment-driven configuration. | `>=3.8,<4` retains its current major line. | github.com/henriquebastos/python-decouple / MIT |
| resend | Research jobs/webhook | Confirmation delivery, contact/segment sync, broadcast send, and signed webhook verification behind a narrow adapter. | `>=2.42,<3` retains the reviewed major line. | github.com/resendlabs/resend-python / MIT |
| stripe | Commerce only | Hosted Checkout and verified Stripe webhook processing. | `>=15.1,<16` retains the current major line. | stripe.com / MIT |
| django-storages[s3] | Public environments | Django storage backend for R2-backed public media; its S3 extra provides boto3. | `>=1.14.6,<2` keeps the reviewed stable major line. | django-storages / BSD-3-Clause |

Mode-specific packages are installed from the same release lock. Research
cannot initialize Stripe/allauth/commerce code; Resend is imported lazily only
inside the research delivery, sync, broadcast, or signed-webhook adapter.

## Development policy

`requirements-dev.in` starts from the runtime inputs and constrains them to the
runtime lock, so `requirements-dev.txt` is a standalone, hash-locked superset
for development and future CI. It adds only:

- `pip-tools` to compile and synchronize locks.
- `pip-audit` to scan locked dependencies for known vulnerabilities.
- `pip-licenses` to produce the auditable license inventory.
- `pre-commit` for the existing secret-scan hook.

Use only the public PyPI simple index over HTTPS. Do not add private or extra
indexes, `--trusted-host`, direct URLs, editable packages, or credentials to
either input or lock file.

## Lock workflow

Create a dedicated CPython 3.12 virtual environment; do not run `pip-sync` in
an unreviewed or shared environment. Bootstrap the pinned compiler, then run:

```sh
python -m pip install "pip-tools==7.6.1"
python -m piptools compile --generate-hashes --strip-extras --no-allow-unsafe --resolver=backtracking --output-file requirements.txt requirements.in
python -m piptools compile --generate-hashes --strip-extras --allow-unsafe --resolver=backtracking --output-file requirements-dev.txt requirements-dev.in
```

The runtime lock keeps pip-tools' default `--no-allow-unsafe` behavior. The
development lock deliberately uses `--allow-unsafe` because pip-tools 7.6.1
depends on `setuptools`; omitting it makes a clean Python 3.12 installation
fail under hash-checking mode. The generated development lock therefore pins
and hashes both `pip` and `setuptools` rather than relying on virtualenv
bootstrap versions.

Install a reviewed lock with `python -m pip install --require-hashes -r
requirements.txt` or `requirements-dev.txt`. For a deliberate dependency
update, change an `.in` constraint or use `--upgrade`, regenerate runtime then
development locks, review the full diff, regenerate the license inventory, run
the audit and test suite, and commit all resulting files together. To roll
back an unsuccessful update, restore the prior reviewed `.in` and lock commits
instead of hand-editing generated files.

## Review gates

Every direct package must retain its documented purpose. `pip-audit
--require-hashes` must report no known vulnerabilities and no suppressions are
permitted. The companion license inventory records resolved distributions;
unknown, custom, or materially restrictive licenses require owner review before
acceptance and are not legal conclusions by themselves.
