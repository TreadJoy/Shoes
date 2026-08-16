import unittest

from django.conf import settings


if not settings.IS_COMMERCE_MODE:
    raise unittest.SkipTest("Order tests require commerce mode.")
