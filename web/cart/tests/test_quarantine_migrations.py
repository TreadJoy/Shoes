from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class QuarantineUnsafeCatalogMigrationTests(TransactionTestCase):
    """The cleanup must not trade historical order records for a clean catalog."""

    migrate_from = [
        ("products", "0010_preorderbatch_preordervariantallocation_and_more"),
        ("cart", "0006_cartitem_preorder_batch"),
    ]
    migrate_to = [
        ("products", "0011_quarantine_unsafe_test_catalog"),
        ("cart", "0007_remove_quarantined_test_catalog_items"),
    ]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps

        Product = old_apps.get_model("products", "Product")
        ProductVariant = old_apps.get_model("products", "ProductVariant")
        Cart = old_apps.get_model("cart", "Cart")
        CartItem = old_apps.get_model("cart", "CartItem")
        Order = old_apps.get_model("orders", "Order")
        OrderItem = old_apps.get_model("orders", "OrderItem")

        product = Product.objects.create(
            name="TreadJoy Test Shoe",
            slug="treadjoy-test-shoe",
            description="Development-only catalog record.",
            price=Decimal("100.00"),
            sale_price=Decimal("90.00"),
            image="products/development-photo.jpg",
            is_active=True,
            is_featured=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="TJ-QUARANTINE-10",
            size="10",
            color="Black",
            stock_quantity=2,
            is_active=True,
        )
        cart = Cart.objects.create(session_key="quarantine-test-session")
        CartItem.objects.create(cart=cart, variant=self.variant, quantity=1)
        order = Order.objects.create(full_name="Development Order")
        self.order_item = OrderItem.objects.create(
            order=order,
            product=product,
            variant=self.variant,
            product_name="TreadJoy Test Shoe",
            sku=self.variant.sku,
            unit_price=Decimal("90.00"),
            quantity=1,
            line_total=Decimal("90.00"),
        )

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)

    def tearDown(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_quarantine_hides_catalog_and_preserves_order_history(self):
        Product = self.executor.loader.project_state(self.migrate_to).apps.get_model(
            "products", "Product"
        )
        ProductVariant = self.executor.loader.project_state(
            self.migrate_to
        ).apps.get_model("products", "ProductVariant")
        CartItem = self.executor.loader.project_state(self.migrate_to).apps.get_model(
            "cart", "CartItem"
        )
        OrderItem = self.executor.loader.project_state(self.migrate_to).apps.get_model(
            "orders", "OrderItem"
        )

        product = Product.objects.get(slug="treadjoy-test-shoe")
        self.assertFalse(product.is_active)
        self.assertFalse(product.is_featured)
        self.assertEqual(product.image, "")
        self.assertFalse(ProductVariant.objects.get(pk=self.variant.pk).is_active)
        self.assertFalse(CartItem.objects.filter(variant_id=self.variant.pk).exists())
        self.assertTrue(OrderItem.objects.filter(pk=self.order_item.pk).exists())
