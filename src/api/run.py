from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import yaml
from typing import List, Dict, Any

router = APIRouter(prefix="/runs", tags=["runs"])

RUNS_DIR = Path(__file__).parent.parent.parent / "runs"

@router.get("/")
async def get_all_runs() -> List[Dict[str, Any]]:
    runs = []
    
    if not RUNS_DIR.exists():
        return runs
    
    for run_folder in RUNS_DIR.iterdir():
        if run_folder.is_dir() and run_folder.name.startswith("run_"):
            run_details_path = run_folder / "run_details.json"
            
            if run_details_path.exists():
                try:
                    with open(run_details_path, 'r') as f:
                        details = json.load(f)
                    if isinstance(details, dict) and len(details) > 0:
                        detail = details
                        runs.append({
                            "id": run_folder.name,
                            "createdOn": detail.get("createdOn"),
                            "timeElapsed": detail.get("timeElapsed"),
                            "turnNumber": detail.get("turnNumber")
                        })
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading {run_details_path}: {e}")
                    continue
    
    runs.sort(key=lambda x: x.get("createdOn", ""), reverse=True)
    return runs

@router.get("/{run_id}")
async def get_run_details(run_id: str) -> Dict[str, Any]:
    run_folder = RUNS_DIR / run_id
    
    if not run_folder.exists() or not run_folder.is_dir():
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    try:
        transcript_path = run_folder / "messages_log.json"
        transcript = []
        if transcript_path.exists():
            with open(transcript_path, 'r') as f:
                transcript = json.load(f)
        
        requirements_path = run_folder / "requirements_log.json"
        requirements = []
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                requirements = json.load(f)
        
        issues_path = run_folder / "issues_log.json"
        issues = []
        if issues_path.exists():
            with open(issues_path, 'r') as f:
                issues = json.load(f)
        
        clarifications_path = run_folder / "clarifications_log.json"
        clarifications = []
        if clarifications_path.exists():
            with open(clarifications_path, 'r') as f:
                clarifications = json.load(f)

        config_path = run_folder / "config.yaml"
        config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
        
        return {
                "transcript": transcript,
                "requirements": requirements,
                "issues": issues,
                "clarifications": clarifications,
                "config": config
        }
        
    except (json.JSONDecodeError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"Error reading run data: {str(e)}")