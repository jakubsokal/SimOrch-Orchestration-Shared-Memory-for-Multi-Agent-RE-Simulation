from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import yaml
from typing import List, Dict, Any

router = APIRouter(prefix="/runs", tags=["runs"])

RUNS_DIR = Path(__file__).parent.parent.parent / "runs"
SCENARIO_DIR = Path(__file__).parent.parent.parent / "scenarios"

@router.get("/")
async def get_all_runs() -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []

    if not RUNS_DIR.exists():
        return runs

    def load_run_details(run_folder: Path) -> Dict[str, Any] | None:
        run_details_path = run_folder / "run_details.json"
        if not run_details_path.exists():
            return None
        try:
            with open(run_details_path, "r", encoding="utf-8") as f:
                details = json.load(f)
            return details if isinstance(details, dict) else None
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading {run_details_path}: {e}")
            return None

    for scenario_folder in RUNS_DIR.iterdir():
        if not scenario_folder.is_dir() or not scenario_folder.name.startswith("scenario_"):
            continue

        for run_folder in scenario_folder.iterdir():
            if not run_folder.is_dir() or not run_folder.name.startswith("run_"):
                continue

            detail = load_run_details(run_folder)
            if not detail:
                continue

            runs.append({
                "id": f"{scenario_folder.name}/{run_folder.name}",
                "scenarioId": scenario_folder.name,
                "runId": run_folder.name,
                "createdOn": detail.get("createdOn"),
                "timeElapsed": detail.get("timeElapsed"),
                "turnNumber": detail.get("turnNumber"),
            })

    for run_folder in RUNS_DIR.iterdir():
        if not run_folder.is_dir() or not run_folder.name.startswith("run_"):
            continue
        detail = load_run_details(run_folder)
        if not detail:
            continue
        runs.append({
            "id": run_folder.name,
            "scenarioId": None,
            "runId": run_folder.name,
            "createdOn": detail.get("createdOn"),
            "timeElapsed": detail.get("timeElapsed"),
            "turnNumber": detail.get("turnNumber"),
        })

    runs.sort(key=lambda x: x.get("createdOn", "") or "", reverse=True)
    return runs

@router.get("/scenarios")
async def get_predefined_scenarios() ->  List[Dict[str, Any]]:
    scenarios = []
    
    if not SCENARIO_DIR.exists():
        return scenarios
    
    for scenario_file in SCENARIO_DIR.iterdir():
        if scenario_file.is_file() and scenario_file.suffix == ".yaml":
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    scenario = yaml.safe_load(f)
                scenarios.append(scenario)
            except (yaml.YAMLError, IOError) as e:
                print(f"Error reading {scenario_file}: {e}")
                continue

    scenarios.sort(key=lambda x: x.get("scenario", {}).get("scenario_name", ""))
    
    return scenarios

def _load_run_folder(run_folder: Path) -> Dict[str, Any]:
    transcript_path = run_folder / "messages_log.json"
    transcript = []
    if transcript_path.exists():
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = json.load(f)

    requirements_path = run_folder / "requirements_log.json"
    requirements = []
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = json.load(f)

    issues_path = run_folder / "issues_log.json"
    issues = []
    if issues_path.exists():
        with open(issues_path, 'r', encoding='utf-8') as f:
            issues = json.load(f)

    clarifications_path = run_folder / "clarifications_log.json"
    clarifications = []
    if clarifications_path.exists():
        with open(clarifications_path, 'r', encoding='utf-8') as f:
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
        "config": config,
    }


@router.get("/{scenario_id}/{run_id}")
async def get_run_details_nested(scenario_id: str, run_id: str) -> Dict[str, Any]:
    run_folder = RUNS_DIR / scenario_id / run_id

    if not run_folder.exists() or not run_folder.is_dir():
        raise HTTPException(status_code=404, detail=f"Run {scenario_id}/{run_id} not found")
    
    try:
        return _load_run_folder(run_folder)
        
    except (json.JSONDecodeError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"Error reading run data: {str(e)}")


@router.get("/{run_id}")
async def get_run_details(run_id: str) -> Dict[str, Any]:
    direct = RUNS_DIR / run_id
    if direct.exists() and direct.is_dir():
        try:
            return _load_run_folder(direct)
        except (json.JSONDecodeError, IOError) as e:
            raise HTTPException(status_code=500, detail=f"Error reading run data: {str(e)}")

    matches: List[Path] = []
    if RUNS_DIR.exists():
        for scenario_folder in RUNS_DIR.iterdir():
            if not scenario_folder.is_dir() or not scenario_folder.name.startswith("scenario_"):
                continue
            candidate = scenario_folder / run_id
            if candidate.exists() and candidate.is_dir():
                matches.append(candidate)

    if not matches:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    if len(matches) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"Run id '{run_id}' is ambiguous across scenarios. Use /runs/{{scenario_id}}/{run_id}.",
        )

    try:
        return _load_run_folder(matches[0])
    except (json.JSONDecodeError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"Error reading run data: {str(e)}")