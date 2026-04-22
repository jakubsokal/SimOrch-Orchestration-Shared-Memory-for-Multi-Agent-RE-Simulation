import json
import yaml
from pathlib import Path

class Logger:
    def __init__(self, scenario_id: str = None):
        self.project_root = Path(__file__).resolve().parents[2]
        self.scenarios_dir = self.project_root / "scenarios"
        self.scenarios_dir.mkdir(exist_ok=True)

        project_root = self.project_root
        if scenario_id:
            if not scenario_id.startswith("scenario_"):
                scenario_id = f"scenario_{scenario_id}"
            runs_path = project_root / "runs" / scenario_id
        else:
            runs_path = project_root / "runs"
        
        
        print(f"[Logger] Creating run directory in: {runs_path}")
        runs_path.mkdir(exist_ok=True, parents=True)

        run_number = len(list(runs_path.iterdir())) + 1
        print(f"[Logger] This is run number: {run_number:03d}")
        self.run_dir = runs_path / f"run_{run_number:03d}"
        
        self.run_dir.mkdir(exist_ok=True)

    def scenario_exists(self, scenario_id: str) -> bool:
        if not scenario_id:
            print(f"[Logger] No scenario ID provided, skipping scenario existence check.")
            return False
        if not scenario_id.startswith("scenario_"):
            scenario_id = f"scenario_{scenario_id}"

        print(f"[Logger] Checking if scenario YAML exists for scenario ID: {scenario_id} - {(self.scenarios_dir / f"{scenario_id}.yaml").exists()}")
        return (self.scenarios_dir / f"{scenario_id}.yaml").exists()
        
    def store_yaml(self, yaml_content):
        yaml_content.pop("api_key", None)
        scenario_id = yaml_content.get("scenario", {}).get("id", None)
        exists = self.scenario_exists(scenario_id);
        print(f"[Logger] Storing YAML for scenario ID: {scenario_id} - Exists: {exists}")
        if not exists:
            
            print(f"[Logger] Storing scenario YAML for scenario ID: {scenario_id}")
            with open(self.scenarios_dir / f"{scenario_id}.yaml", "w", encoding="utf-8") as f:
                yaml.safe_dump(yaml_content, f, default_flow_style=False, sort_keys=False)
         
        with open(f"{self.run_dir}/config.yaml", "w") as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)

    def store_run_details(self, timestamp, turn_number, time_elapsed, seed=None, successful=True, status=None, error=None):
        if status is None:
            status = "completed" if successful else "failed"

        details = {
            "createdOn": timestamp,
            "timeElapsed": time_elapsed,
            "turnNumber": turn_number - 1,
            "seed": seed,
            "reproducible": seed is not None,
            "successful": successful,
            "status": status,
        }

        if error is not None:
            details["error"] = str(error)

        with open(f"{self.run_dir}/run_details.json", "w") as f:
            json.dump(details, f, indent=2)

    def store(self, memory, requirements=[], issues=[]):
        with open(f"{self.run_dir}/messages_log.json", "w") as f:
            json.dump(memory, f, indent=2)

        with open(f"{self.run_dir}/requirements_log.json", "w") as f:
            json.dump(requirements, f, indent=2)

        with open(f"{self.run_dir}/issues_log.json", "w") as f:
            json.dump(issues, f, indent=2)