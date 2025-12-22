import re
from fastapi import APIRouter, HTTPException, Response, Path
import httpx
from app.config import settings

router = APIRouter()

# Shared HTTP client for better connection pooling
_http_client: httpx.AsyncClient | None = None

def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client

# Validate event_id format (Frigate uses UUIDs or numeric IDs)
EVENT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]+$')

def validate_event_id(event_id: str) -> bool:
    return bool(EVENT_ID_PATTERN.match(event_id)) and len(event_id) <= 64

@router.get("/frigate/{event_id}/snapshot.jpg")
async def proxy_snapshot(event_id: str = Path(..., min_length=1, max_length=64)):
    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/snapshot.jpg"
    client = get_http_client()
    try:
        resp = await client.get(url)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        resp.raise_for_status()
        return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Frigate error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to connect to Frigate")

@router.get("/frigate/{event_id}/clip.mp4")
async def proxy_clip(event_id: str = Path(..., min_length=1, max_length=64)):
    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/clip.mp4"
    client = get_http_client()
    try:
        # Note: Streaming proxy is better for large files, but for short clips this is okay for now.
        resp = await client.get(url, timeout=60.0)  # Longer timeout for video
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Clip not found")
        resp.raise_for_status()
        return Response(content=resp.content, media_type=resp.headers.get("content-type", "video/mp4"))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Frigate error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to connect to Frigate")

@router.get("/frigate/{event_id}/thumbnail.jpg")
async def proxy_thumb(event_id: str = Path(..., min_length=1, max_length=64)):
    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/thumbnail.jpg"
    client = get_http_client()
    try:
        resp = await client.get(url)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        resp.raise_for_status()
        return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Frigate error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to connect to Frigate")
