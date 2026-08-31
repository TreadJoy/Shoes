from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection, transaction
from django.test import Client, RequestFactory, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from unittest import skipIf, skipUnless

from web.waitlist.admin import MarketingBroadcastAdmin
from web.waitlist.models import ConsentEvent, EmailSuppression, MarketingBroadcast, ResearchAbuseMetric, ResearchOutboundEmail, ResendWebhookEvent, SubscriptionStatus, WaitlistSubscription
from web.waitlist.providers import ResearchEmailProviderError
from web.waitlist.services import confirmation_token, request_subscription, unsubscribe_token


class WaitlistFlowTests(TestCase):
    payload = {"email": "Jo@Example.COM", "consent": "on"}

    def test_form_is_email_only_affirmative_and_has_no_public_count(self):
        response = self.client.get(reverse("waitlist:join_waitlist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "novalidate")
        self.assertContains(response, "two messages per UTC calendar month")
        self.assertNotContains(response, "First name")
        self.assertNotContains(response, "people have joined")

    def test_valid_request_is_pending_normalized_and_generic(self):
        response = self.client.post(reverse("waitlist:join_waitlist"), self.payload, follow=True)
        self.assertContains(response, "Check your email if your address is eligible")
        subscription = WaitlistSubscription.objects.get()
        self.assertEqual(subscription.email, "jo@example.com")
        self.assertEqual(subscription.status, SubscriptionStatus.PENDING)
        self.assertTrue(subscription.confirmation_token_digest)
        self.assertEqual(ConsentEvent.objects.get().kind, ConsentEvent.Kind.REQUESTED)
        self.assertEqual(ResearchOutboundEmail.objects.count(), 1)

    def test_source_is_derived_from_the_distinct_server_route(self):
        self.client.post(
            reverse("waitlist:join_homepage"),
            {**self.payload, "source": "waitlist_page"},
        )
        self.assertEqual(WaitlistSubscription.objects.get().source, "homepage")

    def test_known_and_unknown_addresses_receive_same_response(self):
        first = self.client.post(reverse("waitlist:join_waitlist"), self.payload, follow=True)
        second = self.client.post(reverse("waitlist:join_waitlist"), {"email": "JO@example.com", "consent": "on"}, follow=True)
        self.assertContains(first, "Check your email if your address is eligible")
        self.assertContains(second, "Check your email if your address is eligible")
        self.assertNotContains(second, "already")

    def test_consent_is_required(self):
        response = self.client.post(reverse("waitlist:join_waitlist"), {"email": "jo@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required")
        self.assertContains(response, "autofocus")
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, 'aria-describedby="id_consent_error"')
        self.assertFalse(WaitlistSubscription.objects.exists())

    def test_honeypot_is_neutral_and_writes_only_aggregate_signal(self):
        response = self.client.post(reverse("waitlist:join_waitlist"), {**self.payload, "company_website": "bot"}, follow=True)
        self.assertContains(response, "Check your email if your address is eligible")
        self.assertFalse(WaitlistSubscription.objects.exists())
        self.assertEqual(ResearchAbuseMetric.objects.get().count, 1)

    def test_get_does_not_confirm_and_post_is_idempotent(self):
        subscription = request_subscription(email="confirm@example.com", source="waitlist_page")
        token = confirmation_token(subscription)
        url = reverse("waitlist:confirm", args=[token])
        self.client.get(url)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, SubscriptionStatus.PENDING)
        self.client.post(url)
        self.client.post(url)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(ConsentEvent.objects.filter(kind=ConsentEvent.Kind.CONFIRMED).count(), 1)

    def test_expired_confirmation_is_rejected(self):
        subscription = request_subscription(email="expired@example.com", source="waitlist_page")
        token = confirmation_token(subscription)
        WaitlistSubscription.objects.filter(pk=subscription.pk).update(confirmation_expires_at=timezone.now() - timedelta(seconds=1))
        response = self.client.post(reverse("waitlist:confirm", args=[token]))
        self.assertContains(response, "expired")

    def test_unsubscribe_get_is_read_only_and_post_suppresses_identity(self):
        subscription = request_subscription(email="leave@example.com", source="waitlist_page")
        self.client.post(reverse("waitlist:confirm", args=[confirmation_token(subscription)]))
        subscription.refresh_from_db()
        token = unsubscribe_token(subscription)
        url = reverse("waitlist:unsubscribe", args=[token])
        self.client.get(url)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.client.post(url)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, SubscriptionStatus.UNSUBSCRIBED)
        self.assertIsNone(subscription.email)
        self.assertEqual(EmailSuppression.objects.count(), 1)

    def test_fresh_double_opt_in_supersedes_but_preserves_suppression_evidence(self):
        original = request_subscription(email="return@example.com", source="waitlist_page")
        self.client.post(reverse("waitlist:confirm", args=[confirmation_token(original)]))
        original.refresh_from_db()
        self.client.post(reverse("waitlist:unsubscribe", args=[unsubscribe_token(original)]))

        replacement = request_subscription(email="RETURN@example.com", source="homepage")

        self.assertNotEqual(replacement.pk, original.pk)
        self.assertEqual(replacement.status, SubscriptionStatus.PENDING)
        suppression = EmailSuppression.objects.get()
        self.assertIsNotNone(suppression.superseded_at)
        self.assertTrue(
            replacement.consent_events.filter(kind=ConsentEvent.Kind.RESUBSCRIBED).exists()
        )

    def test_confirmation_send_limit_is_address_scoped_and_neutral(self):
        for _ in range(4):
            response = self.client.post(
                reverse("waitlist:join_waitlist"), self.payload, follow=True
            )
            self.assertContains(response, "Check your email if your address is eligible")
        self.assertEqual(ResearchOutboundEmail.objects.count(), 3)

    def test_session_throttle_returns_accessible_429(self):
        for index in range(5):
            self.client.post(reverse("waitlist:join_waitlist"), {"email": f"person{index}@example.com", "consent": "on"})
        response = self.client.post(reverse("waitlist:join_waitlist"), {"email": "sixth@example.com", "consent": "on"})
        self.assertEqual(response.status_code, 429)
        self.assertIn("Retry-After", response)
        self.assertContains(response, "Please Wait Before Trying Again", status_code=429)

    def test_csrf_is_enforced_for_state_changes(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse("waitlist:join_waitlist"), self.payload).status_code, 403)
        subscription = request_subscription(
            email="csrf-confirm@example.com", source="waitlist_page"
        )
        self.assertEqual(
            client.post(
                reverse("waitlist:confirm", args=[confirmation_token(subscription)])
            ).status_code,
            403,
        )

    def test_consent_event_is_immutable(self):
        subscription = request_subscription(email="immutable@example.com", source="waitlist_page")
        event = subscription.consent_events.get()
        event.kind = ConsentEvent.Kind.CONFIRMED
        with self.assertRaises(ValidationError):
            event.save()
        with self.assertRaises(ValidationError):
            event.delete()
        with self.assertRaises(ValidationError):
            ConsentEvent.objects.filter(pk=event.pk).update(
                kind=ConsentEvent.Kind.CONFIRMED
            )
        with self.assertRaises(ValidationError):
            ConsentEvent.objects.filter(pk=event.pk).delete()

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    def test_fake_delivery_command_marks_outbox_sent(self):
        request_subscription(email="deliver@example.com", source="waitlist_page")
        output = StringIO()
        call_command("deliver_research_email", limit=1, stdout=output)
        self.assertEqual(ResearchOutboundEmail.objects.get().status, ResearchOutboundEmail.Status.SENT)
        self.assertIn("sent=1", output.getvalue())

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    @patch(
        "web.waitlist.management.commands.deliver_research_email.send_confirmation",
        side_effect=ResearchEmailProviderError("synthetic_provider_failure"),
    )
    def test_delivery_failure_remains_retryable_and_redacted(self, sender):
        request_subscription(email="retry@example.com", source="waitlist_page")
        output = StringIO()
        call_command("deliver_research_email", limit=1, stdout=output)
        outbound = ResearchOutboundEmail.objects.get()
        self.assertEqual(outbound.status, ResearchOutboundEmail.Status.FAILED)
        self.assertEqual(outbound.error_code, "synthetic_provider_failure")
        self.assertIsNotNone(outbound.next_attempt_at)
        self.assertNotIn("retry@example.com", output.getvalue())

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    @override_settings(RESEARCH_RETENTION_POLICY_VERSION="")
    def test_retention_is_dry_run_by_default_and_apply_is_gated(self):
        output = StringIO()
        call_command("enforce_research_retention", stdout=output)
        self.assertIn("dry_run=true", output.getvalue())
        with self.assertRaises(CommandError):
            call_command("enforce_research_retention", apply=True, policy_version="draft")

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    @override_settings(RESEARCH_RETENTION_POLICY_VERSION="draft-retention-v1")
    def test_retention_apply_refuses_a_matching_draft_version(self):
        with self.assertRaises(CommandError):
            call_command(
                "enforce_research_retention",
                apply=True,
                policy_version="draft-retention-v1",
            )

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    @override_settings(RESEARCH_RETENTION_POLICY_VERSION="effective-v1")
    def test_retention_uses_withdrawal_and_supersession_as_five_year_clocks(self):
        six_years_ago = timezone.now() - timedelta(days=365 * 6)
        with patch("django.utils.timezone.now", return_value=six_years_ago):
            subscription = request_subscription(
                email="retention@example.com",
                source="waitlist_page",
            )
            self.client.post(
                reverse(
                    "waitlist:confirm",
                    args=[confirmation_token(subscription)],
                )
            )
        subscription.refresh_from_db()
        self.client.post(
            reverse(
                "waitlist:unsubscribe",
                args=[unsubscribe_token(subscription)],
            )
        )
        suppression = EmailSuppression.objects.get()
        suppression.superseded_at = timezone.now() + timedelta(days=365 * 4)
        suppression.save(update_fields=("superseded_at",))

        call_command(
            "enforce_research_retention",
            apply=True,
            policy_version="effective-v1",
            stdout=StringIO(),
        )
        self.assertEqual(ConsentEvent.objects.count(), 3)
        self.assertTrue(EmailSuppression.objects.exists())

        six_years_later = timezone.now() + timedelta(days=365 * 6)
        with patch(
            "web.waitlist.management.commands.enforce_research_retention.timezone.now",
            return_value=six_years_later,
        ):
            call_command(
                "enforce_research_retention",
                apply=True,
                policy_version="effective-v1",
                stdout=StringIO(),
            )
        self.assertFalse(ConsentEvent.objects.exists())
        self.assertTrue(EmailSuppression.objects.exists())

        ten_years_later = timezone.now() + timedelta(days=365 * 10)
        with patch(
            "web.waitlist.management.commands.enforce_research_retention.timezone.now",
            return_value=ten_years_later,
        ):
            call_command(
                "enforce_research_retention",
                apply=True,
                policy_version="effective-v1",
                stdout=StringIO(),
            )
        self.assertFalse(EmailSuppression.objects.exists())

    @patch("web.waitlist.views.verify_webhook", side_effect=ResearchEmailProviderError("invalid"))
    def test_invalid_webhook_does_not_persist_payload(self, verifier):
        response = self.client.post(
            reverse("waitlist:resend_webhook"),
            data=b'{"email":"secret@example.com"}',
            content_type="application/json",
            headers={"svix-id": "event-1", "svix-timestamp": "1", "svix-signature": "bad"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(hasattr(ResearchOutboundEmail, "raw_payload"))

    @patch("web.waitlist.views.verify_webhook")
    def test_terminal_webhook_is_deduplicated_and_survives_out_of_order_delivery(self, verifier):
        subscription = request_subscription(email="bounce@example.com", source="waitlist_page")
        outbound = subscription.outbound_emails.get()
        outbound.provider_message_id = "provider-message-1"
        outbound.status = ResearchOutboundEmail.Status.SENT
        outbound.save()
        headers = {
            "svix-timestamp": "1",
            "svix-signature": "valid",
        }
        verifier.return_value = {
            "type": "email.bounced",
            "created_at": "2026-08-30T12:00:00Z",
            "data": {"email_id": "provider-message-1"},
        }
        url = reverse("waitlist:resend_webhook")
        first = self.client.post(
            url,
            data=b"{}",
            content_type="application/json",
            headers={**headers, "svix-id": "event-terminal"},
        )
        replay = self.client.post(
            url,
            data=b"{}",
            content_type="application/json",
            headers={**headers, "svix-id": "event-terminal"},
        )
        self.assertEqual(first.status_code, 204)
        self.assertEqual(replay.status_code, 204)
        self.assertEqual(ResendWebhookEvent.objects.count(), 1)
        outbound.refresh_from_db()
        subscription.refresh_from_db()
        self.assertEqual(outbound.status, ResearchOutboundEmail.Status.BOUNCED)
        self.assertEqual(subscription.status, SubscriptionStatus.SUPPRESSED)
        self.assertIsNone(subscription.email)

        verifier.return_value = {
            "type": "email.delivered",
            "created_at": "2026-08-30T11:59:00Z",
            "data": {"email_id": "provider-message-1"},
        }
        self.client.post(
            url,
            data=b"{}",
            content_type="application/json",
            headers={**headers, "svix-id": "event-older-delivery"},
        )
        outbound.refresh_from_db()
        self.assertEqual(outbound.status, ResearchOutboundEmail.Status.BOUNCED)
        self.assertEqual(
            ConsentEvent.objects.filter(kind=ConsentEvent.Kind.SUPPRESSED).count(),
            1,
        )

        verifier.return_value = {
            "type": "email.delivered",
            "created_at": "2026-08-30T12:01:00Z",
            "data": {"email_id": "provider-message-1"},
        }
        self.client.post(
            url,
            data=b"{}",
            content_type="application/json",
            headers={**headers, "svix-id": "event-newer-delivery"},
        )
        outbound.refresh_from_db()
        self.assertEqual(outbound.status, ResearchOutboundEmail.Status.BOUNCED)

    @skipIf(settings.IS_COMMERCE_MODE, "Research roles are installed only in research")
    def test_research_roles_are_least_privilege(self):
        analyst = Group.objects.get(name="Research analyst")
        manager = Group.objects.get(name="Relationship manager")
        self.assertEqual(
            set(analyst.permissions.values_list("codename", flat=True)),
            {"view_surveyresponse", "export_surveyresponse"},
        )
        self.assertEqual(
            set(manager.permissions.values_list("codename", flat=True)),
            {
                "view_waitlistsubscription",
                "view_consentevent",
                "view_emailsuppression",
                "view_researchoutboundemail",
                "view_resendwebhookevent",
                "view_marketingbroadcast",
                "add_marketingbroadcast",
                "approve_marketingbroadcast",
            },
        )

    @override_settings(IS_COMMERCE_MODE=True)
    def test_research_operational_commands_refuse_commerce_mode(self):
        for command in (
            "deliver_research_email",
            "sync_research_resend",
            "enforce_research_retention",
            "check_research_engagement",
        ):
            with self.subTest(command=command), self.assertRaises(CommandError):
                call_command(command, stdout=StringIO(), stderr=StringIO())

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    @override_settings(
        RESEARCH_PRIVACY_NOTICE_VERSION="ci-approved-notice-v1",
        RESEARCH_PRIVACY_NOTICE_BODY="Synthetic CI research privacy notice.",
        RESEARCH_PRIVACY_NOTICE_SHA256="7f9862d185c863a44aecce5c100391d98888738d7d47a1b802dff54b8ea1f205",
        RESEARCH_RETENTION_POLICY_VERSION="ci-retention-v1",
    )
    def test_research_engagement_check_accepts_the_fake_installed_profile(self):
        output = StringIO()
        call_command("check_research_engagement", stdout=output)
        self.assertIn("Research engagement boundary passed", output.getvalue())

    @skipIf(settings.IS_COMMERCE_MODE, "Research-only operational command")
    @override_settings(
        RESEARCH_EMAIL_PROVIDER="resend",
        RESEARCH_RESEND_MANAGEMENT_API_KEY="",
    )
    def test_research_engagement_check_fails_without_the_job_management_key(self):
        with self.assertRaises(CommandError):
            call_command(
                "check_research_engagement",
                stdout=StringIO(),
                stderr=StringIO(),
            )


class MarketingBroadcastAdminTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="relationship-manager-test",
            password="synthetic-test-password",
            is_staff=True,
        )
        permission = Group.objects.get(name="Relationship manager").permissions.get(
            codename="approve_marketingbroadcast"
        )
        self.user.user_permissions.add(permission)
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.request = RequestFactory().post(
            "/admin/waitlist/marketingbroadcast/"
        )
        self.request.user = self.user
        self.model_admin = MarketingBroadcastAdmin(MarketingBroadcast, admin.site)

    @skipIf(settings.IS_COMMERCE_MODE, "Research roles are installed only in research")
    def test_relationship_manager_can_record_only_a_provider_draft_identifier(self):
        self.assertTrue(self.model_admin.has_add_permission(self.request))
        self.assertEqual(self.model_admin.fields, ("provider_broadcast_id",))
        self.assertFalse(self.model_admin.has_change_permission(self.request))

    @skipIf(settings.IS_COMMERCE_MODE, "Research roles are installed only in research")
    @patch("web.waitlist.admin.send_broadcast")
    def test_permissioned_approval_records_actor_count_and_sends_provider_draft(self, sender):
        subscription = request_subscription(
            email="broadcast@example.com", source="waitlist_page"
        )
        self.client.post(
            reverse("waitlist:confirm", args=[confirmation_token(subscription)])
        )
        broadcast = MarketingBroadcast.objects.create(
            provider_broadcast_id="provider-draft-1"
        )

        self.model_admin.approve_and_send(
            self.request, MarketingBroadcast.objects.filter(pk=broadcast.pk)
        )

        broadcast.refresh_from_db()
        self.assertEqual(broadcast.status, MarketingBroadcast.Status.SENT)
        self.assertEqual(broadcast.approved_by, self.user)
        self.assertEqual(broadcast.recipient_count, 1)
        sender.assert_called_once_with("provider-draft-1")

    @skipIf(settings.IS_COMMERCE_MODE, "Research roles are installed only in research")
    @patch("web.waitlist.admin.send_broadcast")
    def test_monthly_cap_blocks_a_third_queued_or_sent_broadcast(self, sender):
        now = timezone.now()
        for index in range(2):
            MarketingBroadcast.objects.create(
                provider_broadcast_id=f"already-{index}",
                status=MarketingBroadcast.Status.SENT,
                approved_by=self.user,
                approved_at=now,
                sent_at=now,
            )
        draft = MarketingBroadcast.objects.create(
            provider_broadcast_id="blocked-third"
        )

        with patch.object(self.model_admin, "message_user") as message_user:
            self.model_admin.approve_and_send(
                self.request, MarketingBroadcast.objects.filter(pk=draft.pk)
            )

        draft.refresh_from_db()
        self.assertEqual(draft.status, MarketingBroadcast.Status.DRAFT)
        sender.assert_not_called()
        message_user.assert_called_once()


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL uniqueness behavior.")
class WaitlistDatabaseContractTests(TransactionTestCase):
    def test_normalized_email_constraint_rolls_back_atomic_duplicates(self):
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WaitlistSubscription.objects.create(
                    email="duplicate@example.com",
                    status=SubscriptionStatus.PENDING,
                    confirmation_token_digest="a" * 64,
                    confirmation_expires_at=now + timedelta(hours=1),
                )
                WaitlistSubscription.objects.create(
                    email="DUPLICATE@example.com",
                    status=SubscriptionStatus.PENDING,
                    confirmation_token_digest="b" * 64,
                    confirmation_expires_at=now + timedelta(hours=1),
                )
        self.assertFalse(WaitlistSubscription.objects.exists())
