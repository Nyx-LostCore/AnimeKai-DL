import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional
from db import init_db, get_session
from sqlmodel import Session
from models import AnimeMetadata
import config
from utils import sanitize_for_filename, format_name, detect_audio_from_file
from storage import LocalStorage, S3Storage
import requests

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(title="AnimeKai-DL")

@app.on_event("startup")
def on_startup():
    init_db()

storage = S3Storage() if config.USE_S3 else LocalStorage()

def get_api_key(header_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    key = header_api_key or ""
    if not key and authorization and authorization.lower().startswith("bearer "):
        key = authorization.split(" ", 1)[1]
    if config.API_KEY and key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@app.post("/upload", dependencies=[Depends(get_api_key)])
async def upload(
    file: UploadFile = File(...),
    metadata_id: Optional[int] = Form(None),
    title: Optional[str] = Form(None),
    season: Optional[int] = Form(None),
    episode: Optional[int] = Form(None),
    quality: Optional[str] = Form(None),
    audio_codec: Optional[str] = Form(None),
    audio_channels: Optional[int] = Form(None),
    audio_lang: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    if file.filename is None:
        raise HTTPException(400, "No filename provided")
    orig_ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
    if orig_ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Extension .{orig_ext} not allowed")

    meta = session.get(AnimeMetadata, metadata_id) if metadata_id else None
    if metadata_id and not meta:
        raise HTTPException(404, "metadata_id not found")

    title_val = title or (meta.title if meta else os.path.splitext(file.filename)[0])
    season_val = season if season is not None else (meta.season if meta and meta.season is not None else 0)
    quality_val = quality or (meta.default_quality if meta else "")
    episode_val = episode or 0

    audio = {"audio_codec": audio_codec or "", "audio_channels": int(audio_channels) if audio_channels else 0, "audio_lang": audio_lang or ""}
    if config.AUTO_DETECT_AUDIO and (not audio["audio_codec"] or not audio["audio_channels"]):
        try:
            file.file.seek(0)
            detected = detect_audio_from_file(file.file)
            file.file.seek(0)
            audio.update({k:v for k,v in detected.items() if v})
        except Exception as e:
            log.warning("audio detect failed: %s", e)

    fields = {"title": title_val,"season": season_val,"episode": episode_val,"quality": quality_val,"ext": orig_ext,
              "audio_codec": sanitize_for_filename(audio["audio_codec"]),
              "audio_channels": audio["audio_channels"],
              "audio_lang": sanitize_for_filename(audio["audio_lang"])}
    name = sanitize_for_filename(format_name(config.NAME_FORMAT, fields))
    if not name.lower().endswith(f".{orig_ext}"):
        name += "." + orig_ext
    prefix = config.ONGOING_PREFIX if meta and (meta.status or "").lower()=="ongoing" else ""
    file.file.seek(0)
    saved = storage.save_with_collision_resolution(file.file, name, prefix=prefix)

    if meta and (meta.status or "").lower()=="ongoing" and config.ONGOING_NOTIFY and config.DISCORD_WEBHOOK_URL:
        try:
            requests.post(config.DISCORD_WEBHOOK_URL,json={"content":f"New episode uploaded: **{name}**"},timeout=5)
        except Exception as e:
            log.warning("notify failed: %s", e)

    return JSONResponse({"original_filename": file.filename, "saved_as": name, "path": saved})

from api.metadata import router as metadata_router
app.include_router(metadata_router)

@app.get("/health")
def health():
    return {"status":"ok"}
