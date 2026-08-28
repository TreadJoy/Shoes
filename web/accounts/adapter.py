from django.conf import settings
from django.contrib import messages

from allauth.account.adapter import DefaultAccountAdapter


GUEST_CART_SESSION_KEY = "treadjoy_guest_cart_session_key"


class TreadJoyAccountAdapter(DefaultAccountAdapter):
    """Keep the pre-auth guest-cart key across Django's session rotation."""

    def pre_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url,
    ):
        response = super().pre_login(
            request,
            user,
            email_verification=email_verification,
            signal_kwargs=signal_kwargs,
            email=email,
            signup=signup,
            redirect_url=redirect_url,
        )
        if (
            response is None
            and settings.IS_COMMERCE_MODE
            and not request.user.is_authenticated
            and getattr(request, "session", None) is not None
            and request.session.session_key
        ):
            request.session[GUEST_CART_SESSION_KEY] = request.session.session_key
            request.session.modified = True
        return response

    def post_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url,
    ):
        if settings.IS_COMMERCE_MODE:
            guest_session_key = request.session.get(GUEST_CART_SESSION_KEY)
            if guest_session_key:
                from web.cart.services import merge_guest_cart

                result = merge_guest_cart(
                    user=user,
                    guest_session_key=guest_session_key,
                )
                request.session.pop(GUEST_CART_SESSION_KEY, None)
                request.session.modified = True
                for notice in result.notices:
                    self.add_message(request, messages.INFO, message=notice)

        return super().post_login(
            request,
            user,
            email_verification=email_verification,
            signal_kwargs=signal_kwargs,
            email=email,
            signup=signup,
            redirect_url=redirect_url,
        )
