import json
from typing import Any
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from asyncpg import Connection

from app.db.database import get_db

router = APIRouter()

class StandardData(BaseModel):
    user_id: UUID
    ended_at: datetime | None = None
    measurement: dict[str, Any]

@router.post("/create")
async def create_pose(
    data: StandardData,
    db: Connection = Depends(get_db)
):
    try:
        # asyncpg requires native python types or json string for JSONB
        row = await db.fetchrow(
            """
            INSERT INTO pose (user_id, ended_at, measurement)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            data.user_id,
            data.ended_at,
            json.dumps(data.measurement)
        )
        
        if not row:
            raise HTTPException(status_code=500, detail="Failed to create pose")
            
        return {"id": str(row["id"])}
        
    except Exception as e:
        print(f"Error creating pose: {e}")
        raise HTTPException(status_code=500, detail=str(e))
