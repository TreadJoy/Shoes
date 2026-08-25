from django.db import migrations


TEST_PRODUCT_SLUG = "treadjoy-test-shoe"


def quarantine_unsafe_test_catalog(apps, schema_editor):
    """Remove the known test catalog record from every public launch path.

    The product remains as a protected relation for existing order snapshots;
    it is deliberately not reactivated by a reverse migration.
    """
    Product = apps.get_model("products", "Product")
    ProductVariant = apps.get_model("products", "ProductVariant")

    product_ids = list(
        Product.objects.filter(slug=TEST_PRODUCT_SLUG).values_list("id", flat=True)
    )
    if not product_ids:
        return

    ProductVariant.objects.filter(product_id__in=product_ids).update(
        is_active=False,
    )
    Product.objects.filter(id__in=product_ids).update(
        is_active=False,
        is_featured=False,
        image="",
    )


def keep_quarantined_catalog_hidden(apps, schema_editor):
    """Never restore unsafe public content during a schema rollback."""


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_preorderbatch_preordervariantallocation_and_more"),
    ]

    operations = [
        migrations.RunPython(
            quarantine_unsafe_test_catalog,
            keep_quarantined_catalog_hidden,
        ),
    ]
