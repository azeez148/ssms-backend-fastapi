import asyncio
import os
import sys

# Add the current directory to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from app.services.kafka_consumer import run_kafka_consumer

if __name__ == "__main__":
    try:
        asyncio.run(run_kafka_consumer())
    except KeyboardInterrupt:
        pass
