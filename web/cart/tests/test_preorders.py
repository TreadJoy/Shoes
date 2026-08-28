from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest import SkipTest
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

if not settings.IS_COMMERCE_MODE:
    raise SkipTest("Cart and checkout tests require commerce mode.")

from web.cart.models import Cart
from web.orders.models import CheckoutAttempt, Order
from web.orders.services import reconcile_retrieved_checkout_session
from web.products.models import (
    PreorderBatch,
    PreorderVariantAllocation,
    Product,
    ProductVariant,
)


class PreorderCartAndCheckoutTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Launch Preorder Shoe",
            slug="launch-preorder-shoe",
            price=Decimal("100.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-LAUNCH-090-BLK",
            size="9",
            color="Black",
            stock_quantity=20,
        )
        self.batch = PreorderBatch.objects.create(
            code="LAUNCH-2026",
            product=self.product,
            estimated_tender_start=date(2026, 10, 12),
            estimated_tender_end=date(2026, 10, 23),
            total_capacity=10,
        )
        PreorderVariantAllocation.objects.create(
            batch=self.batch,
            variant=self.variant,
            capacity=10,
        )
        self.batch.status = PreorderBatch.Status.OPEN
        self.batch.save()

    def add_preorder(self):
        return self.client.post(
            reverse("cart:add_to_cart"),
            {"variant_id": self.variant.pk},
        )

    def checkout_data(self):
        return {
            "full_name": "Preorder Customer",
            "email": "customer@example.com",
            "address_line_1": "100 Test Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
        }

    def test_product_page_discloses_window_without_exact_capacity(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertContains(response, "Preorder")
        self.assertContains(response, "Oct 12")
        self.assertContains(response, "Oct 23, 2026")
        self.assertNotContains(response, "10 available")

    def test_add_to_cart_stores_preorder_batch(self):
        response = self.add_preorder()

        self.assertEqual(response.status_code, 302)
        item = Cart.objects.get().items.get()
        self.assertEqual(item.preorder_batch, self.batch)

    def test_stocked_and_preorder_items_cannot_mix(self):
        self.add_preorder()
        stocked_product = Product.objects.create(
            name="Stocked Shoe",
            slug="stocked-shoe",
            price=Decimal("90.00"),
        )
        stocked_variant = ProductVariant.objects.create(
            product=stocked_product,
            sku="TJ-STOCK-090-BLK",
            size="9",
            color="Black",
            stock_quantity=2,
        )

        response = self.client.post(
            reverse("cart:add_to_cart"),
            {"variant_id": stocked_variant.pk},
            follow=True,
        )

        self.assertContains(
            response,
            "Stocked products and preorders cannot be purchased together.",
        )
        self.assertEqual(Cart.objects.get().items.count(), 1)

    def test_different_preorder_batches_cannot_mix(self):
        self.add_preorder()
        other_product = Product.objects.create(
            name="Second Preorder Shoe",
            slug="second-preorder-shoe",
            price=Decimal("110.00"),
        )
        other_variant = ProductVariant.objects.create(
            product=other_product,
            sku="TJ-SECOND-090-BLK",
            size="9",
            color="Black",
        )
        other_batch = PreorderBatch.objects.create(
            code="SECOND-2026",
            product=other_product,
            estimated_tender_start=date.today() + timedelta(days=60),
            estimated_tender_end=date.today() + timedelta(days=75),
            total_capacity=2,
        )
        PreorderVariantAllocation.objects.create(
            batch=other_batch,
            variant=other_variant,
            capacity=2,
        )
        other_batch.status = PreorderBatch.Status.OPEN
        other_batch.save()

        response = self.client.post(
            reverse("cart:add_to_cart"),
            {"variant_id": other_variant.pk},
            follow=True,
        )

        self.assertContains(
            response,
            "only one preorder batch",
        )
        self.assertEqual(Cart.objects.get().items.count(), 1)

    def test_combined_sku_quantities_cannot_exceed_batch_capacity(self):
        second_variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-LAUNCH-100-BLK",
            size="10",
            color="Black",
        )
        PreorderVariantAllocation.objects.create(
            batch=self.batch,
            variant=second_variant,
            capacity=10,
        )
        self.batch.total_capacity = 2
        self.batch.save()
        self.add_preorder()
        self.add_preorder()

        response = self.client.post(
            reverse("cart:add_to_cart"),
            {"variant_id": second_variant.pk},
            follow=True,
        )

        self.assertContains(response, "exceed the remaining batch availability")
        self.assertEqual(Cart.objects.get().items.count(), 1)

    def test_paused_batch_cart_cannot_checkout(self):
        self.add_preorder()
        self.batch.status = PreorderBatch.Status.PAUSED
        self.batch.save()

        with patch("web.orders.views.create_stripe_checkout_session") as create:
            response = self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(),
                follow=True,
            )

        self.assertContains(response, "not currently open")
        self.assertFalse(Order.objects.exists())
        create.assert_not_called()

    def test_checkout_snapshots_preorder_promise_before_stripe(self):
        self.add_preorder()
        checkout_session = SimpleNamespace(
            id="cs_preorder_test",
            url="https://checkout.stripe.test/preorder",
        )

        with patch(
            "web.orders.views.create_stripe_checkout_session",
            return_value=checkout_session,
        ) as create:
            response = self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(),
            )

        self.assertRedirects(
            response,
            checkout_session.url,
            fetch_redirect_response=False,
        )
        self.assertFalse(Order.objects.exists())
        attempt = CheckoutAttempt.objects.get()
        quote_line = attempt.quote_lines.get()
        self.assertEqual(
            quote_line.fulfillment_type, Order.FulfillmentType.PREORDER
        )
        self.assertEqual(quote_line.preorder_batch, self.batch)
        self.assertEqual(quote_line.estimated_tender_start, date(2026, 10, 12))
        self.assertEqual(quote_line.preorder_batch_code, "LAUNCH-2026")
        self.assertEqual(quote_line.estimated_tender_end, date(2026, 10, 23))
        stripe_line = create.call_args.kwargs["line_items"][0]
        self.assertIn(
            "estimated to ship",
            stripe_line["price_data"]["product_data"]["description"],
        )

        original_start = quote_line.estimated_tender_start
        original_end = quote_line.estimated_tender_end
        self.batch.estimated_tender_start = date(2026, 11, 2)
        self.batch.estimated_tender_end = date(2026, 11, 13)
        self.batch.save()
        reconcile_retrieved_checkout_session({
            "id": attempt.stripe_checkout_session_id,
            "client_reference_id": str(attempt.id),
            "payment_status": "paid",
            "payment_intent": "pi_preorder_snapshot",
            "mode": "payment",
            "livemode": False,
            "amount_subtotal": 10000,
            "amount_total": 10000,
            "currency": "usd",
            "metadata": {
                "checkout_attempt_id": str(attempt.id),
                "expected_amount": "10000",
                "currency": "usd",
            },
            "shipping_details": {
                "name": "Preorder Customer",
                "address": {
                    "line1": "100 Test Street",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60601",
                    "country": "US",
                },
            },
            "customer_details": {"email": "preorder@example.com"},
        })
        order = Order.objects.get()
        item = order.items.get()
        self.assertEqual(order.estimated_tender_start, original_start)
        self.assertEqual(item.estimated_tender_end, original_end)

        confirmation = self.client.get(
            reverse("orders:checkout_success", args=[attempt.pk])
        )
        self.assertContains(confirmation, "Preorder")
        self.assertContains(confirmation, "Oct 12")
        self.assertNotContains(confirmation, "Nov 2")
