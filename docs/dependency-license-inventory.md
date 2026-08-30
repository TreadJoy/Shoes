# Dependency License Inventory

Reverified unchanged on 2026-08-30 after clean CPython 3.12 hash-enforced installations using `pip-licenses==5.5.5 --with-system --format=markdown --with-urls`; Phase 6 made no dependency change. The inventory is factual package metadata, not a legal conclusion. No added package reported an unknown or custom license. `psycopg` and `psycopg-binary` report `LGPL-3.0-only`; owner review remains required before A0.3 is accepted.

## Runtime Lock

| Name               | Version     | License                              | URL                                                                  |
|--------------------|-------------|--------------------------------------|----------------------------------------------------------------------|
| Django             | 5.2.17      | BSD-3-Clause                         | https://www.djangoproject.com/                                       |
| asgiref            | 3.12.1      | BSD License                          | https://github.com/django/asgiref/                                   |
| boto3              | 1.43.81     | Apache-2.0                           | https://github.com/boto/boto3                                        |
| botocore           | 1.43.81     | Apache-2.0                           | https://github.com/boto/botocore                                     |
| certifi            | 2026.7.22   | Mozilla Public License 2.0 (MPL 2.0) | https://github.com/certifi/python-certifi                            |
| charset-normalizer | 3.5.1       | MIT                                  | https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md |
| django-allauth     | 65.19.1     | MIT License                          | https://allauth.org                                                  |
| django-storages    | 1.14.6      | BSD License                          | https://github.com/jschneier/django-storages                         |
| holidays           | 0.103       | MIT                                  | https://github.com/vacanza/holidays/                                 |
| idna               | 3.19        | BSD-3-Clause                         | https://github.com/kjd/idna                                          |
| jmespath           | 1.1.0       | MIT License                          | https://github.com/jmespath/jmespath.py                              |
| pillow             | 12.3.0      | MIT-CMU                              | https://python-pillow.github.io                                      |
| psycopg            | 3.3.4       | LGPL-3.0-only                        | https://psycopg.org/                                                 |
| psycopg-binary     | 3.3.4       | LGPL-3.0-only                        | https://psycopg.org/                                                 |
| python-dateutil    | 2.9.0.post0 | Apache Software License; BSD License | https://github.com/dateutil/dateutil                                 |
| python-decouple    | 3.8         | MIT License                          | http://github.com/henriquebastos/python-decouple/                    |
| requests           | 2.34.2      | Apache Software License              | https://github.com/psf/requests                                      |
| s3transfer         | 0.19.2      | Apache Software License              | https://github.com/boto/s3transfer                                   |
| six                | 1.17.0      | MIT License                          | https://github.com/benjaminp/six                                     |
| sqlparse           | 0.6.0       | BSD License                          | https://github.com/andialbrecht/sqlparse                             |
| stripe             | 15.5.1      | MIT License                          | https://stripe.com/                                                  |
| typing_extensions  | 4.16.0      | PSF-2.0                              | https://github.com/python/typing_extensions                          |
| urllib3            | 2.7.0       | MIT                                  | https://github.com/urllib3/urllib3/blob/main/CHANGES.rst             |

## Development Lock

