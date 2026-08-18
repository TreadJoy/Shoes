import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


YOUTUBE_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
}
YOUTUBE_SHORT_HOSTS = {
    "youtu.be",
    "www.youtu.be",
}


@dataclass(frozen=True)
class HomepageVideo:
    video_id: str
    title: str

    @property
    def embed_url(self):
        return (
            "https://www.youtube-nocookie.com/embed/"
            f"{self.video_id}?autoplay=1&rel=0"
        )


def extract_youtube_video_id(value):
    """Return a safe video ID from an ID or supported HTTPS YouTube URL."""
    candidate = value.strip()
    if not candidate:
        return None

    if YOUTUBE_VIDEO_ID_PATTERN.fullmatch(candidate):
        return candidate

    parsed = urlparse(candidate)
    if parsed.scheme != "https" or parsed.username or parsed.password:
        return None

    hostname = (parsed.hostname or "").lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    if hostname in YOUTUBE_SHORT_HOSTS and len(path_parts) == 1:
        candidate = path_parts[0]
    elif hostname in YOUTUBE_HOSTS:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [""])[0]
        elif len(path_parts) == 2 and path_parts[0] in {
            "embed",
            "live",
            "shorts",
        }:
            candidate = path_parts[1]
        else:
            return None
    else:
        return None

    if YOUTUBE_VIDEO_ID_PATTERN.fullmatch(candidate):
        return candidate

    return None


def build_homepage_video(value, title=""):
    video_id = extract_youtube_video_id(value)
    if not video_id:
        return None

    return HomepageVideo(
        video_id=video_id,
        title=title.strip() or "TreadJoy video",
    )
