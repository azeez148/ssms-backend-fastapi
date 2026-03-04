import json
import asyncio
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.core.logging import logger
from app.schemas.kafka_events import KafkaEvent, KafkaEventType
from app.services.notification import EmailNotificationService, PushNotificationService

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.email_service = EmailNotificationService()
        self.push_service = PushNotificationService()

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_NOTIFICATIONS,
            settings.KAFKA_TOPIC_REPORTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        await self.consumer.start()
        logger.info("Kafka Consumer started")
        try:
            async for msg in self.consumer:
                await self.process_message(msg)
        finally:
            await self.stop()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka Consumer stopped")

    async def process_message(self, msg):
        try:
            event_data = msg.value
            event = KafkaEvent(**event_data)
            logger.info(f"Processing event: {event.event_type}")

            # Run synchronous notification handlers in a threadpool to avoid blocking event loop
            loop = asyncio.get_running_loop()

            if event.event_type == KafkaEventType.SALE_CREATED:
                await loop.run_in_executor(None, self.email_service.send_sale_notification, event.payload)
                await loop.run_in_executor(None, self.push_service.notify_sale_event, event.event_type, event.payload)
            elif event.event_type in [KafkaEventType.SALE_UPDATED, KafkaEventType.SALE_CANCELLED, KafkaEventType.SALE_DELETED]:
                await loop.run_in_executor(None, self.push_service.notify_sale_event, event.event_type, event.payload)
            elif event.event_type == KafkaEventType.PURCHASE_CREATED:
                await loop.run_in_executor(None, self.email_service.send_purchase_notification, event.payload)
            elif event.event_type == KafkaEventType.DAY_SUMMARY_GENERATED:
                await loop.run_in_executor(None, self.email_service.send_day_summary_notification, event.payload)
            elif event.event_type in [KafkaEventType.DAY_STARTED, KafkaEventType.DAY_ENDED, KafkaEventType.EXPENSE_ADDED]:
                await loop.run_in_executor(None, self.push_service.notify_day_event, event.event_type, event.payload)
            # ... handle other event types

        except Exception as e:
            logger.error(f"Error processing Kafka message: {e}")

async def run_kafka_consumer():
    consumer_service = KafkaConsumerService()
    await consumer_service.start()

if __name__ == "__main__":
    asyncio.run(run_kafka_consumer())
