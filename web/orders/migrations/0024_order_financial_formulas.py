from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0023_backfill_order_history")]

    operations = [
        migrations.AddConstraint(
            model_name="order",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    grand_total=(
                        models.F("subtotal")
                        + models.F("shipping_total")
                        + models.F("tax_total")
                        - models.F("discount_total")
                    )
                ),
                name="order_grand_total_matches_components",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    line_total=models.F("unit_price") * models.F("quantity")
                ),
                name="order_item_line_total_matches_quantity",
            ),
        ),
    ]
