import os
from dotenv import load_dotenv
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import json
import asyncio

from fastapi.responses import StreamingResponse
from ..services.simulation_service import run_simulation
from ..llm.requirements_enum import PROVIDER_REQUIREMENTS
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

router = APIRouter(prefix="/initiate", tags=["initiate"]) 

simulation_status = {"status": "idle"}

@router.post("/")
async def initiate_simulation(config: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
    for agent in config.get("re_agents", []) + config.get("user_agents", []):
        provider = agent.get("provider")
        requirements = PROVIDER_REQUIREMENTS[provider.upper()]

        if requirements.get('requires_api_key'):
            api_key = agent.get('api_key') or  os.getenv('OPEN_AI_KEY')
            if not api_key or api_key.strip() == "":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Agent provider '{provider}' requires an API key."
                )

    if "scenario" not in config or "scenarioTruths" not in config or "re_agents" not in config or "user_agents" not in config:
        raise HTTPException(
            status_code=400, 
            detail="Missing required fields: scenario, scenarioTruths, re_agents, user_agents"
        )
    
    simulation_status["status"] = "running"
    background_tasks.add_task(run_and_update, config)

    return {
        "message": "Simulation initiated successfully",
        "config": config
    }

async def run_and_update(config: dict):
    try:
        await asyncio.to_thread(run_simulation, config)
        simulation_status["status"] = "completed"
    except Exception as e:
        simulation_status["status"] = "failed"
        simulation_status["error"] = str(e)
        print(f"[Simulation] Failed: {e}")


@router.get("/stream")
async def stream_status():
    async def event_generator():
        while True:
            payload = {"status": simulation_status["status"]}
            
            if simulation_status["status"] == "failed":
                payload["error"] = simulation_status.get("error", "Unknown error")
            
            data = json.dumps(payload)
            yield f"data: {data}\n\n"
            print(f"[Stream] Sent status update: {data}")
            
            if simulation_status["status"] in ("completed", "failed"):
                simulation_status["status"] = "idle"
                simulation_status.pop("error", None)
                break

            await asyncio.sleep(10)

    return StreamingResponse(event_generator(), media_type="text/event-stream")