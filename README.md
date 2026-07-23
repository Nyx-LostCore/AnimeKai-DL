# AnimeKai-DL — Renamer & Metadata Service (Scaffold)

Quick: FastAPI app to accept uploads, rename using configurable format, store metadata, optional S3, audio autodetect (ffprobe), background worker (RQ + Redis), presigned upload skeleton.

## Features

- FastAPI backend
- Configurable rename format
- Metadata database (SQLModel)
- Optional S3 storage
- Local storage support
- Audio detection using ffprobe
- Background worker using Redis + RQ
- Docker & Docker Compose support
- GitHub Actions CI

## API Endpoints

### Upload

POST `/upload`

Uploads and renames a file.

### Metadata

POST `/api/metadata`

Create metadata.

GET `/api/metadata/search?q=...`

Search metadata.

GET `/api/metadata/{id}`

Get metadata.

## Local Setup

1. Copy `.env.example` to `.env`

2. Edit your environment variables.

3. Run

```bash
docker-compose up --build
```

4. Visit

```
http://localhost:8000/docs
```

## Security

- Protect production endpoints.
- Never commit secrets.
- Store API keys in deployment secrets.

## License

MIT
