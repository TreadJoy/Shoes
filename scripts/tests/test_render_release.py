import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import render_release


class RenderReleaseAdapterTests(unittest.TestCase):
    release_sha = "0123456789abcdef0123456789abcdef01234567"

    def test_promote_records_current_and_previous_deploys(self):
        responses = iter(
            (
                [
                    {
                        "id": "previous-deploy",
                        "status": "live",
                        "commit": {"id": "fedcba9876543210fedcba9876543210fedcba98"},
                    }
                ],
                {"id": "new-deploy"},
                {
                    "id": "new-deploy",
                    "status": "live",
                    "commit": {"id": self.release_sha},
                },
            )
        )

        with tempfile.TemporaryDirectory() as temporary:
            with (
                patch.object(render_release, "request_json", side_effect=responses),
                patch.dict(
                    os.environ,
                    {
                        "RENDER_API_KEY": "synthetic-render-key",
                        "RENDER_DEPLOY_TIMEOUT_SECONDS": "1",
                        "RENDER_DEPLOY_POLL_SECONDS": "1",
                    },
                ),
            ):
                original = Path.cwd()
                try:
                    os.chdir(temporary)
                    render_release.promote("service-id", self.release_sha, "staging")
                finally:
                    os.chdir(original)

            promotion = json.loads(
                Path(temporary, "release-promotion.json").read_text(encoding="utf-8")
            )
            rollback = json.loads(
                Path(temporary, "rollback-manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(promotion["deploy_id"], "new-deploy")
        self.assertEqual(promotion["release_sha"], self.release_sha)
        self.assertEqual(rollback["previous_deploy_id"], "previous-deploy")
        self.assertEqual(
            rollback["previous_commit"], "fedcba9876543210fedcba9876543210fedcba98"
        )

    def test_rollback_records_requested_deploy(self):
        with tempfile.TemporaryDirectory() as temporary:
            with (
                patch.object(
                    render_release,
                    "request_json",
                    return_value={"id": "rollback-result"},
                ),
                patch.dict(os.environ, {"RENDER_API_KEY": "synthetic-render-key"}),
            ):
                original = Path.cwd()
                try:
                    os.chdir(temporary)
                    render_release.rollback("service-id", "previous-deploy", "staging")
                finally:
                    os.chdir(original)

            result = json.loads(
                Path(temporary, "rollback-result.json").read_text(encoding="utf-8")
            )

        self.assertEqual(result["requested_deploy_id"], "previous-deploy")
        self.assertEqual(result["response_deploy_id"], "rollback-result")

    def test_missing_api_key_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                render_release.api_key()


class ResearchReleaseWorkflowProfileTests(unittest.TestCase):
    workflow = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "research-release.yml"

    def test_staging_is_the_only_private_poc_profile_target(self):
        content = self.workflow.read_text(encoding="utf-8")

        self.assertIn(
            "RELEASE_CONTENT_PROFILE: ${{ github.event_name == 'workflow_dispatch' && inputs.target == 'staging' && 'private-poc' || 'public' }}",
            content,
        )
        self.assertIn(
            'python manage.py check_release_content --profile "$RELEASE_CONTENT_PROFILE"',
            content,
        )
        self.assertIn('"content_profile": os.environ["RELEASE_CONTENT_PROFILE"]', content)

    def test_promotions_verify_content_profile(self):
        content = self.workflow.read_text(encoding="utf-8")

        self.assertIn(
            "EXPECTED_CONTENT_PROFILE: ${{ inputs.target == 'staging' && 'private-poc' || 'public' }}",
            content,
        )
        self.assertIn("EXPECTED_CONTENT_PROFILE: public", content)
        self.assertIn(
            'artifact content profile does not match the promotion target',
            content,
        )
