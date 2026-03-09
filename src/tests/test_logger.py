import unittest, os, json, shutil, sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from logs.logger import Logger


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.runs_dir = self.project_root / 'runs'

        self.original_runs = []
        if self.runs_dir.exists():
            self.original_runs = os.listdir(self.runs_dir)
    
    def tearDown(self):
        if self.runs_dir.exists():
            current_runs = os.listdir(self.runs_dir)
            for run in current_runs:
                if run not in self.original_runs:
                    run_path = self.runs_dir / run
                    if run_path.is_dir():
                        shutil.rmtree(run_path)
    
    def test_init_creates_runs_directory(self):
        logger = Logger()
        self.assertTrue(self.runs_dir.exists())
    
    def test_init_creates_run_001(self):
        logger = Logger()
        expected_run_number = len(self.original_runs) + 1
        expected_run_dir = self.runs_dir / f"run_{expected_run_number:03d}"
        self.assertTrue(expected_run_dir.exists())

        self.assertEqual(str(logger.run_dir), str(expected_run_dir))
    
    def test_multiple_loggers_increment_run_number(self):
        start_num = len(self.original_runs) + 1
        logger1 = Logger()
        logger2 = Logger()
        logger3 = Logger()
        
        self.assertTrue((self.runs_dir / f"run_{start_num:03d}").exists())
        self.assertTrue((self.runs_dir / f"run_{start_num+1:03d}").exists())
        self.assertTrue((self.runs_dir / f"run_{start_num+2:03d}").exists())
    
    def test_save_creates_transcript_file(self):
        logger = Logger()
        test_memory = {"key": "value", "data": [1, 2, 3]}
        
        logger.store(test_memory)
        
        transcript_path = os.path.join(logger.run_dir, "messages_log.json")
        self.assertTrue(os.path.exists(transcript_path))
    
    def test_save_writes_correct_json(self):
        logger = Logger()
        test_memory = {"key": "value", "nested": {"data": [1, 2, 3]}}
        
        logger.store(test_memory)
        
        transcript_path = os.path.join(logger.run_dir, "messages_log.json")
        with open(transcript_path, "r") as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, test_memory)
    
    def test_save_formats_json_with_indent(self):
        logger = Logger()
        test_memory = {"key": "value"}
        
        logger.store(test_memory)
        
        transcript_path = os.path.join(logger.run_dir, "messages_log.json")
        with open(transcript_path, "r") as f:
            content = f.read()
        
        self.assertIn("\n", content)
        self.assertIn("  ", content)


if __name__ == '__main__':
    unittest.main()
