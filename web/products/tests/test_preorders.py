from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.urls import reverse

from web.products.models import (
    PreorderBatch,
    PreorderBatchEvent,
    PreorderVariantAllocation,
    Product,
    ProductVariant,
)
from web.products.services import (
    update_preorder_batch,
    update_preorder_variant_capacity,
    variant_availability,
)


class PreorderBatchDomainTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Preorder Test Shoe",
            slug="preorder-test-shoe",
            price=Decimal("100.00"),
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TJ-PRE-090-BLK",
            size="9",
            color="Black",
            stock_quantity=5,
        )
        self.batch = PreorderBatch.objects.create(
            code="DROP-ONE",
            product=self.product,
            estimated_tender_start=date.today() + timedelta(days=30),
            estimated_tender_end=date.today() + timedelta(days=45),
            total_capacity=10,
        )
        self.allocation = PreorderVariantAllocation.objects.create(
            batch=self.batch,
            variant=self.variant,
            capacity=12,
        )
        self.owner = get_user_model().objects.create_superuser(
            username="preorder-owner",
            email="owner@example.com",
            password="test-password",
        )

    def open_batch(self):
        self.batch.status = PreorderBatch.Status.OPEN
        self.batch.save()
        self.batch.refresh_from_db()

    def test_open_batch_requires_every_active_variant_allocation(self):
        ProductVariant.objects.create(
            product=self.product,
            sku="TJ-PRE-100-BLK",
            size="10",
            color="Black",
        )
        self.batch.status = PreorderBatch.Status.OPEN

        with self.assertRaises(ValidationError):
            self.batch.save()

    def test_total_capacity_cannot_exceed_combined_sku_capacity(self):
        self.batch.total_capacity = 13
        self.batch.status = PreorderBatch.Status.OPEN

        with self.assertRaises(ValidationError):
            self.batch.save()

    def test_only_one_live_batch_per_product(self):
        self.open_batch()
        second_batch = PreorderBatch.objects.create(
            code="DROP-TWO",
            product=self.product,
            estimated_tender_start=date.today() + timedelta(days=60),
            estimated_tender_end=date.today() + timedelta(days=75),
            total_capacity=1,
        )
        PreorderVariantAllocation.objects.create(
            batch=second_batch,
            variant=self.variant,
            capacity=1,
        )
        second_batch.status = PreorderBatch.Status.OPEN
        with self.assertRaises(ValidationError):
            second_batch.save()

    def test_batch_must_be_created_as_draft(self):
        with self.assertRaises(ValidationError):
            PreorderBatch.objects.create(
                code="DROP-DIRECT-OPEN",
                product=self.product,
                status=PreorderBatch.Status.OPEN,
                estimated_tender_start=date.today() + timedelta(days=60),
                estimated_tender_end=date.today() + timedelta(days=75),
                total_capacity=1,
            )

    def test_lifecycle_allows_pause_resume_and_makes_closed_terminal(self):
        self.open_batch()
        self.batch.status = PreorderBatch.Status.PAUSED
        self.batch.save()
        self.batch.status = PreorderBatch.Status.OPEN
        self.batch.save()
        self.batch.status = PreorderBatch.Status.CLOSED
        self.batch.save()
        self.batch.status = PreorderBatch.Status.OPEN

        with self.assertRaises(ValidationError):
            self.batch.save()

    def test_shipping_window_locks_after_confirmed_payment(self):
        self.open_batch()
        PreorderBatch.objects.filter(pk=self.batch.pk).update(
            committed_quantity=1
        )
        self.batch.refresh_from_db()
        self.batch.estimated_tender_end += timedelta(days=1)

        with self.assertRaises(ValidationError):
            self.batch.save()

    def test_safe_capacity_edits_create_append_only_audit(self):
        updated = update_preorder_batch(
            self.batch,
            actor=self.owner,
            reason="Manufacturer approved a larger run.",
            total_capacity=11,
        )
        update_preorder_variant_capacity(
            self.allocation,
            actor=self.owner,
            reason="SKU allocation increased.",
            new_capacity=13,
        )

        self.assertEqual(updated.total_capacity, 11)
        self.assertEqual(
            set(PreorderBatchEvent.objects.values_list("event_type", flat=True)),
            {
                PreorderBatchEvent.EventType.BATCH_CAPACITY_CHANGED,
                PreorderBatchEvent.EventType.SKU_CAPACITY_CHANGED,
            },
        )
        event = PreorderBatchEvent.objects.first()
        event.reason = "Changed after creation"
        with self.assertRaises(ValidationError):
            event.save()

    def test_non_superuser_cannot_change_capacity(self):
        staff = get_user_model().objects.create_user(
            username="employee",
            password="test-password",
            is_staff=True,
        )

        with self.assertRaises(PermissionDenied):
            update_preorder_batch(
                self.batch,
                actor=staff,
                reason="Unauthorized change.",
                total_capacity=11,
            )

    def test_capacity_cannot_fall_below_confirmed_commitments(self):
        PreorderBatch.objects.filter(pk=self.batch.pk).update(
            committed_quantity=3,
        )
        PreorderVariantAllocation.objects.filter(pk=self.allocation.pk).update(
            committed_quantity=3,
        )

        with self.assertRaises(ValidationError):
            update_preorder_batch(
                self.batch,
                actor=self.owner,
                reason="Attempt to reduce the production run.",
                total_capacity=2,
            )
        with self.assertRaises(ValidationError):
            update_preorder_variant_capacity(
                self.allocation,
                actor=self.owner,
                reason="Attempt to reduce the SKU allocation.",
                new_capacity=2,
            )

    def test_preorder_admin_management_requires_superuser(self):
        staff = get_user_model().objects.create_user(
            username="catalog-manager",
            password="test-password",
            is_staff=True,
        )
        add_url = reverse("admin:products_preorderbatch_add")
        change_url = reverse(
            "admin:products_preorderbatch_change",
            args=[self.batch.pk],
        )

        self.client.force_login(staff)
        self.assertEqual(self.client.get(add_url).status_code, 403)
        self.assertEqual(self.client.get(change_url).status_code, 403)

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(add_url).status_code, 200)
        self.assertEqual(self.client.get(change_url).status_code, 200)

    def test_open_batch_replaces_stocked_availability(self):
        self.open_batch()

        availability = variant_availability(self.variant)

        self.assertEqual(availability.fulfillment_type, "preorder")
        self.assertEqual(availability.available_quantity, 10)
