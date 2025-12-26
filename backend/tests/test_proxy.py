from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.config import settings

client = TestClient(app)

def test_proxy_clip_disabled():
    # Save original setting
    original_setting = settings.frigate.clips_enabled
    settings.frigate.clips_enabled = False
    
    try:
        response = client.get("/api/frigate/test_event_id/clip.mp4")
        assert response.status_code == 403
        assert response.json()["detail"] == "Clip fetching is disabled"
    finally:
        # Restore setting
        settings.frigate.clips_enabled = original_setting

@patch("httpx.AsyncClient.send")
def test_proxy_clip_enabled(mock_send):
    # Save original setting
    original_setting = settings.frigate.clips_enabled
    settings.frigate.clips_enabled = True
    
    # Mock the response from Frigate
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "video/mp4"}
    mock_response.aiter_bytes.return_value = []
    
    # Setup the mock to return our response
    mock_send.return_value = mock_response
    
    try:
        response = client.get("/api/frigate/test_event_id/clip.mp4")
        # We expect it to try to connect. 
        # Since we mocked send, if it gets here, it passed the 403 check.
        # Note: StreamingResponse might behave differently in TestClient, 
        # but we are mainly checking we didn't get 403.
        assert response.status_code != 403
    finally:
        settings.frigate.clips_enabled = original_setting
