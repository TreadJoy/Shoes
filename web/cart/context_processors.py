from .models import Cart


def cart_summary(request):
    if getattr(request.user, "is_authenticated", False):
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session = getattr(request, "session", None)
        session_key = getattr(session, "session_key", None)
        if not session_key:
            return {"cart_count": 0}
        cart = Cart.objects.filter(session_key=session_key, user=None).first()

    cart_count = cart.total_items() if cart else 0

    return {
        "cart_count": cart_count,
    }
