from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.services.broadcaster import broadcaster
import json
import asyncio

router = APIRouter()

@router.get("/sse")
async def sse_stream():
    async def event_generator():
        queue = await broadcaster.subscribe()
        try:
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            await broadcaster.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
