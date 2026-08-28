from dataclasses import dataclass

from django.db import transaction

from web.products.models import ProductVariant
from web.products.services import PREORDER, variant_availability

from .models import Cart, CartItem


class CartMutationError(ValueError):
    """An expected cart mutation rejection safe to show to the customer."""

    def __init__(self, message, *, product_slug=None):
        super().__init__(message)
        self.product_slug = product_slug


class CartItemNotFound(CartMutationError):
    pass


@dataclass(frozen=True)
class CartMergeResult:
    notices: tuple[str, ...] = ()


def get_or_create_cart(request):
    """Return the cart for exactly one authenticated or guest principal."""
    user = request.user if request.user.is_authenticated else None
    if user is not None:
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    session = getattr(request, "session", None)
    if session is None:
        raise CartMutationError("A session is required for a guest cart.")
    if not session.session_key:
        session.create()

    cart, _ = Cart.objects.get_or_create(
        session_key=session.session_key,
        user=None,
    )
    return cart


def _locked_variant(variant_id):
    try:
        return ProductVariant.objects.select_for_update().select_related(
            "product"
        ).get(id=variant_id, is_active=True)
    except ProductVariant.DoesNotExist as error:
        raise CartMutationError("That product option is no longer available.") from error


def _lock_availability(variant):
    """Lock the finished SKU and any preorder rows before deciding availability."""
    availability = variant_availability(variant)
    if availability.preorder_batch is not None:
        from web.products.models import PreorderBatch, PreorderVariantAllocation

        PreorderBatch.objects.select_for_update().get(
            pk=availability.preorder_batch.pk
        )
        if availability.preorder_allocation is not None:
            PreorderVariantAllocation.objects.select_for_update().get(
                pk=availability.preorder_allocation.pk
            )
        availability = variant_availability(variant)
    return availability


def _locked_cart(cart_id):
    return Cart.objects.select_for_update().get(pk=cart_id)


def _locked_items(cart):
    return list(
        cart.items.select_for_update().select_related(
            "variant",
            "variant__product",
        )
    )


def _ensure_compatible(items, fulfillment_type, preorder_batch):
    if fulfillment_type == PREORDER:
        if any(
            item.preorder_batch_id != preorder_batch.pk
            for item in items
        ):
            raise CartMutationError(
                "Your cart can contain items from only one preorder batch."
            )
    elif any(item.preorder_batch_id is not None for item in items):
        raise CartMutationError(
            "Stocked products and preorders cannot be purchased together."
        )


@transaction.atomic
def add_variant(cart, variant_id):
    cart = _locked_cart(cart.pk)
    variant = _locked_variant(variant_id)
    availability = _lock_availability(variant)
    if not availability.is_available:
        if availability.fulfillment_type == PREORDER:
            raise CartMutationError(
                "That preorder option is not currently available.",
                product_slug=variant.product.slug,
            )
        raise CartMutationError(
            "That size and color is currently out of stock.",
            product_slug=variant.product.slug,
        )

    items = _locked_items(cart)
    _ensure_compatible(items, availability.fulfillment_type, availability.preorder_batch)
    existing = next((item for item in items if item.variant_id == variant.pk), None)
    new_quantity = (existing.quantity if existing else 0) + 1

    if availability.fulfillment_type == PREORDER:
        other_quantity = sum(
            item.quantity
            for item in items
            if item.preorder_batch_id == availability.preorder_batch.pk
            and item.variant_id != variant.pk
        )
        if other_quantity + new_quantity > availability.preorder_batch.remaining_quantity:
            raise CartMutationError(
                "The selected preorder quantities exceed the remaining batch availability."
            )

    if new_quantity > availability.available_quantity:
        if availability.fulfillment_type == PREORDER:
            raise CartMutationError("That preorder quantity is no longer available.")
        raise CartMutationError("You cannot add more than the available inventory.")

    if existing is None:
        CartItem.objects.create(
            cart=cart,
            variant=variant,
            preorder_batch=availability.preorder_batch,
            quantity=1,
        )
    else:
        existing.quantity = new_quantity
        existing.preorder_batch = availability.preorder_batch
        existing.save(update_fields=["quantity", "preorder_batch"])
    return variant.product.name


