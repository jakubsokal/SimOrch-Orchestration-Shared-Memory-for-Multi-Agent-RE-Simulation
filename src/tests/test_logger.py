import unittest, os, json, shutil, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from logs.logger import Logger


class TestLogger(unittest.TestCase):
    def setUp(self):
        if os.path.exists("runs"):
            shutil.rmtree("runs")
    
    def tearDown(self):
        if os.path.exists("runs"):
            shutil.rmtree("runs")
    
    def test_init_creates_runs_directory(self):
        logger = Logger()
        self.assertTrue(os.path.exists("runs"))
    
    def test_init_creates_run_001(self):
        logger = Logger()
        self.assertTrue(os.path.exists("runs/run_001"))
        self.assertEqual(logger.run_dir, os.path.join("runs", "run_001"))
    
    def test_multiple_loggers_increment_run_number(self):
        logger1 = Logger()
        logger2 = Logger()
        logger3 = Logger()
        
        self.assertTrue(os.path.exists("runs/run_001"))
        self.assertTrue(os.path.exists("runs/run_002"))
        self.assertTrue(os.path.exists("runs/run_003"))
    
    def test_save_creates_transcript_file(self):
        logger = Logger()
        test_memory = {"key": "value", "data": [1, 2, 3]}
        
        logger.store(test_memory)
        
        transcript_path = os.path.join(logger.run_dir, "transcript.json")
        self.assertTrue(os.path.exists(transcript_path))
    
    def test_save_writes_correct_json(self):
        logger = Logger()
        test_memory = {"key": "value", "nested": {"data": [1, 2, 3]}}
        
        logger.store(test_memory)
        
        transcript_path = os.path.join(logger.run_dir, "transcript.json")
        with open(transcript_path, "r") as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_memory)
    
    def test_save_formats_json_with_indent(self):
        logger = Logger()
        test_memory = {"key": "value"}
        
        logger.store(test_memory)
        
        transcript_path = os.path.join(logger.run_dir, "transcript.json")
        with open(transcript_path, "r") as f:
            content = f.read()
        
        self.assertIn("\n", content)
        self.assertIn("  ", content)


if __name__ == '__main__':
    unittest.main()
