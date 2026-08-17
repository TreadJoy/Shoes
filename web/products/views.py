from django.shortcuts import render, get_object_or_404
from .models import Product
from .services import variant_availability


def product_list(request):
    products = Product.objects.filter(is_active=True)

    return render(request, "products/product_list.html", {
        "products": products,
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

    return render(request, "products/product_detail.html", {
        "product": product,
        "variant_options": variant_options,
        "preorder_batch": preorder_batch,
        "has_available_variants": any(
            option["availability"].is_available
            for option in variant_options
        ),
    })