@transaction.atomic
def update_item(cart, item_id, quantity):
    cart = _locked_cart(cart.pk)
    item = next((item for item in _locked_items(cart) if item.pk == item_id), None)
    if item is None:
        raise CartItemNotFound("That cart item no longer exists.")

    if quantity <= 0:
        product_name = item.variant.product.name
        item.delete()
        return product_name

    item.variant = _locked_variant(item.variant_id)
    availability = _lock_availability(item.variant)
    if item.preorder_batch_id != (
        availability.preorder_batch.pk if availability.preorder_batch else None
    ):
        raise CartMutationError(
            "This cart item is no longer current. Remove it and select the current offer."
        )
    if quantity > availability.available_quantity:
        if availability.fulfillment_type == PREORDER:
            raise CartMutationError(
                f"The selected preorder quantity for {item.variant.product.name} is no longer available."
            )
        raise CartMutationError(
            f"Only {availability.available_quantity} of {item.variant.product.name} - "
            f"{item.variant.color}, Size {item.variant.size} available."
        )

    if availability.fulfillment_type == PREORDER:
        other_quantity = sum(
            other.quantity
            for other in _locked_items(cart)
            if other.pk != item.pk
            and other.preorder_batch_id == availability.preorder_batch.pk
        )
        if other_quantity + quantity > availability.preorder_batch.remaining_quantity:
            raise CartMutationError(
                "The selected preorder quantities exceed the remaining batch availability."
            )

    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item.variant.product.name


@transaction.atomic
def remove_item(cart, item_id):
    cart = _locked_cart(cart.pk)
    item = next((item for item in _locked_items(cart) if item.pk == item_id), None)
    if item is None:
        raise CartItemNotFound("That cart item no longer exists.")
    product_name = item.variant.product.name
    item.delete()
    return product_name


@transaction.atomic
def clear_cart(cart):
    cart = _locked_cart(cart.pk)
    cart.items.select_for_update().all().delete()


@transaction.atomic
def merge_guest_cart(*, user, guest_session_key):
    guest = (
        Cart.objects.filter(user=None, session_key=guest_session_key).first()
    )
    if guest is None:
        return CartMergeResult()

    account, _ = Cart.objects.get_or_create(user=user)
    carts = {
        cart.pk: cart
        for cart in Cart.objects.select_for_update()
        .filter(pk__in=[guest.pk, account.pk])
        .order_by("pk")
    }
    if guest.pk not in carts or account.pk not in carts:
        return CartMergeResult()
    guest = carts[guest.pk]
    account = carts[account.pk]
    account_items = {
        item.variant_id: item
        for item in account.items.select_for_update().select_related(
            "variant",
            "variant__product",
        )
    }
    notices = []

    for guest_item in guest.items.select_for_update().select_related(
        "variant",
        "variant__product",
    ):
        try:
            variant = _locked_variant(guest_item.variant_id)
        except CartMutationError:
            name = guest_item.variant.product.name
            guest_item.delete()
            notices.append(f"Removed {name} because it is no longer available.")
            continue
        availability = _lock_availability(variant)
        name = variant.product.name

        if not availability.is_available:
            guest_item.delete()
            notices.append(f"Removed {name} because it is no longer available.")
            continue

        existing = account_items.get(variant.pk)
        current_items = list(account_items.values())
        try:
            _ensure_compatible(
                current_items,
                availability.fulfillment_type,
                availability.preorder_batch,
            )
        except CartMutationError:
            guest_item.delete()
            notices.append(
                f"Removed {name} because it cannot be combined with your account cart."
            )
            continue

        max_quantity = availability.available_quantity
        if availability.fulfillment_type == PREORDER:
            other_quantity = sum(
                item.quantity
                for item in current_items
                if item.preorder_batch_id == availability.preorder_batch.pk
                and item.variant_id != variant.pk
            )
            max_quantity = min(
                max_quantity,
                max(0, availability.preorder_batch.remaining_quantity - other_quantity),
            )

        requested_total = guest_item.quantity + (existing.quantity if existing else 0)
        accepted_total = min(requested_total, max_quantity)
        accepted_guest_quantity = max(
            0,
            accepted_total - (existing.quantity if existing else 0),
        )

        if accepted_total == 0:
            if existing is not None:
                existing.delete()
                account_items.pop(variant.pk, None)
            guest_item.delete()
            notices.append(f"Removed {name} because no availability remained.")
            continue

        if accepted_total < requested_total:
            notices.append(
                f"Reduced {name} to {accepted_total} because only {max_quantity} was available."
            )

        if existing is None:
            existing = CartItem.objects.create(
                cart=account,
                variant=variant,
                preorder_batch=availability.preorder_batch,
                quantity=accepted_guest_quantity,
            )
            account_items[variant.pk] = existing
        else:
            if accepted_total != existing.quantity:
                existing.quantity = accepted_total
                existing.preorder_batch = availability.preorder_batch
                existing.save(update_fields=["quantity", "preorder_batch"])
        guest_item.delete()

    guest.delete()
    return CartMergeResult(tuple(notices))
