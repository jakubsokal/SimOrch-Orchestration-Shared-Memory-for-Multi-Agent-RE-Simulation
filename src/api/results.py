from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Any, Dict, List
import json
import datetime

router = APIRouter(prefix="/results", tags=["results"])

PROJECT_ROOT = Path(__file__).parent.parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

@router.get("/")
async def list_results() -> List[Dict[str, Any]]:
    if not RESULTS_DIR.exists():
        return []

    items: List[Dict[str, Any]] = []

    for file in RESULTS_DIR.iterdir():
        if not file.is_file() or file.suffix.lower() != ".json":
            continue

        stat = file.stat()

        created_on = "N/A"
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            generated_at = data.get("generated_at") if isinstance(data, dict) else None
            if isinstance(generated_at, str) and generated_at.strip():
                datetime.datetime.fromisoformat(generated_at)
                created_on = generated_at
        except (OSError, json.JSONDecodeError, ValueError):
            created_on = "N/A"

        items.append(
            {
                "id": file.name,
                "createdOn": created_on,
                "sizeBytes": stat.st_size,
            }
        )

    items.sort(key=lambda x: x.get("_createdSort", "") or "", reverse=True)
    for item in items:
        item.pop("_createdSort", None)
    return items


@router.get("/{result_id}")
async def get_result(result_id: str) -> Dict[str, Any]:
    if "/" in result_id or "\\" in result_id:
        raise HTTPException(status_code=400, detail="Invalid result id")

    if not result_id.endswith(".json"):
        raise HTTPException(status_code=400, detail="Result id must end with .json")

    path = RESULTS_DIR / result_id
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"Result {result_id} not found")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {result_id}: {str(e)}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to read {result_id}: {str(e)}")
