import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.re_agent import REAgent
from agents.base_agent import BaseAgent

class TestREAgent(unittest.TestCase):
    def test_init_sets_name(self):
        agent = REAgent("TestRE")
        self.assertEqual(agent.name, "TestRE")
    
    def test_inherits_from_base_agent(self):
        agent = REAgent("TestRE")

        self.assertIsInstance(agent, BaseAgent)
    
    def test_speak_returns_message(self):
        agent = REAgent("TestRE")
        message = "Hello, world!"
        result = agent.speak(message)
        self.assertEqual(result, message)
    
    def test_speak_with_empty_string(self):
        agent = REAgent("TestRE")
        result = agent.speak("")
        self.assertEqual(result, "")
    
    def test_speak_with_complex_message(self):
        agent = REAgent("TestRE")
        message = "This is a complex message with numbers 123 and symbols !@#"
        result = agent.speak(message)
        self.assertEqual(result, message)
    
    def test_multiple_agents_independent(self):
        agent1 = REAgent("Agent1")
        agent2 = REAgent("Agent2")
        
        self.assertEqual(agent1.name, "Agent1")
        self.assertEqual(agent2.name, "Agent2")
        self.assertNotEqual(agent1.name, agent2.name)


if __name__ == '__main__':
    unittest.main()
