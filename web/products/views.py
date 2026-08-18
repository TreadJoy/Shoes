from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product
from .services import PREORDER, variant_availability


def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related("variants")
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
        products = products.filter(sale_price__isnull=False)

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
        availabilities = [
            variant_availability(variant)
            for variant in product.variants.all()
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

        catalog_items.append({
            "product": product,
            "availability_label": availability_label,
            "has_available_variants": has_available_variants,
            "is_preorder": is_preorder,
        })

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
        Product.objects.prefetch_related("variants"),
        slug=slug,
        is_active=True,
    )
    variant_options = [
        {
            "variant": variant,
            "availability": variant_availability(variant),
        }
        for variant in product.variants.all()
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
    })
