import yaml

class LoadScenario:
    def load(file):
        path = f'scenarios/{file}'
        with open(path) as f:
            return yaml.safe_load(f)