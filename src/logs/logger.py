import json
import yaml
from pathlib import Path

class Logger:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        runs_path = project_root / "runs"
        
        print(f"[Logger] Creating run directory in: {runs_path}")
        runs_path.mkdir(exist_ok=True)

        run_number = len(list(runs_path.iterdir())) + 1
        print(f"[Logger] This is run number: {run_number:03d}")
        self.run_dir = runs_path / f"run_{run_number:03d}"
        
        self.run_dir.mkdir(exist_ok=True)
        
    def store_yaml(self, yaml_content):
        with open(f"{self.run_dir}/config.yaml", "w") as f:
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)

    def store_run_details(self, timestamp, turn_number, time_elapsed, seed=None):
        details = {
            "createdOn": timestamp,
            "timeElapsed": time_elapsed,
            "turnNumber": turn_number - 1,
            "seed": seed,
            "reproducible": seed is not None
        }
        with open(f"{self.run_dir}/run_details.json", "w") as f:
            json.dump(details, f, indent=2)

    def store(self, memory, requirements=[], issues=[]):
        with open(f"{self.run_dir}/messages_log.json", "w") as f:
            json.dump(memory, f, indent=2)

        if requirements:
            with open(f"{self.run_dir}/requirements_log.json", "w") as f:
                json.dump(requirements, f, indent=2)
        if issues:
            with open(f"{self.run_dir}/issues_log.json", "w") as f:
                json.dump(issues, f, indent=2)