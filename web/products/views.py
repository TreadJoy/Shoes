from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, Q

from .models import PreorderBatch, Product, ProductVariant
from .services import PREORDER, variant_availability


def _catalog_queryset():
    variant_queryset = ProductVariant.objects.select_related("product")
    live_batches = (
        PreorderBatch.objects.filter(
            status__in=[PreorderBatch.Status.OPEN, PreorderBatch.Status.PAUSED]
        )
        .prefetch_related("variant_allocations")
    )
    return Product.objects.prefetch_related(
        Prefetch("variants", queryset=variant_queryset),
        Prefetch(
            "preorder_batches",
            queryset=live_batches,
            to_attr="_live_preorder_batches",
        ),
    )


def _price_summary(product, variants):
    active_variants = [variant for variant in variants if variant.is_active]
    prices = [variant.current_price() for variant in active_variants]
    if not prices:
        prices = [product.current_price()]
    compare_prices = [
        variant.compare_price()
        for variant in active_variants
        if variant.compare_price() is not None
    ]
    return {
        "price_min": min(prices),
        "price_max": max(prices),
        "compare_at_price": max(compare_prices) if compare_prices else None,
        "on_sale": bool(compare_prices),
    }


def product_list(request):
    products = _catalog_queryset().filter(is_active=True)
    audience = request.GET.get("audience", "")
    category = request.GET.get("category", "")
    query = request.GET.get("q", "").strip()[:100]
    sale_only = request.GET.get("sale") == "1"

    valid_audiences = {choice[0] for choice in Product.AUDIENCE_CHOICES}
    valid_categories = {choice[0] for choice in Product.CATEGORY_CHOICES}

    if audience in valid_audiences:
        products = products.filter(audience=audience)
    else:
        audience = ""

    if category in valid_categories:
        products = products.filter(category=category)
    else:
        category = ""

    if sale_only:
        products = products.filter(
            Q(sale_price__isnull=False)
            | Q(
                variants__is_active=True,
                variants__compare_at_price__isnull=False,
            )
        ).distinct()

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(variants__color__icontains=query)
        ).distinct()

    if query:
        catalog_heading = f'Search results for “{query}”'
        catalog_description = "Products matching your search."
    elif sale_only:
        catalog_heading = "Sale"
        catalog_description = "Current TreadJoy sale products."
    elif audience:
        catalog_heading = dict(Product.AUDIENCE_CHOICES)[audience]
        catalog_description = f"Explore TreadJoy products for {catalog_heading.lower()}."
    else:
        catalog_heading = "Shop TreadJoy"
        catalog_description = "Explore our latest shoes and gear."

    catalog_items = []
    for product in products:
        variants = list(product.variants.all())
        for variant in variants:
            # Reuse the parent instance so availability can use its prefetched
            # live preorder batches instead of re-querying per SKU.
            variant.product = product
        availabilities = [
            variant_availability(variant)
            for variant in variants
        ]
        has_available_variants = any(
            availability.is_available
            for availability in availabilities
        )
        is_preorder = any(
            availability.fulfillment_type == PREORDER
            for availability in availabilities
        )
        if is_preorder:
            availability_label = (
                "Preorder" if has_available_variants else "Preorder Unavailable"
            )
        elif has_available_variants:
            availability_label = "Available"
        else:
            availability_label = "Sold Out"

        catalog_items.append(
            {
                "product": product,
                "availability_label": availability_label,
                "has_available_variants": has_available_variants,
                "is_preorder": is_preorder,
                **_price_summary(product, variants),
            }
        )

    return render(request, "products/product_list.html", {
        "products": products,
        "catalog_items": catalog_items,
        "catalog_heading": catalog_heading,
        "catalog_description": catalog_description,
        "active_audience": audience,
        "active_category": category,
        "sale_only": sale_only,
        "search_query": query,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        _catalog_queryset(),
        slug=slug,
        is_active=True,
    )
    variants = list(product.variants.all())
    for variant in variants:
        variant.product = product
    variant_options = [
        {
            "variant": variant,
            "availability": variant_availability(variant),
        }
        for variant in variants
    ]
    preorder_batch = next(
        (
            option["availability"].preorder_batch
            for option in variant_options
            if option["availability"].preorder_batch is not None
        ),
        None,
    )
    has_available_variants = any(
        option["availability"].is_available
        for option in variant_options
    )
    if preorder_batch is not None:
        availability_label = (
            "Preorder" if has_available_variants else "Preorder Unavailable"
        )
    elif has_available_variants:
        availability_label = "Available"
    else:
        availability_label = "Sold Out"

    return render(request, "products/product_detail.html", {
        "product": product,
        "variant_options": variant_options,
        "preorder_batch": preorder_batch,
        "has_available_variants": has_available_variants,
        "availability_label": availability_label,
        **_price_summary(product, variants),
    })
