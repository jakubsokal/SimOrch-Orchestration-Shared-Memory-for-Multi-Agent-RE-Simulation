import json, os

class Logger:
    def __init__(self):
        os.makedirs("runs", exist_ok=True)
        run_number = len(os.listdir("runs")) + 1
        self.run_dir = os.path.join("runs", f"run_{run_number:03d}")
        
        os.makedirs(self.run_dir, exist_ok=True)

    def store(self, memory):
        with open(f"{self.run_dir}/messages_log.json", "w") as f:
            json.dump(memory, f, indent=2)