import json
import asyncio
import threading
from datetime import datetime
from aiokafka import AIOKafkaProducer
from app.core.config import settings
from app.core.logging import logger

class KafkaJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class KafkaProducerService:
    def __init__(self):
        self.producer = None
        self._loop = None
        self._lock = threading.Lock()

    async def start(self):
        with self._lock:
            if self.producer is None:
                self._loop = asyncio.get_running_loop()
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v, cls=KafkaJSONEncoder).encode('utf-8')
                )
                await self.producer.start()
                logger.info("Kafka Producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka Producer stopped")

    async def send_message(self, topic: str, message: dict):
        if self.producer is None:
            await self.start()
        try:
            await self.producer.send_and_wait(topic, message)
            logger.info(f"Message sent to topic {topic}: {message['event_type']}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")

    def send_message_sync(self, topic: str, message: dict):
        """
        Thread-safe way to send message from sync code.
        """
        if self.producer is None:
            # This is problematic if called from sync code before start() is called in async context.
            # But in FastAPI, we'll call start() on startup.
            logger.error("Kafka Producer not started. Cannot send message sync.")
            return

        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.send_message(topic, message), self._loop)
        else:
            logger.error("No running event loop found for Kafka Producer.")

kafka_producer = KafkaProducerService()
