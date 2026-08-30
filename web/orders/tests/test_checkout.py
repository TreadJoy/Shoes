import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch
from threading import Barrier
from unittest import skipUnless

import stripe
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.management import call_command
from django.db import close_old_connections, connection, connections
from django.test import Client, SimpleTestCase, TestCase, TransactionTestCase
from django.urls import NoReverseMatch, resolve, reverse
from django.utils import timezone

from web.cart.models import Cart, CartItem
from web.orders.models import (
    CheckoutAttempt,
    InventoryReservation,
    Order,
    Payment,
    ShippingAddress,
)
from web.orders import views as order_views
from web.orders.services import ReservationError, create_checkout_attempt
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
            "web.orders.views.create_stripe_checkout_session",
            return_value=self.checkout_session,
        ) as create:
            response = client.post(
                reverse("orders:checkout"),
                data or self.checkout_data(),
            )
        return response, create

    def paid_session(self, attempt=None, **overrides):
        attempt = attempt or CheckoutAttempt.objects.get()
        session = {
            "id": attempt.stripe_checkout_session_id,
            "client_reference_id": str(attempt.id),
            "payment_status": "paid",
            "payment_intent": "pi_checkout_flow",
            "mode": "payment",
            "livemode": False,
            "amount_subtotal": int(attempt.subtotal * 100),
            "amount_total": int(attempt.grand_total * 100),
            "currency": attempt.currency,
            "metadata": {
                "checkout_attempt_id": str(attempt.id),
                "expected_amount": str(int(attempt.grand_total * 100)),
                "currency": attempt.currency,
            },
            "shipping_details": {
                "name": "Stripe Customer",
                "address": {
                    "line1": "100 Test Street",
                    "line2": "Suite 2",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60601",
                    "country": "US",
                },
            },
            "customer_details": {"email": "customer@example.com"},
        }
        session.update(overrides)
        return session

    def test_valid_stocked_checkout_defers_full_address_to_stripe(self):
        self.add_item(quantity=2)

        response, create = self.start_checkout()

        self.assertRedirects(
            response,
            self.checkout_session.url,
            fetch_redirect_response=False,
        )
        self.assertFalse(Order.objects.exists())
        self.assertFalse(ShippingAddress.objects.exists())
        attempt = CheckoutAttempt.objects.get()
        item = attempt.quote_lines.get()
        self.assertEqual(attempt.cart, Cart.objects.get())
        self.assertEqual(attempt.subtotal, Decimal("198.00"))
        self.assertEqual(attempt.grand_total, Decimal("198.00"))
        self.assertEqual(item.product_name, self.product.name)
        self.assertEqual(item.sku, self.variant.sku)
        self.assertEqual(item.unit_price, Decimal("99.00"))
        self.assertEqual(item.quantity, 2)
        self.assertEqual(
            create.call_args.kwargs["shipping_address_collection"],
            {"allowed_countries": ["US"]},
        )
        self.assertNotIn("order_id", create.call_args.kwargs["metadata"])
        reservation = InventoryReservation.objects.get(attempt=attempt)
        self.assertEqual(attempt.status, CheckoutAttempt.Status.STRIPE_CREATED)
        self.assertEqual(reservation.quantity, 2)
        self.assertEqual(
            reservation.status,
            InventoryReservation.Status.ACTIVE,
        )

    def test_ambiguous_stripe_failure_keeps_checkout_reservation_for_retry(self):
        self.add_item()

        with patch(
            "web.orders.views.create_stripe_checkout_session",
            side_effect=stripe.error.APIConnectionError("offline"),
        ):
            self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(),
            )

        attempt = CheckoutAttempt.objects.get()
        self.assertEqual(attempt.status, CheckoutAttempt.Status.CREATED)
        self.assertEqual(
            InventoryReservation.objects.get(attempt=attempt).status,
            InventoryReservation.Status.ACTIVE,
        )

    def test_ambiguous_stripe_failure_retries_the_same_attempt_and_key(self):
        self.add_item()
        with patch(
            "web.orders.views.create_stripe_checkout_session",
            side_effect=stripe.error.APIConnectionError("offline"),
        ) as first_create:
            self.client.post(reverse("orders:checkout"), self.checkout_data())
        original_attempt = CheckoutAttempt.objects.get()

        with patch(
            "web.orders.views.create_stripe_checkout_session",
            return_value=self.checkout_session,
        ) as second_create:
            response = self.client.post(
                reverse("orders:checkout"), self.checkout_data()
            )

        self.assertRedirects(
            response,
            self.checkout_session.url,
            fetch_redirect_response=False,
        )
        self.assertEqual(CheckoutAttempt.objects.count(), 1)
        self.assertEqual(
            first_create.call_args.kwargs["idempotency_key"],
            second_create.call_args.kwargs["idempotency_key"],
        )
        original_attempt.refresh_from_db()
        self.assertEqual(
            original_attempt.status, CheckoutAttempt.Status.STRIPE_CREATED
        )

    def test_unpaid_checkout_session_does_not_create_an_order(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()

        result = order_views.reconcile_retrieved_checkout_session(
            self.paid_session(
                attempt,
                payment_status="unpaid",
                payment_intent=None,
            )
        )

        self.assertEqual(result.state, "pending")
        self.assertFalse(Order.objects.exists())
        self.assertEqual(
            InventoryReservation.objects.get(attempt=attempt).status,
            InventoryReservation.Status.ACTIVE,
        )

    def test_amount_mismatch_creates_financial_review_without_inventory_commit(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()

        result = order_views.reconcile_retrieved_checkout_session(
            self.paid_session(attempt, amount_total=10000)
        )

        order = Order.objects.get()
        payment = Payment.objects.get(order=order)
        self.variant.refresh_from_db()
        attempt.refresh_from_db()
        self.assertEqual(result.state, "review_required")
        self.assertEqual(order.status, Order.Status.REVIEW_REQUIRED)
        self.assertEqual(order.grand_total, Decimal("99.00"))
        self.assertEqual(payment.amount, Decimal("100.00"))
        self.assertEqual(self.variant.stock_quantity, 10)
        self.assertEqual(attempt.review_reason, "amount_mismatch")
        self.assertEqual(
            InventoryReservation.objects.get(attempt=attempt).status,
            InventoryReservation.Status.RELEASED,
        )

    def test_currency_mismatch_preserves_expected_quote_and_requires_review(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        session = self.paid_session(attempt, currency="eur")
        session["metadata"]["currency"] = "eur"

        result = order_views.reconcile_retrieved_checkout_session(session)

        order = Order.objects.get()
        self.assertEqual(result.reason, "currency_mismatch")
        self.assertEqual(order.grand_total, Decimal("99.00"))
        self.assertEqual(order.status, Order.Status.REVIEW_REQUIRED)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 10)

    def test_live_mode_session_cannot_reconcile_in_test_mode(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()

        result = order_views.reconcile_retrieved_checkout_session(
            self.paid_session(attempt, livemode=True)
        )

        self.assertEqual(result.reason, "stripe_environment_mismatch")
        self.assertEqual(Order.objects.get().status, Order.Status.REVIEW_REQUIRED)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 10)

    def test_shipping_state_mismatch_is_durable_review_and_not_fulfilled(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        session = self.paid_session(attempt)
        session["shipping_details"]["address"]["state"] = "WI"

        result = order_views.reconcile_retrieved_checkout_session(session)

        order = Order.objects.get()
        self.variant.refresh_from_db()
        self.assertEqual(result.state, "review_required")
        self.assertEqual(order.status, Order.Status.REVIEW_REQUIRED)
        self.assertEqual(order.shipping_address.state, "WI")
        self.assertEqual(order.currency, "usd")
        self.assertEqual(order.shipping_state, "WI")
        self.assertEqual(order.shipping_city, "Chicago")
        self.assertEqual(order.shipping_email, "customer@example.com")
        self.assertEqual(self.variant.stock_quantity, 10)

    def test_replayed_session_cannot_change_the_payment_intent(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        original_session = self.paid_session(attempt)
        order_views.reconcile_retrieved_checkout_session(original_session)

        replay = self.paid_session(attempt, payment_intent="pi_different")
        result = order_views.reconcile_retrieved_checkout_session(replay)

        order = Order.objects.get()
        self.assertEqual(result.reason, "payment_intent_mismatch")
        self.assertEqual(order.status, Order.Status.REVIEW_REQUIRED)
        self.assertEqual(Payment.objects.get().stripe_payment_intent_id, "pi_checkout_flow")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 9)

    def test_paid_session_after_reservation_expiry_requires_review(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        CheckoutAttempt.objects.filter(pk=attempt.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        attempt.refresh_from_db()

        result = order_views.reconcile_retrieved_checkout_session(
            self.paid_session(attempt)
        )

        self.assertEqual(result.state, "review_required")
        self.assertEqual(Order.objects.get().status, Order.Status.REVIEW_REQUIRED)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 10)

    def test_expiry_command_releases_inventory_and_expires_attempt(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        InventoryReservation.objects.filter(attempt=attempt).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )

        output = StringIO()
        call_command("release_expired_reservations", stdout=output)

        attempt.refresh_from_db()
        reservation = InventoryReservation.objects.get(attempt=attempt)
        self.assertEqual(attempt.status, CheckoutAttempt.Status.EXPIRED)
        self.assertEqual(reservation.status, InventoryReservation.Status.RELEASED)
        self.assertIn("Released 1 expired reservation", output.getvalue())

    def test_reconciliation_persists_stripe_address_only_after_paid_state(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        self.assertFalse(Order.objects.exists())
        self.assertFalse(ShippingAddress.objects.exists())
        session = {
            "id": attempt.stripe_checkout_session_id,
            "client_reference_id": str(attempt.id),
            "payment_status": "paid",
            "payment_intent": "pi_strict_reconcile",
            "mode": "payment",
            "livemode": False,
            "amount_subtotal": 9900,
            "amount_total": 9900,
            "currency": "usd",
            "metadata": {
                "checkout_attempt_id": str(attempt.id),
                "expected_amount": "9900",
                "currency": "usd",
            },
            "shipping_details": {
                "name": "Stripe Customer",
                "address": {
                    "line1": "100 Test Street",
                    "line2": "Suite 2",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60601",
                    "country": "US",
                },
            },
            "customer_details": {"email": "customer@example.com"},
        }
        event = {
            "id": "evt_strict_reconcile",
            "type": "checkout.session.completed",
            "data": {"object": session},
        }
        with patch(
            "web.orders.views.stripe.Webhook.construct_event",
            return_value=event,
        ), patch(
            "web.orders.views.retrieve_stripe_checkout_session",
            return_value=session,
        ):
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(event),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(response.status_code, 200)
        order = Order.objects.get()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.shipping_address.state, "IL")

    def test_invalid_email_does_not_create_checkout_records_or_call_stripe(self):
        self.add_item()

        with patch(
            "web.orders.views.create_stripe_checkout_session",
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

    def test_invalid_shipping_state_is_rejected(self):
        self.add_item()

        with patch(
            "web.orders.views.create_stripe_checkout_session",
            return_value=self.checkout_session,
        ) as create:
            response = self.client.post(
                reverse("orders:checkout"),
                self.checkout_data(state="Illinois"),
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ensure this value has at most 2 characters")
        self.assertFalse(Order.objects.exists())
        create.assert_not_called()

    def test_stripe_error_keeps_cart_available_for_retry(self):
        self.add_item()

        with patch(
            "web.orders.views.create_stripe_checkout_session",
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
        attempt = CheckoutAttempt.objects.get()
        self.add_item()

        order_views.reconcile_retrieved_checkout_session(
            self.paid_session(attempt, payment_intent="pi_reconcile")
        )

        remaining_item = CartItem.objects.get()
        self.assertEqual(remaining_item.quantity, 1)
        order = Order.objects.get()
        order.refresh_from_db()
        self.assertIsNotNone(order.cart_reconciled_at)

    def test_duplicate_payment_notification_does_not_reconcile_cart_twice(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        self.add_item(quantity=2)

        for _ in range(2):
            order_views.reconcile_retrieved_checkout_session(
                self.paid_session(
                    attempt,
                    payment_intent="pi_duplicate_reconcile",
                )
            )

        self.assertEqual(CartItem.objects.get().quantity, 2)

    def test_signed_checkout_webhook_reconciles_cart_and_inventory(self):
        self.add_item()
        self.start_checkout()
        attempt = CheckoutAttempt.objects.get()
        self.add_item()
        event = {
            "id": "evt_checkout_flow",
            "type": "checkout.session.completed",
            "data": {
                "object": self.paid_session(attempt),
            },
        }

        with patch(
            "web.orders.views.stripe.Webhook.construct_event",
            return_value=event,
        ), patch(
            "web.orders.views.retrieve_stripe_checkout_session",
            return_value=event["data"]["object"],
        ):
            response = self.client.post(
                reverse("orders:stripe_webhook"),
                data=json.dumps(event),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItem.objects.get().quantity, 1)
        order = Order.objects.get()
        order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertIsNotNone(order.cart_reconciled_at)
        self.assertEqual(self.variant.stock_quantity, 9)
        self.assertEqual(Payment.objects.get(order=order).status, "succeeded")
        self.assertEqual(
            InventoryReservation.objects.get(
                attempt=order.checkout_attempt,
            ).status,
            InventoryReservation.Status.COMMITTED,
        )


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

    def test_pending_success_page_offers_manual_status_check(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["checkout_order_ids"] = [self.order.pk]
        session.save()

        response = self.client.get(
            reverse("orders:order_success", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Check payment status")
        self.assertNotContains(response, 'http-equiv="refresh"')

    def test_guest_cannot_view_another_session_order(self):
        guest_order = Order.objects.create(
            full_name="Guest",
            email="guest@example.com",
            subtotal=Decimal("25.00"),
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


@skipUnless(
    connection.vendor == "postgresql",
    "Requires PostgreSQL row-level locking.",
)
class ConcurrentCheckoutReservationTests(TransactionTestCase):
    def setUp(self):
        product = Product.objects.create(
            name="Last Unit Shoe",
            slug="last-unit-shoe",
            price=Decimal("90.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="TJ-LAST-UNIT",
            size="9",
            color="Black",
            stock_quantity=1,
        )
        self.carts = []
        for index in range(2):
            cart = Cart.objects.create(session_key=f"reservation-{index}")
            CartItem.objects.create(cart=cart, variant=self.variant, quantity=1)
            self.carts.append(cart)

    def reserve(self, cart_id, barrier):
        close_old_connections()
        try:
            cart = Cart.objects.get(pk=cart_id)
            barrier.wait(timeout=5)
            try:
                create_checkout_attempt(
                    cart,
                    user=None,
                    email="customer@example.com",
                    eligibility_state="IL",
                )
            except ReservationError:
                return "rejected"
            return "reserved"
        finally:
            connections.close_all()

    def test_competing_checkouts_cannot_reserve_the_same_last_unit(self):
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(
                    lambda cart: self.reserve(cart.pk, barrier),
                    self.carts,
                )
            )

        self.assertCountEqual(results, ["reserved", "rejected"])
        self.assertEqual(
            InventoryReservation.objects.filter(
                status=InventoryReservation.Status.ACTIVE
            ).count(),
            1,
        )
