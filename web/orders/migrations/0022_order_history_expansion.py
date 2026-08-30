from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("orders", "0021_checkoutattempt_unique_active_checkout_attempt_per_cart"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="currency",
            field=models.CharField(default="usd", max_length=3),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_full_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_address_line_1",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_address_line_2",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_city",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_state",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_postal_code",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_country",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="orderstatusevent",
            name="actor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="order_status_events",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="orderstatusevent",
            name="source",
            field=models.CharField(
                choices=[
                    ("system", "System"),
                    ("stripe", "Stripe"),
                    ("shipment", "Shipment"),
                    ("refund", "Refund"),
                    ("admin", "Admin"),
                    ("migration", "Migration"),
                    ("legacy", "Legacy"),
                ],
                default="system",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="orderstatusevent",
            name="reason",
            field=models.CharField(default="status_changed", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="orderstatusevent",
            name="external_reference",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="orderstatusevent",
            name="internal_detail",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="orderstatusevent",
            name="customer_message",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="orderstatusevent",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="status_events",
                to="orders.order",
            ),
        ),
    ]
