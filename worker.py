import os
import logging

import redis
from rq import Queue, Connection, Worker

from utils import detect_audio_from_file
from storage import LocalStorage, S3Storage
import config

log = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL", config.REDIS_URL)
redis_conn = redis.from_url(redis_url)

q = Queue(connection=redis_conn)


def probe_and_store(task_args):
    """
    Example background task to probe audio and post-process.

    task_args can include:
      - temp_path
      - s3_key
      - storage backend
      - metadata
    """

    # TODO:
    # - Probe audio/video information
    # - Rename/update metadata
    # - Upload to S3 if needed
    # - Clean temporary files
    # - Send notifications

    return {
        "status": "ok"
    }


if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker(["default"])
        worker.work()