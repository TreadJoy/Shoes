from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("cart", "0007_remove_quarantined_test_catalog_items"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.CheckConstraint(
                check=(
                    Q(user__isnull=False, session_key__isnull=True)
                    | (
                        Q(user__isnull=True)
                        & Q(session_key__isnull=False)
                        & ~Q(session_key="")
                    )
                ),
                name="cart_exactly_one_principal",
            ),
        ),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.UniqueConstraint(
                condition=(
                    Q(user__isnull=True)
                    & Q(session_key__isnull=False)
                    & ~Q(session_key="")
                ),
                fields=("session_key",),
                name="unique_guest_cart_session",
            ),
        ),
    ]
