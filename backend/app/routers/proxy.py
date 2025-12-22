from fastapi import APIRouter, HTTPException, Response
import httpx
from app.config import settings

router = APIRouter()

@router.get("/frigate/{event_id}/snapshot.jpg")
async def proxy_snapshot(event_id: str):
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/snapshot.jpg"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
        except Exception:
            raise HTTPException(status_code=404, detail="Snapshot not found")

@router.get("/frigate/{event_id}/clip.mp4")
async def proxy_clip(event_id: str):
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/clip.mp4"
    async with httpx.AsyncClient() as client:
        try:
            # Note: Streaming proxy is better for large files, but for short clips this is okay for now.
            resp = await client.get(url)
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "video/mp4"))
        except Exception:
             raise HTTPException(status_code=404, detail="Clip not found")

@router.get("/frigate/{event_id}/thumbnail.jpg")
async def proxy_thumb(event_id: str):
    url = f"{settings.frigate.frigate_url}/api/events/{event_id}/thumbnail.jpg"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            return Response(content=resp.content, media_type=resp.headers.get("content-type", "image/jpeg"))
        except Exception:
             raise HTTPException(status_code=404, detail="Thumbnail not found")
