import unittest

from src.env_runner.env import build_env


class EnvAllowlistTest(unittest.TestCase):
    def test_only_allowed_request_variables_are_passed(self):
        result = build_env(
            {"SAFE_FLAG": "1", "API_TOKEN": "secret", "PATH": "/evil"},
            allowlist=["SAFE_FLAG"],
        )
        env = result["env"]
        self.assertEqual(env["SAFE_FLAG"], "1")
        self.assertNotIn("API_TOKEN", env)
        self.assertNotEqual(env["PATH"], "/evil")
        self.assertEqual(result["keys"], sorted(env))

    def test_preserves_protected_defaults(self):
        result = build_env({"HOME": "/tmp/other"}, allowlist=["HOME"])
        self.assertNotEqual(result["env"]["HOME"], "/tmp/other")
        self.assertIn("PATH", result["env"])


if __name__ == "__main__":
    unittest.main()
