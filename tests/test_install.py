"""Exercise install.sh in a disposable kit and HOME, never the user's real folders."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAME = "generate-custom-resume"


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.data = self.base / "data"
        self.root = self.make_kit(self.base / "kit")

    def tearDown(self):
        self.tmp.cleanup()

    def make_kit(self, root: Path) -> Path:
        root.mkdir()
        shutil.copytree(ROOT / "skills", root / "skills", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(ROOT / "install.sh", root)
        return root

    def run_install(self, *args: str, root: Path | None = None) -> subprocess.CompletedProcess:
        env = {**os.environ, "HOME": str(self.home), "RESUME_KIT_HOME": str(self.data)}
        result = subprocess.run(["bash", str((root or self.root) / "install.sh"), *args],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def link(self, path: Path, target: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target, target_is_directory=True)
        return path

    def skill(self, root: Path | None = None) -> Path:
        return (root or self.root) / "skills" / NAME

    def test_links_claude_and_agents_and_keeps_existing_data(self):
        profile = self.data / "profile/profile.json"
        profile.parent.mkdir(parents=True)
        profile.write_text('{"name": "Existing fictional profile"}')
        for _ in range(2):
            self.run_install()
            for tool in (".claude", ".agents"):
                link = self.home / tool / "skills" / NAME
                self.assertEqual(link.resolve(), self.skill().resolve())
            self.assertEqual(profile.read_text(), '{"name": "Existing fictional profile"}')
            self.assertTrue((self.data / "profile/base-resume.md").exists())
            self.assertTrue((self.data / "applications").is_dir())
            self.assertFalse((self.data / "profile/achievements.json").exists())

    def test_target_limits_where_links_go(self):
        self.run_install("--target", "claude")
        self.assertTrue((self.home / ".claude/skills" / NAME).is_symlink())
        self.assertFalse((self.home / ".agents/skills" / NAME).exists())

    def test_leaves_foreign_installs_alone(self):
        other = self.base / "package-manager-copy"
        other.mkdir()
        foreign = self.link(self.home / ".agents/skills" / NAME, other)
        copied = self.home / ".claude/skills" / NAME
        copied.mkdir(parents=True)
        output = self.run_install().stdout
        self.assertEqual(foreign.resolve(), other.resolve())
        self.assertTrue(copied.is_dir() and not copied.is_symlink())
        self.assertIn("left it alone", output)

    def test_moved_kit_links_are_repointed(self):
        self.run_install()
        moved = self.base / "moved-kit"
        self.root.rename(moved)
        link = self.home / ".claude/skills" / NAME
        self.assertFalse(link.exists())  # absolute link now dangles
        output = self.run_install(root=moved).stdout
        self.assertEqual(link.resolve(), self.skill(moved).resolve())
        self.assertIn("repointed", output)

    def test_cleans_only_its_own_old_layout(self):
        old_command = self.home / ".claude/commands" / f"{NAME}.md"
        old_command.parent.mkdir(parents=True)
        old_command.write_text(f"Read and follow `{self.root}/skills/{NAME}/SKILL.md`.")
        user_command = self.home / ".claude/commands/other.md"
        user_command.write_text("unrelated")
        ours = self.link(self.home / ".cursor/skills/clarity", self.root / "skills/clarity")
        foreign_target = self.base / "someone-elses-clarity"
        foreign_target.mkdir()
        foreign = self.link(self.home / ".claude/skills/clarity", foreign_target)
        self.run_install()
        self.assertFalse(old_command.exists())
        self.assertTrue(user_command.exists())
        self.assertFalse(ours.is_symlink())
        self.assertEqual(foreign.resolve(), foreign_target.resolve())

    def test_uninstall_removes_only_links_and_keeps_data(self):
        self.run_install()
        foreign_target = self.base / "user-skill"
        foreign_target.mkdir()
        foreign = self.link(self.home / ".claude/skills/unrelated", foreign_target)
        self.run_install("--uninstall")
        for tool in (".claude", ".agents"):
            self.assertFalse((self.home / tool / "skills" / NAME).is_symlink())
        self.assertEqual(foreign.resolve(), foreign_target.resolve())
        self.assertTrue((self.data / "profile/profile.json").exists())


if __name__ == "__main__":
    unittest.main()
