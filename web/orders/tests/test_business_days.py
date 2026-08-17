from datetime import datetime, timezone as datetime_timezone
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from web.orders.services import next_inventory_review_deadline


CENTRAL = ZoneInfo("America/Chicago")


class InventoryReviewDeadlineTests(SimpleTestCase):
    def assert_local_deadline(self, detected_at, expected_local):
        deadline = next_inventory_review_deadline(detected_at)

        self.assertEqual(deadline.tzinfo, datetime_timezone.utc)
        self.assertEqual(deadline.astimezone(CENTRAL), expected_local)

    def test_normal_weekday_deadline_is_next_day_at_five_central(self):
        detected_at = datetime(2026, 8, 11, 10, 30, tzinfo=CENTRAL)

        self.assert_local_deadline(
            detected_at,
            datetime(2026, 8, 12, 17, 0, tzinfo=CENTRAL),
        )

    def test_friday_deadline_skips_weekend(self):
        detected_at = datetime(2026, 8, 14, 16, 59, tzinfo=CENTRAL)

        self.assert_local_deadline(
            detected_at,
            datetime(2026, 8, 17, 17, 0, tzinfo=CENTRAL),
        )

    def test_deadline_skips_observed_federal_holiday_and_weekend(self):
        detected_at = datetime(2026, 7, 2, 18, 0, tzinfo=CENTRAL)

        self.assert_local_deadline(
            detected_at,
            datetime(2026, 7, 6, 17, 0, tzinfo=CENTRAL),
        )

    def test_deadline_uses_central_time_across_standard_time(self):
        detected_at = datetime(2026, 1, 6, 20, 0, tzinfo=datetime_timezone.utc)

        deadline = next_inventory_review_deadline(detected_at)

        self.assertEqual(
            deadline,
            datetime(2026, 1, 7, 23, 0, tzinfo=datetime_timezone.utc),
        )
