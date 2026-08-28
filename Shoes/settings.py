"""Environment-driven Django settings for TreadJoy."""

from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured

from . import environment


BASE_DIR = Path(__file__).resolve().parent.parent

_VALID_TREADJOY_MODES = {"commerce", "research"}
_VALID_ENVIRONMENTS = {"local", "ci", "staging", "production"}
_VALID_INGRESS = {"direct", "cloudflare-locked"}
_VALID_DB_SSLMODES = {"require", "verify-ca", "verify-full"}

TREADJOY_ENVIRONMENT = environment.choice(
    "TREADJOY_ENVIRONMENT", _VALID_ENVIRONMENTS
)
IS_PUBLIC_ENVIRONMENT = TREADJOY_ENVIRONMENT in {"staging", "production"}

if (
    TREADJOY_ENVIRONMENT == "ci"
    and os.environ.get("DJANGO_SETTINGS_MODULE") != "Shoes.ci_settings"
):
    raise ImproperlyConfigured(
        "TREADJOY_ENVIRONMENT='ci' may only be used with Shoes.ci_settings."
    )

TREADJOY_MODE = environment.choice("TREADJOY_MODE", _VALID_TREADJOY_MODES)
IS_COMMERCE_MODE = TREADJOY_MODE == "commerce"

DEBUG = environment.boolean(
    "DJANGO_DEBUG",
    default=True if TREADJOY_ENVIRONMENT in {"local", "ci"} else None,
    required=IS_PUBLIC_ENVIRONMENT,
)
if TREADJOY_ENVIRONMENT in {"local", "ci"} and not DEBUG:
    raise ImproperlyConfigured(
        "DJANGO_DEBUG must be true when TREADJOY_ENVIRONMENT is local or ci."
    )
if IS_PUBLIC_ENVIRONMENT and DEBUG:
    raise ImproperlyConfigured(
        "DJANGO_DEBUG must be false when TREADJOY_ENVIRONMENT is staging or production."
    )

_secret_key = environment.string("SECRET_KEY", required=True)
SECRET_KEY = (
    environment.strong_secret("SECRET_KEY") if IS_PUBLIC_ENVIRONMENT else _secret_key
)
SECRET_KEY_FALLBACKS = environment.csv("SECRET_KEY_FALLBACKS", default="")
if IS_PUBLIC_ENVIRONMENT:
    for index, fallback in enumerate(SECRET_KEY_FALLBACKS):
        if (
            len(fallback) < 50
            or len(set(fallback)) < 5
            or fallback.startswith("django-insecure-")
            or fallback.startswith("replace-with-")
        ):
            raise ImproperlyConfigured(
                f"Invalid configuration for SECRET_KEY_FALLBACKS[{index}]: "
                "must be a generated production-strength secret."
            )

_default_hosts = "localhost,127.0.0.1" if not IS_PUBLIC_ENVIRONMENT else None
_configured_hosts = environment.csv(
    "ALLOWED_HOSTS", default=_default_hosts, required=IS_PUBLIC_ENVIRONMENT
)
ALLOWED_HOSTS = (
    environment.public_hosts(_configured_hosts)
    if IS_PUBLIC_ENVIRONMENT
    else _configured_hosts
)

if IS_PUBLIC_ENVIRONMENT:
    CSRF_TRUSTED_ORIGINS = environment.https_origins(
        environment.csv("CSRF_TRUSTED_ORIGINS", required=True),
        allowed_hosts=ALLOWED_HOSTS,
    )
else:
    CSRF_TRUSTED_ORIGINS = ()

TREADJOY_INGRESS = environment.choice(
    "TREADJOY_INGRESS",
    _VALID_INGRESS,
    default="cloudflare-locked" if IS_PUBLIC_ENVIRONMENT else "direct",
)
if IS_PUBLIC_ENVIRONMENT and TREADJOY_INGRESS != "cloudflare-locked":
    raise ImproperlyConfigured(
        "TREADJOY_INGRESS must be cloudflare-locked in staging and production."
    )
if not IS_PUBLIC_ENVIRONMENT and TREADJOY_INGRESS != "direct":
    raise ImproperlyConfigured(
        "TREADJOY_INGRESS must be direct in local and ci environments."
    )


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "web.core.apps.CoreConfig",
    "web.products",
    "web.survey",
    "web.waitlist",
    "web.accounts",
]
if IS_COMMERCE_MODE:
    INSTALLED_APPS += ["web.cart", "web.orders"]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "Shoes.middleware.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "Shoes.urls"

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "web.core.context_processors.deployment_mode",
]
if IS_COMMERCE_MODE:
    TEMPLATE_CONTEXT_PROCESSORS.append("web.cart.context_processors.cart_summary")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": TEMPLATE_CONTEXT_PROCESSORS},
    }
]

WSGI_APPLICATION = "Shoes.wsgi.application"


_use_bare_runserver_sqlite = (
    TREADJOY_ENVIRONMENT == "local"
    and os.environ.get("TREADJOY_RUNSERVER_DEFAULTS") == "1"
)
if _use_bare_runserver_sqlite:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": environment.string("DB_NAME", required=True),
            "USER": environment.string("DB_USER", required=True),
            "PASSWORD": environment.string("DB_PASSWORD", required=True),
            "HOST": environment.string("DB_HOST", default="127.0.0.1", required=True),
            "PORT": environment.integer("DB_PORT", minimum=1, maximum=65535, default=5432),
        }
    }
