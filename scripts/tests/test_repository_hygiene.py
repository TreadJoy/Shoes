from unittest import TestCase

from scripts.check_repository_hygiene import path_issues, text_issues


class RepositoryPathHygieneTests(TestCase):
    def test_safe_project_path_passes(self):
        self.assertEqual(path_issues("web/core/views.py"), [])

    def test_generated_and_private_paths_fail(self):
        for path in (
            ".env",
            ".DS_Store",
            "web/__pycache__/views.pyc",
            "deploy/node_modules/package/index.js",
        ):
            with self.subTest(path=path):
                self.assertTrue(path_issues(path))

    def test_outer_whitespace_and_control_characters_fail(self):
        self.assertTrue(path_issues("docs/ bad-name.md"))
        self.assertTrue(path_issues("docs/bad\nname.md"))


class RepositoryTextHygieneTests(TestCase):
    def test_empty_and_binary_files_are_not_treated_as_text(self):
        self.assertEqual(text_issues("empty", b""), [])
        self.assertEqual(text_issues("image.png", b"\x89PNG\x00"), [])

    def test_clean_utf8_text_passes(self):
        self.assertEqual(text_issues("README.md", "TreadJoy\n".encode()), [])

    def test_crlf_missing_newline_and_trailing_whitespace_fail(self):
        crlf = text_issues("file.txt", b"first\r\nsecond\r\n")
        self.assertIn("text file uses CRLF line endings", {item.message for item in crlf})

        missing = text_issues("file.txt", b"no final newline")
        self.assertIn(
            "non-empty text file lacks a final newline",
            {item.message for item in missing},
        )

        trailing = text_issues("file.txt", b"trailing space \n")
        self.assertIn("line 1 has trailing whitespace", {item.message for item in trailing})
