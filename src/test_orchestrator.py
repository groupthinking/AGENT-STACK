import unittest
from unittest.mock import patch
import io

from agents import Orchestrator


class TestOrchestrator(unittest.TestCase):
    def test_run_returns_summary(self):
        data = "This is a test input string that should be summarized and optimized."
        orchestrator = Orchestrator()
        result = orchestrator.run(data)
        self.assertIsInstance(result, str)
        # Result should be trimmed to 50 chars and stripped
        expected = data.strip()[:50]
        self.assertEqual(result, expected)

    def test_logger_outputs_messages(self):
        data = "Capture the logs"
        orchestrator = Orchestrator()
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            orchestrator.run(data)
            lines = mock_stdout.getvalue().strip().splitlines()
        self.assertGreaterEqual(len(lines), 3)
        self.assertEqual(lines[0], "[LOG] Parsing data")
        self.assertEqual(lines[1], "[LOG] Summarizing data")
        self.assertEqual(lines[2], "[LOG] Optimizing summary")


if __name__ == "__main__":
    unittest.main()
