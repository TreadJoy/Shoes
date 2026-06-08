from .models import Cart


def cart_summary(request):
    cart_count = 0

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key, user=None).first()

        if cart:
            cart_count = cart.total_items()

    except Exception:
        cart_count = 0

    return {
        "cart_count": cart_count,
    }