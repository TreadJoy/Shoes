from django.db import migrations, models
from django.db.models.functions import Lower


SOURCE_VALUES = {"homepage", "waitlist_page", "unknown"}


def normalize_and_dedupe(apps, schema_editor):
    WaitlistSignup = apps.get_model("waitlist", "WaitlistSignup")
    rows = list(WaitlistSignup.objects.order_by("created_at", "pk"))
    seen = {}

    for row in rows:
        normalized_email = (row.email or "").strip().lower()
        row.email = normalized_email
        row.first_name = (row.first_name or "").strip()
        if row.source not in SOURCE_VALUES:
            row.source = "unknown"

        first = seen.get(normalized_email)
        if first is None:
            seen[normalized_email] = row
            row.save(update_fields=["email", "first_name", "source"])
            continue

        if not first.first_name and row.first_name:
            first.first_name = row.first_name
        if first.source == "unknown" and row.source != "unknown":
            first.source = row.source
        first.save(update_fields=["first_name", "source"])
        row.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("waitlist", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(normalize_and_dedupe, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="waitlistsignup",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="waitlistsignup",
            name="source",
            field=models.CharField(
                choices=[
                    ("homepage", "Homepage"),
                    ("waitlist_page", "Waitlist page"),
                    ("unknown", "Unknown"),
                ],
                default="unknown",
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="waitlistsignup",
            constraint=models.UniqueConstraint(
                Lower("email"),
                name="waitlistsignup_email_ci_unique",
            ),
        ),
    ]
