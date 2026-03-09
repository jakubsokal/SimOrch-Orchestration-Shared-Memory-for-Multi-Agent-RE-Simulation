import unittest, sys, os, shutil
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from orchestrator.orchestrator import Orchestrator
from memory import SharedMemory

class TestExample(unittest.TestCase):
    def setUp(self):
        self.re_agent = Mock()
        self.re_agent.name = "RE"
        self.re_agent.role = 1
        self.re_agent.speak.return_value = "What features do you need?"
        
        self.user_agent = Mock()
        self.user_agent.name = "User"
        self.user_agent.role = 2
        self.user_agent.speak.return_value = "I need fitness tracking features"
        
        self.memory = SharedMemory()
        
  
        self.logger = Mock()
        self.logger.store = Mock()
        
        self.orchestrator = Orchestrator(
            max_turns=2,
            re_agents={"RE": self.re_agent},
            user_agents={"User": self.user_agent},
            helper_agent= None,
            shared_memory=self.memory,
            logger=self.logger
        )
    
    def tearDown(self):
        self.memory = None
        self.orchestrator = None
        self.re_agent = None
        self.user_agent = None
        self.logger = None
    
    def test_orchestrator_init(self):
        self.assertIsInstance(self.orchestrator, Orchestrator)
        self.assertIn(self.re_agent.name, self.orchestrator.re_agents)
        self.assertIn(self.user_agent.name, self.orchestrator.user_agents)
        self.assertIs(self.orchestrator.shared_memory, self.memory)
        self.assertIs(self.orchestrator.logger, self.logger)

    def test_orchestrator_start(self):
        try:
            self.orchestrator.start()
        except Exception as e:
            self.fail(f"Orchestrator.start() raised an exception: {e}")

    def test_orchestration(self):
        self.orchestrator.start()
        messages = self.memory.get_all_messages()

        print(f"Messages in shared memory after orchestration: {messages}")        
        self.assertGreater(len(messages), 0, "No messages were written to shared memory during orchestration.")
        self.assertEqual(messages[0]["agent"], "RE", "First message should be from RE agent.")
        self.assertEqual(messages[1]["agent"], "User", "Second message should be from User agent.")
        

if __name__ == '__main__':
    unittest.main()