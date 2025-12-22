import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.event_processor import EventProcessor

@pytest.mark.asyncio
async def test_process_mqtt_message_valid_bird():
    # Mock classifier
    classifier = MagicMock()
    classifier.classify.return_value = [{"label": "Cardinal", "score": 0.95, "index": 1}]
    
    # Mock EventProcessor methods/dependencies
    processor = EventProcessor(classifier)
    processor.http_client.get = AsyncMock()
    processor.http_client.get.return_value = MagicMock(status_code=200, content=b"fakeimage")
    processor.http_client.post = AsyncMock()
    
    # Mock DB interaction (This is harder without dependency injection or mocking get_db)
    # Ideally checking side effects or using a test DB. 
    # For unit test, we might want to mock the _save_detection method if we can't easily mock the context manager.
    processor._save_detection = AsyncMock() 
    processor._set_sublabel = AsyncMock()

    payload = b'{"after": {"id": "123", "label": "bird", "camera": "cam1", "start_time": 1700000000}}'
    
    await processor.process_mqtt_message(payload)
    
    processor._save_detection.assert_called_once()
    processor._set_sublabel.assert_called_with("123", "Cardinal")

@pytest.mark.asyncio
async def test_process_mqtt_message_ignore_non_bird():
    classifier = MagicMock()
    processor = EventProcessor(classifier)
    
    payload = b'{"after": {"id": "124", "label": "person", "camera": "cam1"}}'
    await processor.process_mqtt_message(payload)
    
    classifier.classify.assert_not_called()
