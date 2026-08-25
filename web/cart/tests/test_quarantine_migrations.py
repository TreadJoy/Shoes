from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class QuarantineUnsafeCatalogMigrationTestCase(TransactionTestCase):
    """The cleanup must not trade historical order records for a clean catalog."""

    migrate_from = [
        ("products", "0010_preorderbatch_preordervariantallocation_and_more"),
        ("cart", "0006_cartitem_preorder_batch"),
        ("orders", "0015_order_cart_reconciliation"),
    ]
    migrate_to = [
        ("products", "0011_quarantine_unsafe_test_catalog"),
        ("cart", "0007_remove_quarantined_test_catalog_items"),
        ("orders", "0015_order_cart_reconciliation"),
    ]

    create_known_records = True

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps

        Product = old_apps.get_model("products", "Product")
        ProductVariant = old_apps.get_model("products", "ProductVariant")
        Cart = old_apps.get_model("cart", "Cart")
        CartItem = old_apps.get_model("cart", "CartItem")

        if not self.create_known_records:
            self.executor = MigrationExecutor(connection)
            self.executor.migrate(self.migrate_to)
            return

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
        self.second_variant = ProductVariant.objects.create(
            product=product,
            sku="TJ-QUARANTINE-11",
            size="11",
            color="Black",
            stock_quantity=2,
            is_active=True,
        )
        first_cart = Cart.objects.create(session_key="quarantine-test-session-a")
        second_cart = Cart.objects.create(session_key="quarantine-test-session-b")
        CartItem.objects.create(cart=first_cart, variant=self.variant, quantity=1)
        CartItem.objects.create(
            cart=second_cart,
            variant=self.second_variant,
            quantity=1,
        )

        self.orders = [
            Order.objects.create(full_name="Development Order One"),
            Order.objects.create(full_name="Development Order Two"),
            Order.objects.create(
                full_name="Paid Development Order",
                status="paid",
                grand_total=Decimal("90.00"),
            ),
        ]
        self.order_item_ids = []
        for index, order in enumerate(self.orders):
            item = OrderItem.objects.create(
                order=order,
                product=product,
                variant=self.variant,
                product_name="TreadJoy Test Shoe",
                sku=self.variant.sku,
                unit_price=Decimal("90.00"),
                quantity=1,
                line_total=Decimal("90.00"),
            )
            self.order_item_ids.append(item.pk)

        Payment = old_apps.get_model("orders", "Payment")
        self.paid_payment_id = Payment.objects.create(
            order=self.orders[-1],
            stripe_payment_intent_id="pi_quarantine_paid_order",
            amount=Decimal("90.00"),
            currency="usd",
            status="succeeded",
        ).pk

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)

    def tearDown(self):
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.executor.loader.graph.leaf_nodes())
        super().tearDown()

class QuarantineUnsafeCatalogMigrationTests(
    QuarantineUnsafeCatalogMigrationTestCase
):
    def test_quarantine_hides_both_variants_and_preserves_order_history(self):
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
        Payment = self.executor.loader.project_state(self.migrate_to).apps.get_model(
            "orders", "Payment"
        )

        product = Product.objects.get(slug="treadjoy-test-shoe")
        self.assertFalse(product.is_active)
        self.assertFalse(product.is_featured)
        self.assertEqual(product.image, "")
        self.assertFalse(ProductVariant.objects.get(pk=self.variant.pk).is_active)
        self.assertFalse(
            ProductVariant.objects.get(pk=self.second_variant.pk).is_active
        )
        self.assertFalse(
            CartItem.objects.filter(
                variant_id__in=[self.variant.pk, self.second_variant.pk]
            ).exists()
        )
        self.assertEqual(
            OrderItem.objects.filter(pk__in=self.order_item_ids).count(),
            3,
        )
        self.assertTrue(Payment.objects.filter(pk=self.paid_payment_id).exists())

    def test_reverse_and_reapply_never_restore_quarantined_content(self):
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps
        Product = old_apps.get_model("products", "Product")
        ProductVariant = old_apps.get_model("products", "ProductVariant")
        CartItem = old_apps.get_model("cart", "CartItem")

        product = Product.objects.get(slug="treadjoy-test-shoe")
        self.assertFalse(product.is_active)
        self.assertFalse(product.is_featured)
        self.assertEqual(product.image, "")
        self.assertFalse(ProductVariant.objects.get(pk=self.variant.pk).is_active)
        self.assertFalse(
            ProductVariant.objects.get(pk=self.second_variant.pk).is_active
        )
        self.assertFalse(CartItem.objects.filter(variant_id=self.variant.pk).exists())

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        target_apps = self.executor.loader.project_state(self.migrate_to).apps
        Product = target_apps.get_model("products", "Product")
        ProductVariant = target_apps.get_model("products", "ProductVariant")
        CartItem = target_apps.get_model("cart", "CartItem")

        self.assertFalse(Product.objects.get(slug="treadjoy-test-shoe").is_active)
        self.assertFalse(ProductVariant.objects.get(pk=self.variant.pk).is_active)
        self.assertFalse(
            CartItem.objects.filter(
                variant_id__in=[self.variant.pk, self.second_variant.pk]
            ).exists()
        )


class QuarantineUnsafeCatalogMigrationWithoutRecordsTests(
    QuarantineUnsafeCatalogMigrationTestCase
):
    create_known_records = False

    def test_cleanup_is_a_noop_when_the_known_product_is_absent(self):
        Product = self.executor.loader.project_state(self.migrate_to).apps.get_model(
            "products", "Product"
        )
        CartItem = self.executor.loader.project_state(self.migrate_to).apps.get_model(
            "cart", "CartItem"
        )

        self.assertFalse(Product.objects.filter(slug="treadjoy-test-shoe").exists())
        self.assertEqual(CartItem.objects.count(), 0)
