from .models import (
    WAITLIST_SOURCE_HOMEPAGE,
    WAITLIST_SOURCE_PAGE,
    WAITLIST_SOURCE_UNKNOWN,
    WaitlistSignup,
)


def create_waitlist_signup(*, email, first_name="", source=""):
    """Create one signup per normalized email without overwriting attribution."""
    return WaitlistSignup.objects.get_or_create(
        email=email.strip().lower(),
        defaults={
            "first_name": first_name.strip(),
            "source": (
                source.strip()
                if source.strip()
                in {
                    WAITLIST_SOURCE_HOMEPAGE,
                    WAITLIST_SOURCE_PAGE,
                    WAITLIST_SOURCE_UNKNOWN,
                }
                else WAITLIST_SOURCE_UNKNOWN
            ),
        },
    )
