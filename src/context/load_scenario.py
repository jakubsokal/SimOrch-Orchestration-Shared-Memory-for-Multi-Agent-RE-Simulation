import yaml
from pathlib import Path
import argparse

class LoadScenario:
    def load(file):
        scenario_path = Path(__file__).resolve().parents[2] / 'scenarios'
        
        path = scenario_path / file

        print(f"[Context] Attempting to load scenario from {Path(__file__).resolve().parents[2]}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as e:
            print(f"[Context] Failed to load scenario from {path}: {e}")
            return e
        print(f"[Context] Loaded scenario from {path}")
        
    def args_load():
        parser = argparse.ArgumentParser(description='Load scenario configuration')
        parser.add_argument('--config', type=str, required=True, help='Path to scenario configuration file')
        
        try:
            args = parser.parse_args()
        except Exception as e:
            print(f"[Context] Failed to parse args: {e}")
            return e

        print(f"[Context] Loaded args: {args}")
        return args