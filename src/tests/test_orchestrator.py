import unittest, sys, os, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from orchestrator.orchestrator import Orchestrator
from memory.shared_memory import SharedMemory
from agents.re_agent import REAgent
from agents.user_agent import UserAgent
from logs.logger import Logger

class TestExample(unittest.TestCase):
    def setUp(self):
        self.memory = SharedMemory()
        self.re_agent = REAgent("RE")
        self.user_agent = UserAgent("User")
        self.logger = Logger()
        self.orchestrator = Orchestrator(
            agents={
                self.re_agent.name: self.re_agent,
                self.user_agent.name: self.user_agent
            },
            shared_memory=self.memory,
            logger=self.logger
        )
    
    def tearDown(self):
        self.memory = None
        self.orchestrator = None
        self.re_agent = None
        self.user_agent = None
        self.logger = None
        if os.path.exists("runs"):
            shutil.rmtree("runs")
    
    def test_orchestrator_init(self):
        self.assertIsInstance(self.orchestrator, Orchestrator)
        self.assertIn(self.re_agent.name, self.orchestrator.agents)
        self.assertIn(self.user_agent.name, self.orchestrator.agents)
        self.assertIs(self.orchestrator.shared_memory, self.memory)
        self.assertIs(self.orchestrator.logger, self.logger)

    def test_orchestrator_start(self):
        try:
            self.orchestrator.start()
        except Exception as e:
            self.fail(f"Orchestrator.start() raised an exception: {e}")

    def test_orchestration(self):
        self.orchestrator.start()
        messages = self.memory.read()
        self.assertGreater(len(messages), 0, "No messages were written to shared memory during orchestration.")
        self.assertEqual(messages[0]["agent"], "RE", "First message should be from RE agent.")
        self.assertEqual(messages[1]["agent"], "User", "Second message should be from User agent.")
        

if __name__ == '__main__':
    unittest.main()