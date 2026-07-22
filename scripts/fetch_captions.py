#!/usr/bin/env python3
"""YouTube URL에서 제목·채널·자막 텍스트를 추출해 JSON으로 출력한다.

사용법: python3 fetch_captions.py <youtube_url>
출력(JSON): {video_id, url, title, channel, language, text}
실패 시 exit 1, stderr에 사유.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def video_id_of(url: str) -> str:
    p = urlparse(url.strip())
    host = p.netloc.lower().removeprefix("www.")
    vid = ""
    if host == "youtu.be":
        vid = p.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if p.path == "/watch":
            vid = parse_qs(p.query).get("v", [""])[0]
        elif p.path.startswith(("/shorts/", "/live/", "/embed/")):
            vid = p.path.strip("/").split("/")[1]
    if not VIDEO_ID_RE.fullmatch(vid):
        sys.exit(f"유효한 YouTube URL이 아님: {url}")
    return vid


def parse_vtt(value: str) -> str:
    lines, previous = [], ""
    for raw in value.splitlines():
        line = re.sub(r"<[^>]+>", "", raw).strip()
        if (not line or line == "WEBVTT" or "-->" in line or line.isdigit()
                or line.startswith(("Kind:", "Language:", "NOTE"))):
            continue
        line = " ".join(line.replace("&nbsp;", " ").replace("&amp;", "&").split())
        if line != previous:
            lines.append(line)
            previous = line
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("사용법: fetch_captions.py <youtube_url>")
    vid = video_id_of(sys.argv[1])
    url = f"https://www.youtube.com/watch?v={vid}"

    info_raw = subprocess.run(
        ["yt-dlp", "--no-playlist", "--skip-download", "--dump-single-json", url],
        capture_output=True, text=True, timeout=120,
    )
    if info_raw.returncode != 0:
        sys.exit(f"영상 정보 조회 실패: {info_raw.stderr.strip().splitlines()[-1:]}")
    info = json.loads(info_raw.stdout.strip().splitlines()[-1])

    available: set[str] = set()
    for field in ("subtitles", "automatic_captions"):
        if isinstance(info.get(field), dict):
            available.update(info[field])
    language = next(
        (l for l in ("ko-orig", "ko", "en-orig", "en") if l in available),
        next((l for l in sorted(available) if l.startswith(("ko", "en"))), ""),
    )
    if not language:
        sys.exit("한국어/영어 자막이 없는 영상")

    with tempfile.TemporaryDirectory(prefix="yt2note-") as d:
        sub = subprocess.run(
            ["yt-dlp", "--no-playlist", "--skip-download", "--write-subs",
             "--write-auto-subs", "--sub-langs", language, "--sub-format", "vtt",
             "-o", f"{d}/%(id)s.%(ext)s", url],
            capture_output=True, text=True, timeout=180,
        )
        if sub.returncode != 0:
            sys.exit(f"자막 다운로드 실패: {sub.stderr.strip().splitlines()[-1:]}")
        files = sorted(Path(d).glob(f"{vid}.{language}*.vtt"))
        if not files:
            sys.exit("자막 파일이 생성되지 않음")
        text = parse_vtt(files[0].read_text(encoding="utf-8"))

    if len(text) < 200:
        sys.exit(f"자막이 너무 짧음({len(text)}자) — 처리 중단")

    json.dump(
        {"video_id": vid, "url": url, "title": info.get("title", ""),
         "channel": info.get("channel") or info.get("uploader", ""),
         "language": language, "text": text},
        sys.stdout, ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
