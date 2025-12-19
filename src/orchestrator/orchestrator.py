import logs.logger as logger
import memory.shared_memory as shared_memory
class Orchestrator:
    def __init__(self, agents, max_turns=3):
        self.agents = agents
        self.shared_memory = shared_memory.SharedMemory()
        self.max_turns = max_turns
        
    def start(self):
        last_message = None
        role = None

        for turn in range(self.max_turns): 
            for name, agent in self.agents.items():
                mem = self.shared_memory.read()

                if len(mem) > 0:
                    last_message = mem[turn - 1]["message"]
                    role = mem[turn - 1]["role"]
                
                reply = agent.speak(last_message, role)

                self.shared_memory.write(name, reply, turn + 1, agent.role)
            
            print(f"[Turn {turn + 1}] Finished")

        logger.Logger().store(self.shared_memory.read())