if IS_PUBLIC_ENVIRONMENT:
    _db_sslmode = environment.choice("DB_SSLMODE", _VALID_DB_SSLMODES)
    DATABASES["default"]["OPTIONS"] = {"sslmode": _db_sslmode}
    if _db_sslmode in {"verify-ca", "verify-full"}:
        DATABASES["default"]["OPTIONS"]["sslrootcert"] = str(
            environment.absolute_path("DB_SSLROOTCERT")
        )


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if IS_PUBLIC_ENVIRONMENT:
    STATIC_ROOT = environment.absolute_path("STATIC_ROOT")
    _r2_account_id = environment.string("R2_ACCOUNT_ID", required=True)
    _r2_bucket_name = environment.string("R2_BUCKET_NAME", required=True)
    _r2_access_key_id = environment.string("R2_ACCESS_KEY_ID", required=True)
    _r2_secret_access_key = environment.string("R2_SECRET_ACCESS_KEY", required=True)
    _r2_custom_domain = environment.hostname(
        "R2_MEDIA_CUSTOM_DOMAIN",
        environment.string("R2_MEDIA_CUSTOM_DOMAIN", required=True),
        allow_ip_address=False,
    )
    if _r2_custom_domain.endswith(".r2.dev") or _r2_custom_domain.endswith(
        ".r2.cloudflarestorage.com"
    ):
        raise ImproperlyConfigured(
            "Invalid configuration for R2_MEDIA_CUSTOM_DOMAIN: "
            "must be a Cloudflare custom domain, not an R2 development or API domain."
        )

    MEDIA_URL = f"https://{_r2_custom_domain}/media/"
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": _r2_access_key_id,
                "secret_key": _r2_secret_access_key,
                "bucket_name": _r2_bucket_name,
                "endpoint_url": f"https://{_r2_account_id}.r2.cloudflarestorage.com",
                "region_name": "auto",
                "addressing_style": "path",
                "custom_domain": _r2_custom_domain,
                "location": "media",
                "querystring_auth": False,
                "file_overwrite": False,
                "default_acl": None,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


_STRIPE_SETTING_NAMES = (
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
)


def _required_commerce_setting(name: str) -> str:
    return environment.string(name, required=True)


if IS_COMMERCE_MODE:
    STRIPE_SECRET_KEY = _required_commerce_setting("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = _required_commerce_setting("STRIPE_WEBHOOK_SECRET")
else:
    _configured_stripe_settings = {
        name for name in _STRIPE_SETTING_NAMES if environment.string(name, default="")
    }
    _configured_stripe_settings.update(
        name
        for name, value in os.environ.items()
        if name.startswith("STRIPE_") and value.strip()
    )
    if _configured_stripe_settings:
        raise ImproperlyConfigured(
            "Stripe configuration must not be present when TREADJOY_MODE='research': "
            f"{', '.join(sorted(_configured_stripe_settings))}."
        )


if IS_PUBLIC_ENVIRONMENT:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = environment.string("EMAIL_HOST", required=True)
    EMAIL_PORT = environment.integer("EMAIL_PORT", minimum=1, maximum=65535, required=True)
    EMAIL_HOST_USER = environment.string("EMAIL_HOST_USER", required=True)
    EMAIL_HOST_PASSWORD = environment.string("EMAIL_HOST_PASSWORD", required=True)
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 10
    DEFAULT_FROM_EMAIL = environment.email_address("DEFAULT_FROM_EMAIL")
    SERVER_EMAIL = environment.email_address("SERVER_EMAIL")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = "noreply@treadjoy.com"
    SERVER_EMAIL = DEFAULT_FROM_EMAIL


SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"
ACCOUNT_LOGIN_REDIRECT_URL = "core:home"
ACCOUNT_LOGOUT_REDIRECT_URL = "core:home"
ACCOUNT_SIGNUP_REDIRECT_URL = "core:home"
ACCOUNT_LOGIN_METHODS = {"username"}
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_ADAPTER = "web.accounts.adapter.TreadJoyAccountAdapter"

HOMEPAGE_YOUTUBE_VIDEO_ID = environment.string(
    "HOMEPAGE_YOUTUBE_VIDEO_ID", default=""
)
HOMEPAGE_YOUTUBE_TITLE = environment.string("HOMEPAGE_YOUTUBE_TITLE", default="")


SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
USE_X_FORWARDED_HOST = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

_csp_directives = [
    "default-src 'self'",
    "base-uri 'none'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data:",
    "connect-src 'self'",
    "frame-src https://www.youtube-nocookie.com",
]

if IS_PUBLIC_ENVIRONMENT:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = environment.integer(
        "SECURE_HSTS_SECONDS", minimum=3600, maximum=63072000, required=True
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS = environment.boolean(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", required=True
    )
    SECURE_HSTS_PRELOAD = environment.boolean("SECURE_HSTS_PRELOAD", required=True)
    if SECURE_HSTS_PRELOAD and (
        not SECURE_HSTS_INCLUDE_SUBDOMAINS or SECURE_HSTS_SECONDS < 31536000
    ):
        raise ImproperlyConfigured(
            "SECURE_HSTS_PRELOAD requires SECURE_HSTS_INCLUDE_SUBDOMAINS=true "
            "and SECURE_HSTS_SECONDS of at least 31536000."
        )
    SILENCED_SYSTEM_CHECKS = []
    if not SECURE_HSTS_INCLUDE_SUBDOMAINS:
        SILENCED_SYSTEM_CHECKS.append("security.W005")
    if not SECURE_HSTS_PRELOAD:
        SILENCED_SYSTEM_CHECKS.append("security.W021")
    _csp_directives[8] = f"img-src 'self' data: https://{_r2_custom_domain}"
    _csp_directives.append("upgrade-insecure-requests")
else:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False

CONTENT_SECURITY_POLICY = "; ".join(_csp_directives)
