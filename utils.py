import re
import unicodedata
from datetime import datetime
from typing import Dict, Any
import json
import shutil
import subprocess
from tempfile import NamedTemporaryFile


def sanitize_for_filename(s: Any, replacement: str = "_") -> str:
    if s is None:
        return ""

    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")

    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[ ]", replacement, s)
    s = re.sub(r"{2,}", replacement, s)

    return s[:255]


class SafeFields(dict):
    def __missing__(self, key):
        return ""


def format_name(format_string: str, fields: Dict[str, Any]) -> str:
    data = {}

    for k, v in fields.items():
        if k in ("season", "episode", "audio_channels"):
            try:
                data[k] = int(v) if v not in (None, "") else 0
            except Exception:
                data[k] = 0
        else:
            data[k] = v if v is not None else ""

    if not data.get("uploaded_at"):
        data["uploaded_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")

    if "title" in data:
        data["title"] = sanitize_for_filename(data["title"])

    return format_string.format_map(SafeFields(data))


def detect_audio_from_file(fileobj) -> dict:
    """
    Uses ffprobe (if installed) to detect
    codec, channels and language.
    """

    if not shutil.which("ffprobe"):
        return {}

    try:
        fileobj.seek(0)
    except Exception:
        pass

    with NamedTemporaryFile(delete=True) as tmp:
        fileobj.seek(0)

        while True:
            chunk = fileobj.read(8192)

            if not chunk:
                break

            tmp.write(chunk)

        tmp.flush()

        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            "-select_streams",
            "a",
            tmp.name,
        ]

        try:
            out = subprocess.check_output(
                cmd,
                stderr=subprocess.DEVNULL,
            )

            info = json.loads(out)

            streams = info.get("streams", [])

            if not streams:
                return {}

            audio = streams[0]

            codec = audio.get("codec_name")
            channels = audio.get("channels")

            tags = audio.get("tags", {}) or {}

            language = (
                tags.get("language")
                or tags.get("lang")
                or ""
            )

            return {
                "audio_codec": codec or "",
                "audio_channels": int(channels) if channels else 0,
                "audio_lang": language or "",
            }

        except Exception:
            return {}