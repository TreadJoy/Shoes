from dataclasses import dataclass

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import (
    PreorderBatch,
    PreorderBatchEvent,
    PreorderVariantAllocation,
)


STOCKED = "stocked"
PREORDER = "preorder"
HERITAGE_COURT_V1 = "heritage_court_v1"
HERITAGE_COURT_COMPONENTS = (
    (
        "FRONT_SHELL",
        "Front Shell",
        "Visual group identified as the front shell in the current prototype. Attachment and removal mechanics are unverified.",
        "unverified",
    ),
    (
        "BOOTIE_AND_SOLE",
        "Bootie and Sole",
        "The bootie and sole stay together as one visual group, designated permanent in the current prototype.",
        "permanent",
    ),
    (
        "TONGUE",
        "Tongue",
        "Visual group identified as the tongue in the current prototype. Attachment and removal mechanics are unverified.",
        "unverified",
    ),
    (
        "LACES",
        "Laces",
        "Visual group identified as the laces in the current prototype. Interchangeability is unverified.",
        "unverified",
    ),
    (
        "BACK_PANEL",
        "Back Panel",
        "Visual group identified as the back panel in the current prototype. Attachment and removal mechanics are unverified.",
        "unverified",
    ),
    (
        "LOGO_HOLDER",
        "Logo Holder",
        "Visual group identified as the logo holder in the current prototype. Attachment and removal mechanics are unverified.",
        "unverified",
    ),
    (
        "BACK_LOOP",
        "Back Loop",
        "Visual group identified as the back loop in the current prototype. Its function and interchangeability are unverified.",
        "unverified",
    ),
)
HERITAGE_COURT_COMPONENT_CODES = tuple(
    component[0] for component in HERITAGE_COURT_COMPONENTS
)


def component_bom_issues(variant, *, assignments=None):
    """Return field-addressable issues for an opted-in Heritage Court BOM."""
    product = getattr(variant, "product", None)
    if product is None or product.component_standard != HERITAGE_COURT_V1:
        return {}

    if assignments is None:
        assignments = (
            list(
                variant.components.select_related(
                    "part_type",
                    "part_variant__part",
                    "part_variant__compatibility_group",
                )
            )
            if variant.pk
            else []
        )

    expected = {
        code: (display_order, status)
        for display_order, (code, _name, _description, status)
        in enumerate(HERITAGE_COURT_COMPONENTS, start=1)
    }
    by_code = {code: [] for code in expected}
    issues = []

    for assignment in assignments:
        part_type = assignment.part_type
        code = part_type.code
        if code not in expected:
            issues.append(
                f"{code} is a legacy or unexpected type; only the seven "
                "Heritage Court v1 slots are allowed."
            )
            continue
        by_code[code].append(assignment)
        _display_order, expected_status = expected[code]
        if not part_type.is_active:
            issues.append(f"{code} is inactive.")
        if part_type.interchangeability_status != expected_status:
            issues.append(f"{code} has an unsupported evidence state.")

        part_variant = assignment.part_variant
        part = part_variant.part
        if not part.is_active:
            issues.append(f"The part assigned to {code} is inactive.")
        if not part_variant.is_active:
            issues.append(f"The part variant assigned to {code} is inactive.")
        if part.part_type_id != part_type.pk:
            issues.append(f"The part assigned to {code} has a different type.")
        if variant.compatibility_group_id is None:
            issues.append("A compatibility group is required for the shoe variant.")
        elif part_variant.compatibility_group_id != variant.compatibility_group_id:
            issues.append(f"The part variant assigned to {code} is incompatible.")
        if not part_variant.compatibility_group.is_active:
            issues.append(
                f"The compatibility group assigned to {code} is inactive."
            )

    for code in HERITAGE_COURT_COMPONENT_CODES:
        count = len(by_code[code])
        if count == 0:
            issues.append(f"Missing required component slot: {code}.")
        elif count != 1:
            issues.append(f"Component slot {code} must be assigned exactly once.")

    return {"is_active": issues} if issues else {}


def validate_heritage_court_bom(variant):
    """Raise model validation errors unless an opted-in BOM is ready."""
    issues = component_bom_issues(variant).get("is_active", [])
    if issues:
        raise ValidationError({"is_active": issues})


class AvailabilityError(ValueError):
    pass


@dataclass(frozen=True)
class VariantAvailability:
    fulfillment_type: str
    available_quantity: int
    preorder_batch: PreorderBatch | None = None
    preorder_allocation: PreorderVariantAllocation | None = None

    @property
    def is_available(self):
        return self.available_quantity > 0


@dataclass(frozen=True)
class CartAvailability:
    fulfillment_type: str
    preorder_batch: PreorderBatch | None = None


def _require_preorder_superuser(actor):
    if actor is None or not actor.is_superuser:
        raise PermissionDenied(
            "Only a superuser may manage preorder batches."
        )


def live_preorder_batch_for_product(product):
    prefetched = getattr(product, "_live_preorder_batches", None)
    if prefetched is not None:
        return prefetched[0] if prefetched else None
    return (
        PreorderBatch.objects
        .filter(
            product=product,
            status__in=[
                PreorderBatch.Status.OPEN,
                PreorderBatch.Status.PAUSED,
            ],
        )
        .first()
    )


