from .models import WaitlistSignup


def create_waitlist_signup(*, email, first_name="", source=""):
    """Create one signup per normalized email without overwriting attribution."""
    return WaitlistSignup.objects.get_or_create(
        email=email.strip().lower(),
        defaults={
            "first_name": first_name.strip(),
            "source": source.strip(),
        },
    )
