import unittest

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


if __name__ == "__main__":
    unittest.main()
