import json
import logging
import uuid
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from Shoes.observability import (
    RedactionFilter,
    JsonFormatter,
    RequestContextFilter,
    emit_alert,
    redact_path,
    redact_text,
)


class ObservabilityRedactionTests(SimpleTestCase):
    def test_redacts_secrets_tokens_and_email_addresses(self):
        value = (
            "password=synthetic-password token=opaque-token "
            "key=sk_test_synthetic_key contact=owner@example.invalid"
        )

        redacted = redact_text(value)

        self.assertNotIn("synthetic-password", redacted)
        self.assertNotIn("opaque-token", redacted)
        self.assertNotIn("sk_test_synthetic_key", redacted)
        self.assertNotIn("owner@example.invalid", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)

    def test_redacts_waitlist_path_tokens(self):
        self.assertEqual(
            redact_path("/waitlist/confirm/opaque-token-123/"),
            "/waitlist/confirm/[REDACTED]/",
        )
        self.assertEqual(
            redact_path("/waitlist/unsubscribe/opaque-token-456"),
            "/waitlist/unsubscribe/[REDACTED]",
        )

    def test_filter_replaces_rendered_message_and_arguments(self):
        record = logging.LogRecord(
            "synthetic",
            logging.WARNING,
            __file__,
            1,
            "secret=%s email=%s",
            ("synthetic-secret", "owner@example.invalid"),
            None,
        )

        self.assertTrue(RedactionFilter().filter(record))
        self.assertNotIn("synthetic-secret", record.getMessage())
        self.assertNotIn("owner@example.invalid", record.getMessage())
        self.assertEqual(record.args, ())

    def test_filter_uses_request_object_after_context_is_reset(self):
        record = logging.LogRecord(
            "django.request",
            logging.WARNING,
            __file__,
            1,
            "Not Found",
            (),
            None,
        )
        record.request = SimpleNamespace(
            request_id="12345678-1234-5678-1234-567812345678"
        )

        self.assertTrue(RequestContextFilter().filter(record))
        self.assertEqual(
            record.request_id,
            "12345678-1234-5678-1234-567812345678",
        )

    def test_json_formatter_allowlists_fields_and_redacts_values(self):
        record = logging.LogRecord(
            "synthetic",
            logging.WARNING,
            __file__,
            1,
            "contact=owner@example.invalid token=opaque-token "
            "/waitlist/confirm/opaque-token/",
            (),
            None,
        )
        record.event = "synthetic.check"
        record.request_id = "12345678-1234-5678-1234-567812345678"
        record.request_path = "/waitlist/confirm/opaque-token/"
        record.unexpected = "must not be serialized"

        payload = json.loads(JsonFormatter().format(record))

        self.assertEqual(payload["event"], "synthetic.check")
        self.assertEqual(payload["request_id"], record.request_id)
        self.assertEqual(
            payload["request_path"], "/waitlist/confirm/[REDACTED]/"
        )
        self.assertNotIn("owner@example.invalid", payload["message"])
        self.assertNotIn("opaque-token", payload["message"])
        self.assertIn("/waitlist/confirm/[REDACTED]/", payload["message"])
        self.assertNotIn("unexpected", payload)


class RequestCorrelationTests(TestCase):
    def test_valid_request_id_is_propagated_and_logged(self):
        request_id = "12345678-1234-5678-1234-567812345678"

        with self.assertLogs("Shoes.request", level="INFO") as captured:
            response = self.client.get(
                "/health/live/", HTTP_X_REQUEST_ID=request_id
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Request-ID"], request_id)
        completion = next(
            record
            for record in captured.records
            if getattr(record, "event", "") == "request.completed"
        )
        self.assertEqual(completion.request_id, request_id)
        self.assertEqual(completion.request_path, "/health/live/")

    def test_invalid_request_id_is_replaced_with_uuid(self):
        response = self.client.get(
            "/health/live/", HTTP_X_REQUEST_ID="not-a-safe-request-id"
        )

        generated = response["X-Request-ID"]
        self.assertNotEqual(generated, "not-a-safe-request-id")
        self.assertEqual(str(uuid.UUID(generated)), generated)


class AlertDeliveryTests(SimpleTestCase):
    def test_synthetic_alert_is_delivered_as_structured_record(self):
        with self.assertLogs("Shoes.alert", level="WARNING") as captured:
            emit_alert(
                "synthetic.delivery",
                "warning",
                "Synthetic alert delivery check.",
                dedupe_key="synthetic-check",
                synthetic=True,
            )

        record = captured.records[0]
        self.assertEqual(record.event, "alert")
        self.assertEqual(record.alert_name, "synthetic.delivery")
        self.assertEqual(record.dedupe_key, "synthetic-check")
        self.assertTrue(record.synthetic)
