from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import aiosqlite

@dataclass
class Detection:
    detection_time: datetime
    detection_index: int
    score: float
    display_name: str
    category_name: str
    frigate_event: str
    camera_name: str
    id: Optional[int] = None

class DetectionRepository:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def get_by_frigate_event(self, frigate_event: str) -> Optional[Detection]:
        async with self.db.execute(
            "SELECT id, detection_time, detection_index, score, display_name, category_name, frigate_event, camera_name FROM detections WHERE frigate_event = ?",
            (frigate_event,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                # row[1] is detection_time. sqlite stores as string usually.
                # If it comes back as string, parse it.
                dt = row[1]
                if isinstance(dt, str):
                    try:
                        dt = datetime.fromisoformat(dt)
                    except ValueError:
                        # Fallback or strict error? 
                        # In this app, we trust what we wrote.
                        pass
                
                return Detection(
                    id=row[0],
                    detection_time=dt,
                    detection_index=row[2],
                    score=row[3],
                    display_name=row[4],
                    category_name=row[5],
                    frigate_event=row[6],
                    camera_name=row[7]
                )
            return None

    async def create(self, detection: Detection):
        await self.db.execute("""
            INSERT INTO detections (detection_time, detection_index, score, display_name, category_name, frigate_event, camera_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (detection.detection_time, detection.detection_index, detection.score, detection.display_name, detection.category_name, detection.frigate_event, detection.camera_name))
        await self.db.commit()

    async def update(self, detection: Detection):
        await self.db.execute("""
            UPDATE detections 
            SET detection_time = ?, detection_index = ?, score = ?, display_name = ?, category_name = ?
            WHERE frigate_event = ?
        """, (detection.detection_time, detection.detection_index, detection.score, detection.display_name, detection.category_name, detection.frigate_event))
        await self.db.commit()

    async def get_all(self, limit: int = 50, offset: int = 0) -> list[Detection]:
        async with self.db.execute(
            "SELECT id, detection_time, detection_index, score, display_name, category_name, frigate_event, camera_name FROM detections ORDER BY detection_time DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                dt = row[1]
                if isinstance(dt, str):
                    try:
                        dt = datetime.fromisoformat(dt)
                    except ValueError:
                        pass
                results.append(Detection(
                    id=row[0],
                    detection_time=dt,
                    detection_index=row[2],
                    score=row[3],
                    display_name=row[4],
                    category_name=row[5],
                    frigate_event=row[6],
                    camera_name=row[7]
                ))
            return results

    async def get_species_counts(self) -> list[dict]:
        async with self.db.execute(
            "SELECT display_name, COUNT(*) as count FROM detections GROUP BY display_name ORDER BY count DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"species": row[0], "count": row[1]} for row in rows]
