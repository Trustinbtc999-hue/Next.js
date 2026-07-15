"""Unit tests for cline_mcp_config.json.

These tests validate the structure and content of the Cline MCP server
configuration file, focusing on the "github" MCP server entry that was
added to enable the GitHub MCP server (ghcr.io/github/github-mcp-server).
"""

import json
import os
import unittest

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cline_mcp_config.json",
)


class TestClineMcpConfigFile(unittest.TestCase):
    """Sanity checks on the overall config file."""

    @classmethod
    def setUpClass(cls):
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            cls.raw_contents = fh.read()
        cls.config = json.loads(cls.raw_contents)

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(CONFIG_PATH))

    def test_file_is_valid_json(self):
        # json.loads in setUpClass would have raised if invalid; re-parse
        # here explicitly so a JSON error surfaces as a clear test failure.
        try:
            json.loads(self.raw_contents)
        except json.JSONDecodeError as exc:
            self.fail(f"cline_mcp_config.json is not valid JSON: {exc}")

    def test_top_level_is_object_with_mcp_servers(self):
        self.assertIsInstance(self.config, dict)
        self.assertIn("mcpServers", self.config)
        self.assertIsInstance(self.config["mcpServers"], dict)

    def test_existing_tronscan_server_untouched(self):
        # Regression check: adding the "github" server should not have
        # removed or corrupted the pre-existing "tronscan" server entry.
        servers = self.config["mcpServers"]
        self.assertIn("tronscan", servers)
        self.assertEqual(servers["tronscan"]["command"], "npx")

    def test_mcp_servers_has_at_least_two_entries(self):
        self.assertGreaterEqual(len(self.config["mcpServers"]), 2)


class TestGithubMcpServerEntry(unittest.TestCase):
    """Tests specific to the newly added "github" MCP server entry."""

    @classmethod
    def setUpClass(cls):
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            cls.config = json.load(fh)
        cls.servers = cls.config["mcpServers"]

    def test_github_server_present(self):
        self.assertIn("github", self.servers)

    def test_github_server_is_object(self):
        self.assertIsInstance(self.servers["github"], dict)

    def test_github_command_is_docker(self):
        github = self.servers["github"]
        self.assertEqual(github.get("command"), "docker")

    def test_github_args_is_list(self):
        github = self.servers["github"]
        self.assertIn("args", github)
        self.assertIsInstance(github["args"], list)

    def test_github_args_exact_sequence(self):
        github = self.servers["github"]
        expected_args = [
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server:v1.6.0",
        ]
        self.assertEqual(github["args"], expected_args)

    def test_github_args_run_detached_flags_present(self):
        # -i (interactive) and --rm (auto-remove container) are required
        # for the docker-based MCP server to behave correctly.
        args = self.servers["github"]["args"]
        self.assertIn("-i", args)
        self.assertIn("--rm", args)

    def test_github_image_uses_pinned_version_tag(self):
        args = self.servers["github"]["args"]
        image_entries = [a for a in args if a.startswith("ghcr.io/github/github-mcp-server")]
        self.assertEqual(len(image_entries), 1)
        image = image_entries[0]
        self.assertIn(":", image, "Image reference should be pinned to a specific tag")
        tag = image.split(":", 1)[1]
        self.assertNotEqual(tag, "latest", "Image should be pinned to a fixed version, not 'latest'")
        self.assertEqual(image, "ghcr.io/github/github-mcp-server:v1.6.0")

    def test_github_env_declared_in_args(self):
        # The "-e" docker flag must be immediately followed by the name of
        # the environment variable it forwards into the container.
        args = self.servers["github"]["args"]
        idx = args.index("-e")
        self.assertEqual(args[idx + 1], "GITHUB_PERSONAL_ACCESS_TOKEN")

    def test_github_env_object_present(self):
        github = self.servers["github"]
        self.assertIn("env", github)
        self.assertIsInstance(github["env"], dict)

    def test_github_env_contains_pat_key(self):
        env = self.servers["github"]["env"]
        self.assertIn("GITHUB_PERSONAL_ACCESS_TOKEN", env)

    def test_github_env_value_is_variable_reference_not_hardcoded(self):
        # Ensure the token is sourced from the environment rather than
        # being a hardcoded secret committed to the repo.
        env = self.servers["github"]["env"]
        value = env["GITHUB_PERSONAL_ACCESS_TOKEN"]
        self.assertEqual(value, "${env:GITHUB_PERSONAL_ACCESS_TOKEN}")

    def test_github_env_var_name_matches_docker_e_flag(self):
        # The variable name passed via "-e" in args must match the key
        # defined in the "env" object so docker actually forwards it.
        github = self.servers["github"]
        args = github["args"]
        idx = args.index("-e")
        env_var_in_args = args[idx + 1]
        self.assertIn(env_var_in_args, github["env"])

    def test_github_no_plaintext_secret_values(self):
        # Defensive check: no value under the github server config should
        # look like an actual token/secret (only the variable placeholder
        # is allowed).
        github = self.servers["github"]
        env_value = github["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"]
        self.assertTrue(env_value.startswith("${env:"))
        self.assertTrue(env_value.endswith("}"))


if __name__ == "__main__":
    unittest.main()