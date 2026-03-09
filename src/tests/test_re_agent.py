import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.re_agent import REAgent
from agents.base_agent import BaseAgent
from unittest.mock import Mock
        

class TestREAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.name = "MockLLM"
        self.mock_llm.invoke.return_value = "Hello, world!"

    def test_init_sets_name(self):
        agent = REAgent("TestRE", llm=self.mock_llm)
        self.assertEqual(agent.name, "TestRE")
    
    def test_inherits_from_base_agent(self):
        agent = REAgent("TestRE", llm=self.mock_llm)
        self.assertIsInstance(agent, BaseAgent)
    
    def test_speak_returns_message(self):
        agent = REAgent("TestRE", llm=self.mock_llm)
        message = "Hello, world!"
        result = agent.speak(message, role=1)
        self.assertEqual(result, message)
    
    def test_speak_with_empty_string(self):
        self.mock_llm.invoke.return_value = ""
        agent = REAgent("TestRE", llm=self.mock_llm)
        result = agent.speak("", role=1)
        self.assertEqual(result, "")
    
    def test_speak_with_complex_message(self):
        self.mock_llm.invoke.return_value = "This is a complex message with numbers 123 and symbols !@#"
        agent = REAgent("TestRE", llm=self.mock_llm)
        message = "This is a complex message with numbers 123 and symbols !@#"
        result = agent.speak(message, role=1)

        self.assertEqual(result, message)
    
    def test_multiple_agents_independent(self):
        self.mock_llm2 = Mock()
        self.mock_llm2.name = "MockLLM1234"
        self.mock_llm2.invoke.return_value = "TESTER"
        agent1 = REAgent("Agent1", llm=self.mock_llm)
        agent2 = REAgent("Agent2", llm=self.mock_llm2)
        
        self.assertEqual(agent1.name, "Agent1")
        self.assertEqual(agent2.name, "Agent2")
        self.assertNotEqual(agent1.name, agent2.name)


if __name__ == '__main__':
    unittest.main()
