import io
import json

from vedit.sources import github, tiktok, youtube


def test_tiktok_hashtags():
    assert tiktok.hashtags("Quán xịn #cafe #SàiGòn #cafe nhé") == ["#SàiGòn", "#cafe"]


def test_github_search_parses(monkeypatch):
    payload = {"items": [{"full_name": "a/b", "description": "x" * 400, "stargazers_count": 5, "language": "Python",
                          "topics": ["video"], "pushed_at": "2026-01-02T00:00:00Z", "html_url": "https://github.com/a/b"}]}
    seen = {}

    def fake_request(path, token, accept="application/vnd.github+json"):
        seen["path"] = path
        return json.dumps(payload).encode()

    monkeypatch.setattr(github, "_request", fake_request)
    result = github.search_repositories("video editing", limit=3, sort=None)
    assert result[0]["repo"] == "a/b" and len(result[0]["description"]) == 300 and result[0]["updated"] == "2026-01-02"
    assert "sort=" not in seen["path"] and "per_page=3" in seen["path"]


def test_youtube_caption_parsing(monkeypatch):
    json3 = {"events": [{"tStartMs": 1000, "segs": [{"utf8": "xin "}, {"utf8": "chào"}]}, {"tStartMs": 2000}]}
    vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<c>dòng một</c>\n\n00:00:02.000 --> 00:00:03.000\ndòng một\ndòng hai\n"

    def fake_urlopen(req, timeout=30):
        return io.BytesIO((json.dumps(json3) if "json3" in req.full_url else vtt).encode())

    monkeypatch.setattr(youtube.urllib.request, "urlopen", fake_urlopen)
    assert youtube._caption_text("json3", "https://x/json3") == "[1s] xin chào"
    assert youtube._caption_text("vtt", "https://x/vtt") == "dòng một\ndòng hai"
    info = {"automatic_captions": {"vi-orig": [{"ext": "vtt", "url": "u1"}, {"ext": "json3", "url": "u2"}]}}
    assert youtube._pick_caption(info, ("vi", "en")) == ("json3", "u2")
