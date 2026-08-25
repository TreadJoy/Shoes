import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import stripe
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, SimpleTestCase, TestCase
from django.urls import NoReverseMatch, resolve, reverse

from web.cart.models import Cart, CartItem
from web.orders.models import Order, Payment, ShippingAddress
from web.orders import views as order_views
from web.orders.views import mark_order_as_paid
from web.products.models import Product, ProductVariant


class OrderRouteTests(SimpleTestCase):
    def test_order_list_and_detail_have_one_canonical_route_name(self):
        self.assertEqual(reverse("orders:order_list"), "/orders/")
        self.assertEqual(
            reverse("orders:order_detail", args=[17]),
            "/orders/17/",
        )
        self.assertIs(resolve("/orders/").func, order_views.order_list)
        self.assertIs(
            resolve("/orders/17/").func,
            order_views.order_detail,
        )

        with self.assertRaises(NoReverseMatch):
            reverse("orders:order_history")

    def test_history_compatibility_path_is_unnamed(self):
        match = resolve("/orders/history/")

        self.assertIsNone(match.url_name)
        self.assertEqual(match.route, "orders/history/")


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Checkout Shoe",
            slug="checkout-shoe",
            price=Decimal("99.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-CHECKOUT-090-BLK",
            size="9",
            color="Black",
            stock_quantity=10,
        )
        self.checkout_session = SimpleNamespace(
            id="cs_checkout_flow",
            url="https://checkout.stripe.test/session",
        )

    def checkout_data(self, **overrides):
        data = {
            "full_name": "Checkout Customer",
            "email": "customer@example.com",
            "address_line_1": "100 Test Street",
            "address_line_2": "Suite 2",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
        }
        data.update(overrides)
        return data

    def add_item(self, client=None, quantity=1):
        client = client or self.client
        for _ in range(quantity):
            client.post(
                reverse("cart:add_to_cart"),
                {"variant_id": self.variant.pk},
            )

    def start_checkout(self, client=None, data=None):
        client = client or self.client
        with patch(
            "web.orders.views.stripe.checkout.Session.create",
            return_value=self.checkout_session,
        ) as create:
            response = client.post(
                reverse("orders:checkout"),
                data or self.checkout_data(),
            )
        return response, create

    def test_valid_stocked_checkout_snapshots_order_and_local_address(self):
        self.add_item(quantity=2)

        response, create = self.start_checkout()

        self.assertRedirects(
            response,
            self.checkout_session.url,
            fetch_redirect_response=False,
        )
        order = Order.objects.get()
        item = order.items.get()
        self.assertEqual(order.source_cart, Cart.objects.get())
        self.assertEqual(order.subtotal, Decimal("198.00"))
        self.assertEqual(order.grand_total, Decimal("198.00"))
        self.assertEqual(order.shipping_address.city, "Chicago")
        self.assertEqual(item.product_name, self.product.name)
        self.assertEqual(item.sku, self.variant.sku)
        self.assertEqual(item.unit_price, Decimal("99.00"))
        self.assertEqual(item.quantity, 2)
        self.assertNotIn("shipping_address_collection", create.call_args.kwargs)
        self.assertEqual(
            create.call_args.kwargs["metadata"]["order_id"],
            str(order.pk),
        )

    def test_invalid_email_does_not_create_checkout_records_or_call_stripe(self):
        self.add_item()

        with patch(
            "web.orders.views.stripe.checkout.Session.create",
            return_value=self.checkout_session,
        ) as create:
            response = self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(email="not-an-email"),
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertContains(response, "not-an-email")
        self.assertFalse(Order.objects.exists())
        self.assertFalse(ShippingAddress.objects.exists())
        create.assert_not_called()

    def test_whitespace_only_required_value_is_rejected(self):
        self.add_item()

        with patch(
            "web.orders.views.stripe.checkout.Session.create",
            return_value=self.checkout_session,
        ) as create:
            response = self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(full_name="   "),
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertFalse(Order.objects.exists())
        create.assert_not_called()

    def test_stripe_error_keeps_cart_available_for_retry(self):
        self.add_item()

        with patch(
            "web.orders.views.stripe.checkout.Session.create",
            side_effect=stripe.error.APIConnectionError("offline"),
        ):
            response = self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(),
                follow=True,
            )

        self.assertContains(response, "Payment checkout failed")
        self.assertEqual(CartItem.objects.get().quantity, 1)

    def test_paid_order_reconciles_only_purchased_quantity_without_success_page(self):
        self.add_item()
        self.start_checkout()
        order = Order.objects.get()
        self.add_item()

        mark_order_as_paid(
            order,
            amount_total_cents=9900,
            amount_subtotal_cents=9900,
            payment_intent_id="pi_reconcile",
            checkout_session_id=self.checkout_session.id,
        )

        remaining_item = CartItem.objects.get()
        self.assertEqual(remaining_item.quantity, 1)
        order.refresh_from_db()
        self.assertIsNotNone(order.cart_reconciled_at)

    def test_duplicate_payment_notification_does_not_reconcile_cart_twice(self):
        self.add_item()
        self.start_checkout()
        order = Order.objects.get()
        self.add_item(quantity=2)

        for _ in range(2):
            mark_order_as_paid(
                order,
                amount_total_cents=9900,
                amount_subtotal_cents=9900,
                payment_intent_id="pi_duplicate_reconcile",
                checkout_session_id=self.checkout_session.id,
            )
            order.refresh_from_db()

        self.assertEqual(CartItem.objects.get().quantity, 2)

    def test_signed_checkout_webhook_reconciles_cart_and_inventory(self):
        self.add_item()
        self.start_checkout()
        order = Order.objects.get()
        self.add_item()
        event = {
            "id": "evt_checkout_flow",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": self.checkout_session.id,
                    "payment_intent": "pi_checkout_flow",
                    "amount_subtotal": 9900,
                    "amount_total": 9900,
                    "currency": "usd",
                    "metadata": {"order_id": str(order.pk)},
                },
            },
        }

        with patch(
            "web.orders.views.stripe.Webhook.construct_event",
            return_value=event,
        ):
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(event),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItem.objects.get().quantity, 1)
        order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertIsNotNone(order.cart_reconciled_at)
        self.assertEqual(self.variant.stock_quantity, 9)
        self.assertEqual(Payment.objects.get(order=order).status, "succeeded")


class OrderAccessAndPresentationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner",
            email="owner@example.com",
            password="CorrectHorseBattery9!",
        )
        self.other_user = get_user_model().objects.create_user(
            username="other",
            email="other@example.com",
            password="CorrectHorseBattery9!",
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Order Owner",
            email="owner@example.com",
            subtotal=Decimal("125.00"),
            grand_total=Decimal("125.00"),
        )

    def test_order_detail_requires_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("orders:order_detail", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_canonical_order_list_displays_grand_total_and_item_count(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("orders:order_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "$125.00")
        self.assertContains(response, "<strong>Items:</strong> 0", html=True)

    def test_authenticated_history_url_redirects_to_canonical_order_list(self):
        self.client.force_login(self.user)

        response = self.client.get("/orders/history/")

        self.assertRedirects(response, reverse("orders:order_list"))

    def test_anonymous_history_url_preserves_login_requirement(self):
        response = self.client.get("/orders/history/")

        self.assertRedirects(
            response,
            "/accounts/login/?next=/orders/history/",
            fetch_redirect_response=False,
        )

    def test_order_detail_prefetches_rendered_relations(self):
        self.client.force_login(self.user)

        with patch(
            "web.orders.views.render",
            return_value=HttpResponse(),
        ) as render:
            response = self.client.get(
                reverse("orders:order_detail", args=[self.order.pk])
            )

        self.assertEqual(response.status_code, 200)
        rendered_order = render.call_args.args[2]["order"]
        self.assertEqual(
            set(rendered_order._prefetched_objects_cache),
            {"items", "shipments", "status_events"},
        )

    def test_pending_success_page_emits_refresh_metadata(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["checkout_order_ids"] = [self.order.pk]
        session.save()

        response = self.client.get(
            reverse("orders:order_success", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'http-equiv="refresh"')

    def test_guest_cannot_view_another_session_order(self):
        guest_order = Order.objects.create(
            full_name="Guest",
            email="guest@example.com",
            grand_total=Decimal("25.00"),
        )

        response = Client().get(
            reverse("orders:order_success", args=[guest_order.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_payment_string_uses_order_id(self):
        payment = Payment.objects.create(
            order=self.order,
            stripe_payment_intent_id="pi_string",
            amount=Decimal("125.00"),
            status=Payment.Status.SUCCEEDED,
        )

        self.assertEqual(
            str(payment),
            f"Payment for Order #{self.order.pk} - succeeded",
        )
