import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.base_agent import BaseAgent

class ConcreteAgent(BaseAgent):
    def speak(self, message):
        return f"{self.name} says: {message}"

class TestBaseAgent(unittest.TestCase):
    def test_init_sets_name(self):
        agent = BaseAgent("TestAgent")
        self.assertEqual(agent.name, "TestAgent")
    
    def test_speak_base_error(self):
        agent = BaseAgent("TestAgent")
        with self.assertRaises(NotImplementedError):
            agent.speak("Hello")
    
    def test_subclass_can_implement_speak(self):
        agent = ConcreteAgent("Bob")
        result = agent.speak("Hello")
        self.assertEqual(result, "Bob says: Hello")
    
    def test_subclass_inherits_name(self):
        agent = ConcreteAgent("Alice")
        self.assertEqual(agent.name, "Alice")


if __name__ == '__main__':
    unittest.main()