def variant_availability(variant):
    batch = live_preorder_batch_for_product(variant.product)

    if batch is None:
        return VariantAvailability(
            fulfillment_type=STOCKED,
            available_quantity=(
                variant.stock_quantity if variant.is_active else 0
            ),
        )

    prefetched_allocations = getattr(batch, "_prefetched_objects_cache", {}).get(
        "variant_allocations"
    )
    if prefetched_allocations is not None:
        allocation = next(
            (
                candidate
                for candidate in prefetched_allocations
                if candidate.variant_id == variant.id
            ),
            None,
        )
    else:
        allocation = batch.variant_allocations.filter(variant=variant).first()
    available_quantity = 0
    if (
        batch.status == PreorderBatch.Status.OPEN
        and variant.is_active
        and variant.product.is_active
        and allocation is not None
    ):
        available_quantity = min(
            batch.remaining_quantity,
            allocation.remaining_quantity,
        )

    return VariantAvailability(
        fulfillment_type=PREORDER,
        available_quantity=available_quantity,
        preorder_batch=batch,
        preorder_allocation=allocation,
    )


def validate_cart_items_for_checkout(cart_items):
    if not cart_items:
        raise AvailabilityError("Your cart is empty.")

    fulfillment_types = set()
    preorder_batch_ids = set()
    preorder_batch = None
    preorder_total_quantity = 0

    for item in cart_items:
        variant = item.variant
        if variant is None:
            raise AvailabilityError(
                "This cart item does not have a valid size/color option."
            )
        if not variant.is_active or not variant.product.is_active:
            raise AvailabilityError(
                f"{variant.product.name} — {variant.color}, "
                f"Size {variant.size} is no longer available."
            )

        if variant.product.component_standard == HERITAGE_COURT_V1:
            try:
                validate_heritage_court_bom(variant)
            except ValidationError as error:
                raise AvailabilityError(
                    "This product is not ready for purchase."
                ) from error

        availability = variant_availability(variant)
        fulfillment_types.add(availability.fulfillment_type)

        if availability.fulfillment_type == PREORDER:
            current_batch = availability.preorder_batch
            if (
                item.preorder_batch_id is None
                or current_batch is None
                or item.preorder_batch_id != current_batch.id
            ):
                raise AvailabilityError(
                    "A preorder in your cart is no longer current. "
                    "Remove it and select the current offer."
                )
            if current_batch.status != PreorderBatch.Status.OPEN:
                raise AvailabilityError(
                    f"Preorder {current_batch.code} is not currently open."
                )
            preorder_batch_ids.add(current_batch.id)
            preorder_batch = current_batch
            preorder_total_quantity += item.quantity
        elif item.preorder_batch_id is not None:
            raise AvailabilityError(
                "A preorder in your cart has closed. Remove it before checkout."
            )

        if item.quantity > availability.available_quantity:
            if availability.fulfillment_type == PREORDER:
                raise AvailabilityError(
                    f"The selected preorder quantity for {variant.product.name} "
                    "is no longer available."
                )
            raise AvailabilityError(
                f"Only {availability.available_quantity} of "
                f"{variant.product.name} — {variant.color}, "
                f"Size {variant.size} available."
            )

    if len(fulfillment_types) > 1:
        raise AvailabilityError(
            "Stocked products and preorders cannot be purchased together."
        )
    if len(preorder_batch_ids) > 1:
        raise AvailabilityError(
            "Items from different preorder batches cannot be purchased together."
        )
    if (
        preorder_batch is not None
        and preorder_total_quantity > preorder_batch.remaining_quantity
    ):
        raise AvailabilityError(
            "The selected preorder quantities exceed the remaining batch "
            "availability."
        )

    fulfillment_type = fulfillment_types.pop()
    return CartAvailability(
        fulfillment_type=fulfillment_type,
        preorder_batch=preorder_batch,
    )


@transaction.atomic
def update_preorder_batch(
    batch,
    *,
    actor,
    reason,
    status=None,
    total_capacity=None,
):
    _require_preorder_superuser(actor)
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError("A reason is required for preorder changes.")

    locked = PreorderBatch.objects.select_for_update().get(pk=batch.pk)
    previous_status = locked.status
    previous_capacity = locked.total_capacity

    if status is not None:
        locked.status = status
    if total_capacity is not None:
        if total_capacity < locked.committed_quantity:
            raise ValidationError(
                "Total capacity cannot be lower than committed quantity."
            )
        locked.total_capacity = total_capacity

    locked.save()

    if locked.status != previous_status:
        PreorderBatchEvent.objects.create(
            batch=locked,
            event_type=PreorderBatchEvent.EventType.STATUS_CHANGED,
            previous_status=previous_status,
            new_status=locked.status,
            reason=reason,
            actor=actor,
        )
    if locked.total_capacity != previous_capacity:
        PreorderBatchEvent.objects.create(
            batch=locked,
            event_type=PreorderBatchEvent.EventType.BATCH_CAPACITY_CHANGED,
            previous_capacity=previous_capacity,
            new_capacity=locked.total_capacity,
            reason=reason,
            actor=actor,
        )

    return locked


@transaction.atomic
def update_preorder_variant_capacity(
    allocation,
    *,
    new_capacity,
    actor,
    reason,
):
    _require_preorder_superuser(actor)
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError("A reason is required for preorder changes.")

    locked = (
        PreorderVariantAllocation.objects.select_for_update()
        .select_related("batch", "variant")
        .get(pk=allocation.pk)
    )
    if new_capacity < locked.committed_quantity:
        raise ValidationError(
            "SKU capacity cannot be lower than committed quantity."
        )

    previous_capacity = locked.capacity
    locked.capacity = new_capacity
    locked.save()
    locked.batch.full_clean()

    if previous_capacity != new_capacity:
        PreorderBatchEvent.objects.create(
            batch=locked.batch,
            variant_allocation=locked,
            event_type=PreorderBatchEvent.EventType.SKU_CAPACITY_CHANGED,
            previous_capacity=previous_capacity,
            new_capacity=new_capacity,
            reason=reason,
            actor=actor,
        )

    return locked
