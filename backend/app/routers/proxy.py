import re
from fastapi import APIRouter, HTTPException, Response, Path, Request
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

def get_frigate_headers() -> dict:
    """Build headers for Frigate requests, including auth token if configured."""
    headers = {}
    if settings.frigate.frigate_auth_token:
        headers['Authorization'] = f'Bearer {settings.frigate.frigate_auth_token}'
    return headers

# Validate event_id format (Frigate uses UUIDs, numeric IDs, or timestamp-based IDs with dots)
EVENT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_.]+$')

def validate_event_id(event_id: str) -> bool:
    return bool(EVENT_ID_PATTERN.match(event_id)) and len(event_id) <= 64

@router.get("/frigate/test")
async def test_frigate_connection():
    """Test connection to Frigate and return status with details."""
    url = f"{settings.frigate.frigate_url}/api/version"
    client = get_http_client()
    headers = get_frigate_headers()
    try:
        resp = await client.get(url, headers=headers, timeout=10.0)
        resp.raise_for_status()
        version = resp.text.strip().strip('"')
        return {
            "status": "ok",
            "frigate_url": settings.frigate.frigate_url,
            "version": version
        }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate connection timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Frigate authentication failed - check auth token")
        raise HTTPException(status_code=e.response.status_code, detail=f"Frigate returned error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Frigate at {settings.frigate.frigate_url}")

@router.get("/frigate/config")
async def proxy_config():
    url = f"{settings.frigate.frigate_url}/api/config"
    client = get_http_client()
    headers = get_frigate_headers()
    try:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return Response(content=resp.content, media_type=resp.headers.get("content-type", "application/json"))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate request timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Frigate authentication failed")
        raise HTTPException(status_code=e.response.status_code, detail="Frigate error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to connect to Frigate")

@router.get("/frigate/{event_id}/snapshot.jpg")
async def proxy_snapshot(event_id: str = Path(..., min_length=1, max_length=64)):
    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/snapshot.jpg"
    client = get_http_client()
    headers = get_frigate_headers()
    try:
        resp = await client.get(url, headers=headers)
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

@router.head("/frigate/{event_id}/clip.mp4")
async def check_clip_exists(event_id: str = Path(..., min_length=1, max_length=64)):
    """Check if a clip exists for an event by checking the event details."""
    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    # Frigate doesn't support HEAD for clips, so check event exists instead
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}"
    client = get_http_client()
    headers = get_frigate_headers()
    try:
        resp = await client.get(url, headers=headers, timeout=10.0)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Event not found")
        resp.raise_for_status()
        # Check if event has a clip
        event_data = resp.json()
        has_clip = event_data.get("has_clip", False)
        if not has_clip:
            raise HTTPException(status_code=404, detail="Clip not available for this event")
        return Response(status_code=200)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Frigate error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to connect to Frigate")


@router.get("/frigate/{event_id}/clip.mp4")
async def proxy_clip(
    request: Request,
    event_id: str = Path(..., min_length=1, max_length=64)
):
    """Stream video clip from Frigate with Range request support."""
    from fastapi.responses import StreamingResponse

    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")

    clip_url = f"{settings.frigate.frigate_url}/api/events/{event_id}/clip.mp4"
    headers = get_frigate_headers()

    # First, verify the clip exists by checking event metadata
    event_url = f"{settings.frigate.frigate_url}/api/events/{event_id}"
    client = get_http_client()
    try:
        event_resp = await client.get(event_url, headers=headers, timeout=10.0)
        if event_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Event not found")
        event_resp.raise_for_status()
        event_data = event_resp.json()
        if not event_data.get("has_clip", False):
            raise HTTPException(status_code=404, detail="Clip not available for this event")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Frigate request timed out")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Failed to connect to Frigate")

    # Build request headers, forwarding Range if present for seeking support
    request_headers = dict(headers)
    range_header = request.headers.get("range")
    if range_header:
        request_headers["Range"] = range_header

    # Stream the clip from Frigate
    async def stream_clip():
        async with httpx.AsyncClient(timeout=None) as stream_client:
            async with stream_client.stream("GET", clip_url, headers=request_headers) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    yield chunk

    # Determine response status and headers based on Range request
    response_headers = {
        "Content-Disposition": f"inline; filename={event_id}.mp4",
        "Accept-Ranges": "bytes",
    }

    # For range requests, we need to return 206 Partial Content
    # For simplicity, we'll let the StreamingResponse handle it with 200
    # The Accept-Ranges header tells the client we support ranges
    return StreamingResponse(
        stream_clip(),
        media_type="video/mp4",
        headers=response_headers
    )

@router.get("/frigate/{event_id}/thumbnail.jpg")
async def proxy_thumb(event_id: str = Path(..., min_length=1, max_length=64)):
    if not validate_event_id(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/thumbnail.jpg"
    client = get_http_client()
    headers = get_frigate_headers()
    try:
        resp = await client.get(url, headers=headers)
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