import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-codex-defaults.sh"


class InstallerTests(unittest.TestCase):
    def test_installer_is_idempotent_and_preserves_user_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            codex_home = Path(temp) / "codex-home"
            bin_dir = Path(temp) / "bin"
            bin_dir.mkdir()
            (bin_dir / "python3").symlink_to(sys.executable)
            codex_home.mkdir()
            (codex_home / "config.toml").write_text(
                'model = "gpt-5.5"\n\n'
                '[marketplaces.evopilot]\n'
                'source_type = "local"\n'
                'source = "/tmp/old-evopilot"\n\n'
                '[plugins."evopilot@evopilot"]\n'
                'enabled = false\n',
                encoding="utf-8",
            )
            (codex_home / "AGENTS.md").write_text(
                "# Existing defaults\n\n"
                "- Keep this user preference.\n\n"
                "<!-- EVOPILOT DEFAULTS START -->\n"
                "old managed block\n"
                "<!-- EVOPILOT DEFAULTS END -->\n",
                encoding="utf-8",
            )
            env = {
                **os.environ,
                "CODEX_HOME": str(codex_home),
                "EVOPILOT_SKIP_CODEX_CLI": "1",
                "PATH": f"{bin_dir}:/usr/bin:/bin:/usr/sbin:/sbin",
            }

            for _ in range(2):
                subprocess.run(
                    [str(INSTALLER)],
                    cwd=ROOT,
                    env=env,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

            config = (codex_home / "config.toml").read_text(encoding="utf-8")
            agents = (codex_home / "AGENTS.md").read_text(encoding="utf-8")

            self.assertIn('model = "gpt-5.5"', config)
            self.assertIn('source_type = "git"', config)
            self.assertIn('source = "https://github.com/sdfdu/evopilot.git"', config)
            self.assertIn('enabled = true', config)
            self.assertEqual(config.count("[marketplaces.evopilot]"), 1)
            self.assertEqual(config.count('[plugins."evopilot@evopilot"]'), 1)

            self.assertIn("- Keep this user preference.", agents)
            self.assertIn("Prefer EvoPilot as the default workflow layer", agents)
            self.assertNotIn("old managed block", agents)
            self.assertEqual(agents.count("<!-- EVOPILOT DEFAULTS START -->"), 1)
            self.assertEqual(agents.count("<!-- EVOPILOT DEFAULTS END -->"), 1)


if __name__ == "__main__":
    unittest.main()