| Name                    | Version     | License                              | URL                                                                  |
|-------------------------|-------------|--------------------------------------|----------------------------------------------------------------------|
| CacheControl            | 0.14.4      | Apache-2.0                           | https://pypi.org/project/CacheControl/                               |
| Django                  | 5.2.17      | BSD-3-Clause                         | https://www.djangoproject.com/                                       |
| PyYAML                  | 6.0.3       | MIT License                          | https://pyyaml.org/                                                  |
| Pygments                | 2.21.0      | BSD-2-Clause                         | https://pygments.org                                                 |
| asgiref                 | 3.12.1      | BSD License                          | https://github.com/django/asgiref/                                   |
| boolean.py              | 5.0         | BSD-2-Clause                         | https://github.com/bastikr/boolean.py                                |
| boto3                   | 1.43.81     | Apache-2.0                           | https://github.com/boto/boto3                                        |
| botocore                | 1.43.81     | Apache-2.0                           | https://github.com/boto/botocore                                     |
| build                   | 1.5.0       | MIT                                  | https://build.pypa.io                                                |
| certifi                 | 2026.7.22   | Mozilla Public License 2.0 (MPL 2.0) | https://github.com/certifi/python-certifi                            |
| cfgv                    | 3.5.0       | MIT                                  | https://github.com/asottile/cfgv                                     |
| charset-normalizer      | 3.5.1       | MIT                                  | https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md |
| click                   | 8.4.2       | BSD-3-Clause                         | https://github.com/pallets/click/                                    |
| cyclonedx-python-lib    | 11.12.0     | Apache Software License              | https://github.com/CycloneDX/cyclonedx-python-lib/#readme            |
| defusedxml              | 0.7.1       | Python Software Foundation License   | https://github.com/tiran/defusedxml                                  |
| distlib                 | 0.4.3       | Python Software Foundation License   | https://github.com/pypa/distlib                                      |
| django-allauth          | 65.19.1     | MIT License                          | https://allauth.org                                                  |
| django-storages         | 1.14.6      | BSD License                          | https://github.com/jschneier/django-storages                         |
| filelock                | 3.32.4      | MIT                                  | https://github.com/tox-dev/py-filelock                               |
| holidays                | 0.103       | MIT                                  | https://github.com/vacanza/holidays/                                 |
| identify                | 2.6.19      | MIT                                  | https://github.com/pre-commit/identify                               |
| idna                    | 3.19        | BSD-3-Clause                         | https://github.com/kjd/idna                                          |
| jmespath                | 1.1.0       | MIT License                          | https://github.com/jmespath/jmespath.py                              |
| license-expression      | 30.4.4      | Apache-2.0                           | https://github.com/aboutcode-org/license-expression                  |
| markdown-it-py          | 4.2.0       | MIT License                          | https://github.com/executablebooks/markdown-it-py                    |
| mdurl                   | 0.1.2       | MIT License                          | https://github.com/executablebooks/mdurl                             |
| msgpack                 | 1.2.1       | Apache-2.0                           | https://msgpack.org/                                                 |
| nodeenv                 | 1.10.0      | BSD License                          | https://github.com/ekalinin/nodeenv                                  |
| packageurl-python       | 0.17.6      | MIT License                          | https://github.com/package-url/packageurl-python                     |
| packaging               | 26.3        | Apache-2.0 OR BSD-2-Clause           | https://github.com/pypa/packaging                                    |
| pillow                  | 12.3.0      | MIT-CMU                              | https://python-pillow.github.io                                      |
| pip                     | 26.2.1      | MIT                                  | https://pip.pypa.io/                                                 |
| pip-api                 | 0.0.34      | Apache Software License              | http://github.com/di/pip-api                                         |
| pip-licenses            | 5.5.5       | MIT                                  | https://github.com/raimon49/pip-licenses                             |
| pip-requirements-parser | 32.0.1      | MIT                                  | https://github.com/nexB/pip-requirements-parser                      |
| pip-tools               | 7.6.1       | BSD License                          | https://github.com/jazzband/pip-tools/                               |
| pip_audit               | 2.10.1      | Apache Software License              | https://pypi.org/project/pip-audit/                                  |
| platformdirs            | 4.11.4      | MIT                                  | https://github.com/tox-dev/platformdirs                              |
| pre_commit              | 4.6.2       | MIT                                  | https://github.com/pre-commit/pre-commit                             |
| prettytable             | 3.18.0      | BSD-3-Clause                         | https://github.com/prettytable/prettytable                           |
| psycopg                 | 3.3.4       | LGPL-3.0-only                        | https://psycopg.org/                                                 |
| psycopg-binary          | 3.3.4       | LGPL-3.0-only                        | https://psycopg.org/                                                 |
| py-serializable         | 2.1.0       | Apache Software License              | https://github.com/madpah/serializable#readme                        |
| pyparsing               | 3.3.2       | MIT                                  | https://github.com/pyparsing/pyparsing/                              |
| pyproject_hooks         | 1.2.0       | MIT License                          | https://github.com/pypa/pyproject-hooks                              |
| python-dateutil         | 2.9.0.post0 | Apache Software License; BSD License | https://github.com/dateutil/dateutil                                 |
| python-decouple         | 3.8         | MIT License                          | http://github.com/henriquebastos/python-decouple/                    |
| python-discovery        | 1.5.3       | MIT License                          | https://github.com/tox-dev/python-discovery                          |
| requests                | 2.34.2      | Apache Software License              | https://github.com/psf/requests                                      |
| rich                    | 15.0.0      | MIT License                          | https://github.com/Textualize/rich                                   |
| s3transfer              | 0.19.2      | Apache Software License              | https://github.com/boto/s3transfer                                   |
| setuptools              | 84.0.0      | MIT                                  | https://github.com/pypa/setuptools                                   |
| six                     | 1.17.0      | MIT License                          | https://github.com/benjaminp/six                                     |
| sortedcontainers        | 2.4.0       | Apache Software License              | http://www.grantjenks.com/docs/sortedcontainers/                     |
| sqlparse                | 0.6.0       | BSD License                          | https://github.com/andialbrecht/sqlparse                             |
| stripe                  | 15.5.1      | MIT License                          | https://stripe.com/                                                  |
| tomli                   | 2.4.1       | MIT                                  | https://github.com/hukkin/tomli                                      |
| tomli_w                 | 1.2.0       | MIT License                          | https://github.com/hukkin/tomli-w                                    |
| typing_extensions       | 4.16.0      | PSF-2.0                              | https://github.com/python/typing_extensions                          |
| urllib3                 | 2.7.0       | MIT                                  | https://github.com/urllib3/urllib3/blob/main/CHANGES.rst             |
| virtualenv              | 21.7.5      | MIT                                  | https://github.com/pypa/virtualenv                                   |
| wcwidth                 | 0.8.2       | MIT                                  | https://github.com/jquast/wcwidth                                    |
| wheel                   | 0.48.0      | MIT                                  | https://github.com/pypa/wheel                                        |
