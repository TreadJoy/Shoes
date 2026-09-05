import copy
import json
import unittest
from pathlib import Path

from scripts import validate_cloudflare_research


POLICY_PATH = (
    Path(__file__).resolve().parents[2]
    / "deploy"
    / "cloudflare"
    / "research"
    / "policy.json"
)


class CloudflareResearchPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_checked_in_policy_validates(self):
        validate_cloudflare_research.validate(self.policy)

    def test_a22_edge_limits_are_distinct_from_application_limits(self):
        waitlist, survey = self.policy["rate_limiting"]["rules"]

        self.assertEqual(
            (waitlist["requests_per_period"], waitlist["period_seconds"]),
            (10, 600),
        )
        self.assertEqual(
            (survey["requests_per_period"], survey["period_seconds"]),
            (60, 600),
        )
        self.assertEqual(
            [rule["staging_action"] for rule in (waitlist, survey)],
            ["log", "log"],
        )
        self.assertEqual(
            [rule["enforced_action"] for rule in (waitlist, survey)],
            ["managed_challenge", "managed_challenge"],
        )

    def test_validator_rejects_wrong_edge_threshold_or_action(self):
        mutated = copy.deepcopy(self.policy)
        mutated["rate_limiting"]["rules"][0]["requests_per_period"] = 5
        with self.assertRaises(validate_cloudflare_research.PolicyError):
            validate_cloudflare_research.validate(mutated)

        mutated = copy.deepcopy(self.policy)
        mutated["rate_limiting"]["rules"][1]["enforced_action"] = "block"
        with self.assertRaises(validate_cloudflare_research.PolicyError):
            validate_cloudflare_research.validate(mutated)

    def test_validator_rejects_unscoped_or_unsafe_media_configuration(self):
        mutated = copy.deepcopy(self.policy)
        mutated["dns"]["media"]["target"] = "public-bucket.r2.dev"
        with self.assertRaises(validate_cloudflare_research.PolicyError):
            validate_cloudflare_research.validate(mutated)

        mutated = copy.deepcopy(self.policy)
        mutated["access"]["allow_email"] = ["reviewer@example.invalid"]
        with self.assertRaises(validate_cloudflare_research.PolicyError):
            validate_cloudflare_research.validate(mutated)

        mutated = copy.deepcopy(self.policy)
        mutated["access"]["origin_jwt_validation"]["algorithms"] = ["HS256"]
        with self.assertRaises(validate_cloudflare_research.PolicyError):
            validate_cloudflare_research.validate(mutated)

    def test_probe_script_requires_fixed_hostnames_and_explicit_origin_gate(self):
        script = (
            Path(__file__).resolve().parents[2]
            / "scripts"
            / "check_cloudflare_research.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("https://research.tread-joy.com/*", script)
        self.assertIn("https://media.research.tread-joy.com/*", script)
        self.assertIn('REQUIRE_ORIGIN_CHECK=true requires ORIGIN_URL', script)
        self.assertIn('"Cache-Control:" "$static_headers"', script)
        self.assertIn('"Cache-Control:" "$media_headers"', script)
