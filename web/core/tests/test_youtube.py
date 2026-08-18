from django.test import SimpleTestCase

from web.core.youtube import build_homepage_video, extract_youtube_video_id


class YoutubeConfigurationTests(SimpleTestCase):
    def test_accepts_id_and_supported_https_url_shapes(self):
        values = (
            "dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/live/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        )

        for value in values:
            with self.subTest(value=value):
                self.assertEqual(
                    extract_youtube_video_id(value),
                    "dQw4w9WgXcQ",
                )

    def test_rejects_untrusted_or_malformed_values(self):
        values = (
            "",
            "not a video",
            "http://youtu.be/dQw4w9WgXcQ",
            "https://example.com/dQw4w9WgXcQ",
            "https://youtube.example.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=too-short",
        )

        for value in values:
            with self.subTest(value=value):
                self.assertIsNone(extract_youtube_video_id(value))

    def test_builds_only_privacy_enhanced_embed_url(self):
        video = build_homepage_video(
            "dQw4w9WgXcQ",
            "  TreadJoy product story  ",
        )

        self.assertEqual(video.title, "TreadJoy product story")
        self.assertEqual(
            video.embed_url,
            "https://www.youtube-nocookie.com/embed/"
            "dQw4w9WgXcQ?autoplay=1&rel=0",
        )
