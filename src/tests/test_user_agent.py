import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.user_agent import UserAgent
from agents.base_agent import BaseAgent
from agents.agent_factory import AgentFactory
from unittest.mock import Mock
        

class TestUserAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = Mock()
        self.mock_llm.name = "MockLLM"
        self.mock_llm.invoke.return_value = "Hello, world!"

    def test_init_sets_name(self):
        agent = UserAgent("TestUser", llm=self.mock_llm)
        self.assertEqual(agent.name, "TestUser")
    
    def test_inherits_from_base_agent(self):
        agent = UserAgent("TestUser", llm=self.mock_llm)
        self.assertIsInstance(agent, BaseAgent)
    
    def test_speak_returns_message(self):
        agent = UserAgent("TestUser", llm=self.mock_llm)
        message = "Hello, world!"
        result = agent.speak(message, role=2)
        self.assertEqual(result, message)
    
    def test_speak_with_empty_string(self):
        self.mock_llm.invoke.return_value = ""
        agent = UserAgent("TestUser", llm=self.mock_llm)
        result = agent.speak("", role=2)
        self.assertEqual(result, "")
    
    def test_speak_with_complex_message(self):
        self.mock_llm.invoke.return_value = "This is a complex message with numbers 123 and symbols !@#"
        agent = UserAgent("TestUser", llm=self.mock_llm)
        message = "This is a complex message with numbers 123 and symbols !@#"
        result = agent.speak(message, role=2)
        self.assertEqual(result, message)
    
    def test_multiple_agents_independent(self):
        self.mock_llm2 = Mock()
        self.mock_llm2.name = "MockLLM1234"
        self.mock_llm2.invoke.return_value = "TESTER"
        agent1 = UserAgent("Agent1", llm=self.mock_llm)
        agent2 = UserAgent("Agent2", llm=self.mock_llm2)
        
        self.assertEqual(agent1.name, "Agent1")
        self.assertEqual(agent2.name, "Agent2")
        self.assertNotEqual(agent1.name, agent2.name)

    def test_context_prompt_in_speak(self):
        json = {
                'provider': 'OLLAMA',
                'model': 'llama2',
                'role': 2, 
                'name': 'Employee',
                'context_prompt':  "You are an office employee. You need a system to book meeting rooms easily. You are frustrated with the current, manual email-based process."
            }
        agent = AgentFactory.create_agent(json,
                                           description='A dialogue between a Requirements Engineer and a User(employee) and a User(office manager) to elicit requirements for a corporate room booking system.', seed=42)
        message = "I need faster emails and to be able to handle more traffic."
        res1 = agent.speak(message, role='LISTEN')
        print(f"\n\n\nres1: {res1}\n\n\n")
        result = agent.speak(message, role=2)

        print(f"\n\n\nres1: {res1}\n\n\nresult: {result}\n\n\n")
        self.assertNotEqual(result, res1)


if __name__ == '__main__':
    unittest.main()
