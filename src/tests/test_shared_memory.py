import unittest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from memory.shared_memory import SharedMemory


class TestMemory(unittest.TestCase):
    def test_write_and_read(self):
        memory = SharedMemory()
        memory.write("user", "Hello, how are you?")

        messages = memory.read()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["message"], "Hello, how are you?")

    def test_multiple_writes(self):
        memory = SharedMemory()
        memory.write("RE", "Hello! What are your requirements?")
        memory.write("user", "Hi there! I need my app to do XYZ.")
        memory.write("RE", "So you want XYZ functionality?")

        messages = memory.read()
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["message"], "Hi there! I need my app to do XYZ.")
        self.assertEqual(messages[2]["role"], "RE")
        self.assertEqual(messages[2]["message"], "So you want XYZ functionality?")
    
if __name__ == '__main__':
    unittest.main()
