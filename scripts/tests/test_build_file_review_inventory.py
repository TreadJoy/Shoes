from pathlib import Path
from unittest import TestCase

from scripts.build_file_review_inventory import classification, is_sensitive_local_file


class FileReviewInventoryClassificationTests(TestCase):
    def test_sensitive_local_files_are_preserved_without_content_review(self):
        self.assertEqual(
            classification(".env", is_tracked=False),
            ("preserve", "private local state; contents deliberately not reviewed"),
        )
        self.assertEqual(
            classification("db.sqlite3", is_tracked=False),
            ("preserve", "private local state; contents deliberately not reviewed"),
        )

    def test_private_environment_variants_and_local_databases_are_not_read(self):
        for path in (".env.local", "data/private.sqlite", "data/private.db"):
            with self.subTest(path=path):
                self.assertTrue(is_sensitive_local_file(path))
        self.assertFalse(is_sensitive_local_file(".env.example"))

    def test_generated_litter_is_marked_for_deletion(self):
        disposition, _reason = classification("static/.DS_Store", is_tracked=False)
        self.assertEqual(disposition, "delete")

    def test_earlier_design_generations_are_archived(self):
        for generation in ("treadjoy-modular-v1", "treadjoy-modular-v2"):
            with self.subTest(generation=generation):
                disposition, _reason = classification(
                    f"design/archive/{generation}/renders/example.png",
                    is_tracked=False,
                )
                self.assertEqual(disposition, "archive")

    def test_current_design_generation_is_reviewed(self):
        disposition, _reason = classification(
            "design/active/treadjoy-heritage-court-v3/README.md",
            is_tracked=False,
        )
        self.assertEqual(disposition, "review")

    def test_development_ai_logo_stays_private(self):
        self.assertEqual(
            classification(
                "media/development/treadjoy-ai-logo.png", is_tracked=False
            ),
            (
                "preserve",
                "development-only placeholder; unapproved for public deployment",
            ),
        )

    def test_reviewed_untracked_phase_files_are_not_left_unresolved(self):
        for path in (
            ".editorconfig",
            "docs/file-review.md",
            "treadjoy/settings.py",
        ):
            with self.subTest(path=path):
                self.assertEqual(
                    classification(path, is_tracked=False),
                    ("review", "current reviewed project file"),
                )

    def test_tracked_files_are_reviewed(self):
        disposition, _reason = classification("web/core/views.py", is_tracked=True)
        self.assertEqual(disposition, "review")

    def test_unknown_ignored_files_require_investigation(self):
        disposition, _reason = classification(
            Path("local/unknown.dat").as_posix(), is_tracked=False
        )
        self.assertEqual(disposition, "investigate")
