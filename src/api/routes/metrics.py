import json

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/real")
async def get_real_metrics():
    """Get the latest real consciousness metrics."""
    try:
        with open("data/monitor/real_metrics.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Metrics not available yet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
