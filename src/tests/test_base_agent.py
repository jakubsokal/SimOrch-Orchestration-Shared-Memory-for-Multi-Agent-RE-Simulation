import unittest, sys, os
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.base_agent import BaseAgent

class ConcreteAgent(BaseAgent):
    def speak(self, message, role):
        return f"{self.name} who is {role} says: {message}"

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.invoke.return_value = "TESTER"
    
    def test_init_sets_name(self):
        agent = BaseAgent("TestAgent", llm=self.mock_llm)
        self.assertEqual(agent.name, "TestAgent")
    
    def test_speak_base_error(self):
        agent = BaseAgent("TestAgent", llm=self.mock_llm)
        with self.assertRaises(NotImplementedError):
            agent.speak("Hello", "user")
    
    def test_subclass_can_implement_speak(self):
        agent = ConcreteAgent("Bob", llm=self.mock_llm)
        result = agent.speak("Hello", "user")
        self.assertEqual(result, "Bob who is user says: Hello")
    
    def test_subclass_inherits_name(self):
        agent = ConcreteAgent("Alice", llm=self.mock_llm)
        self.assertEqual(agent.name, "Alice")


if __name__ == '__main__':
    unittest.main()
