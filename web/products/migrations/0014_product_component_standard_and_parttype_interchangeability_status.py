from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0013_product_product_price_nonnegative_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="component_standard",
            field=models.CharField(
                blank=True,
                choices=[
                    ("heritage_court_v1", "Heritage Court v1 (visual BOM)"),
                ],
                db_comment=(
                    "Opt-in component taxonomy for product-level BOM validation. "
                    "Blank products retain their existing component behavior."
                ),
                default="",
                max_length=40,
            ),
        ),
        migrations.AddField(
            model_name="parttype",
            name="interchangeability_status",
            field=models.CharField(
                choices=[("permanent", "Permanent"), ("unverified", "Unverified")],
                db_comment=(
                    "Evidence state for whether this visual component group is "
                    "interchangeable in the physical shoe."
                ),
                default="unverified",
                max_length=15,
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    component_standard__in=("", "heritage_court_v1")
                ),
                name="product_component_standard_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="parttype",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    interchangeability_status__in=("permanent", "unverified")
                ),
                name="part_type_interchangeability_status_valid",
            ),
        ),
    ]
