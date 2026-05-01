import asyncio
import os
import re
from pathlib import Path
from uuid import uuid4

import yt_dlp

from .queue import Track


URL_RE = re.compile(r"^https?://", re.I)


def _duration_text(seconds: int | None) -> str:
    if not seconds:
        return "unknown"
    mins, sec = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    if hrs:
        return f"{hrs}:{mins:02d}:{sec:02d}"
    return f"{mins}:{sec:02d}"


async def download_track(query: str, download_dir: str, requested_by: str) -> Track:
    return await asyncio.to_thread(_download_track_sync, query, download_dir, requested_by)


def _download_track_sync(query: str, download_dir: str, requested_by: str) -> Track:
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    target = str(Path(download_dir) / f"{uuid4().hex}.%(ext)s")
    source = query if URL_RE.match(query) else f"ytsearch1:{query}"

    opts = {
        "format": "bestaudio/best",
        "outtmpl": target,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(source, download=True)
        if "entries" in info:
            info = info["entries"][0]

    file_path = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
    if not file_path.exists():
        matches = sorted(Path(download_dir).glob(f"{file_path.stem}.*"), key=os.path.getmtime)
        if not matches:
            raise RuntimeError("Audio download finished but output file was not found.")
        file_path = matches[-1]

    return Track(
        title=info.get("title", "Unknown title"),
        url=info.get("webpage_url", query),
        duration=info.get("duration"),
        file_path=str(file_path),
        requested_by=requested_by,
    )


def format_track(track: Track) -> str:
    return f"{track.title} ({_duration_text(track.duration)})"
