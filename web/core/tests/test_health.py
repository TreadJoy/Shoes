from unittest.mock import Mock, patch

from django.db.utils import OperationalError
from django.test import TestCase


class HealthEndpointTests(TestCase):
    def test_live_is_generic_and_does_not_touch_dependencies(self):
        response = self.client.get("/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertNotIn("database", response.content.decode().lower())

    def test_ready_reports_database_health_without_details(self):
        response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_ready_returns_generic_503_and_alerts_on_dependency_failure(self):
        cursor = Mock()
        cursor.__enter__ = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        cursor.execute.side_effect = OperationalError(
            "password=synthetic-secret host=private-db.example.invalid"
        )
        database = Mock()
        database.cursor.return_value = cursor

        with (
            patch("web.core.health.connections", {"default": database}),
            self.assertLogs("Shoes.alert", level="CRITICAL") as captured,
        ):
            response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
        self.assertNotIn("synthetic-secret", response.content.decode())
        self.assertNotIn("private-db", "\n".join(captured.output))
        self.assertEqual(captured.records[0].alert_name, "database_unavailable")
        self.assertFalse(captured.records[0].synthetic)
