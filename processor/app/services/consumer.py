import json
import logging
import time

import redis
from pydantic import ValidationError

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.repository import RedisRepository
from app.schemas.bike_data import ApiResponse

from .processing import ProcessingService

logger = logging.getLogger(__name__)


class DataConsumer:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.stream_name = settings.REDIS_STREAM_NAME
        self.group_name = settings.REDIS_CONSUMER_GROUP
        self.consumer_name = settings.REDIS_CONSUMER_NAME
        self._ensure_consumer_group()

    def _ensure_consumer_group(self):
        try:
            self.redis_client.xgroup_create(
                name=self.stream_name, groupname=self.group_name, id="0", mkstream=True
            )
            logger.info(f"Consumer group '{self.group_name}' created.")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"Consumer group '{self.group_name}' already exists.")
            else:
                raise

    def run(self):
        logger.info("Starting to listen for messages...")
        while True:
            try:
                messages = self.redis_client.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=1,
                    block=2000,
                )
                if not messages:
                    continue

                for _, msg_list in messages:
                    for msg_id, data in msg_list:
                        self._handle_message(msg_id, data)
            except Exception as e:
                logger.error(f"Error while processing messages: {e}", exc_info=True)
                time.sleep(5)

    def _handle_message(self, msg_id: str, data: dict):
        db = SessionLocal()
        try:
            snapshot = ApiResponse.model_validate_json(data["data"])

            redis_repo = RedisRepository(
                host=settings.REDIS_HOST, port=settings.REDIS_DOCKER_PORT
            )
            processing_service = ProcessingService(db, redis_repo)
            processing_service.process_snapshot(snapshot)

            self.redis_client.xack(self.stream_name, self.group_name, msg_id)
            logger.info(f"Successfully processed and acknowledged message {msg_id}")

            self.redis_client.xtrim(self.stream_name, minid=msg_id)
            logger.info(f"Stream '{self.stream_name}' trimmed up to message {msg_id}")
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error(
                f"Validation/JSON error for message {msg_id}: {e}. Acknowledging to avoid reprocessing."
            )
            self.redis_client.xack(self.stream_name, self.group_name, msg_id)
            self.redis_client.xtrim(self.stream_name, minid=msg_id)
        except Exception as e:
            logger.error(
                f"Failed to process message {msg_id}: {e}. It will be retried."
            )
        finally:
            db.close()
