from django.db import migrations


TEST_PRODUCT_SLUG = "treadjoy-test-shoe"


def remove_quarantined_test_catalog_items(apps, schema_editor):
    CartItem = apps.get_model("cart", "CartItem")
    Product = apps.get_model("products", "Product")
    ProductVariant = apps.get_model("products", "ProductVariant")

    product_ids = Product.objects.filter(
        slug=TEST_PRODUCT_SLUG,
    ).values_list("id", flat=True)
    variant_ids = ProductVariant.objects.filter(
        product_id__in=product_ids,
    ).values_list("id", flat=True)
    CartItem.objects.filter(variant_id__in=variant_ids).delete()


def keep_quarantined_cart_items_removed(apps, schema_editor):
    """Never restore stale test cart lines during a schema rollback."""


class Migration(migrations.Migration):

    dependencies = [
        ("cart", "0006_cartitem_preorder_batch"),
        ("products", "0011_quarantine_unsafe_test_catalog"),
    ]

    operations = [
        migrations.RunPython(
            remove_quarantined_test_catalog_items,
            keep_quarantined_cart_items_removed,
        ),
    ]
