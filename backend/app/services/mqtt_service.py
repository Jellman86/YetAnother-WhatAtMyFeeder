import asyncio
import json
import structlog
from aiomqtt import Client, MqttError
from app.config import settings

log = structlog.get_logger()

class MQTTService:
    def __init__(self):
        self.client = None
        self.running = False

    async def start(self, message_callback):
        self.running = True
        while self.running:
            try:
                async with Client(
                    hostname=settings.frigate.mqtt_server,
                    port=settings.frigate.mqtt_port,
                    username=settings.frigate.mqtt_username,
                    password=settings.frigate.mqtt_password,
                ) as client:
                    self.client = client
                    topic = f"{settings.frigate.main_topic}/events"
                    await client.subscribe(topic)
                    await log.info("Connected to MQTT", topic=topic)

                    async for message in client.messages:
                        await message_callback(message.payload)
            except MqttError as e:
                await log.error("MQTT connection lost", error=str(e))
                await asyncio.sleep(5)  # Reconnect delay
            except Exception as e:
                await log.error("Unexpected error in MQTT service", error=str(e))
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False
        if self.client:
            # aiomqtt client context manager handles disconnect, but we can break the loop
            pass
