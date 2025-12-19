import datetime

class SharedMemory:
    def __init__(self):
        self.messages = []

    def write(self, name: str, message: str, turn: int, role: str = "agent"):
        self.messages.append({
            "turn": turn,
            "agent": name,
            "role": role,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat()
            })
        
    def read(self):
        return self.messages