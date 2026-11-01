"""Exercise installer ownership behavior in a disposable kit, never the user's HOME."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.root = self.make_kit(self.base / "kit")

    def tearDown(self):
        self.tmp.cleanup()

    def make_kit(self, root: Path) -> Path:
        root.mkdir()
        for name in ("scripts", "commands", "skills"):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(ROOT / "setup.sh", root)
        (root / "profile").mkdir()
        for path in (ROOT / "profile").glob("*.example.*"):
            shutil.copy(path, root / "profile")
        return root

    def setup(self, *args: str, root: Path | None = None) -> subprocess.CompletedProcess:
        env = {**os.environ, "HOME": str(self.home)}
        result = subprocess.run(["bash", str((root or self.root) / "setup.sh"), "--skip-smoke", *args],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def link(self, path: Path, target: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target, target_is_directory=True)
        return path

    def test_preserves_external_skill_links_and_existing_profile(self):
        profile = self.root / "profile/profile.json"
        profile.write_text('{"name": "Existing fictional profile"}')
        external = self.base / "other-skill"
        external.mkdir()
        link = self.link(self.root / ".claude/skills/cover-letter", external)
        for _ in range(2):
            self.setup()
            self.assertEqual(link.resolve(), external.resolve())
            self.assertEqual(profile.read_text(), '{"name": "Existing fictional profile"}')
            self.assertTrue((self.root / ".cursor/skills/generate-custom-resume").is_symlink())
            self.assertFalse((self.root / "profile/achievements.json").exists())
            command = (self.root / ".claude/commands/generate-custom-resume.md").read_text()
            self.assertNotIn("{{KIT}}", command)
            self.assertIn(str(self.root), command)

    def test_retired_links_removed_only_when_owned(self):
        ours = self.link(self.root / ".claude/skills/humanizer-zh", self.root / "skills/humanizer-zh")
        foreign_target = self.base / "someone-elses-humanizer"
        foreign_target.mkdir()
        foreign = self.link(self.root / ".cursor/skills/humanizer-zh", foreign_target)
        self.setup()
        self.assertFalse(ours.is_symlink())
        self.assertEqual(foreign.resolve(), foreign_target.resolve())

    def test_moved_kit_links_are_repointed(self):
        self.setup()
        moved = self.base / "moved-kit"
        self.root.rename(moved)
        link = moved / ".claude/skills/generate-custom-resume"
        self.assertFalse(link.exists())  # absolute link now dangles
        (moved / ".claude/skills/clarity").unlink()
        unrelated = self.link(moved / ".claude/skills/clarity", self.base / "deleted/elsewhere")
        output = self.setup(root=moved).stdout
        self.assertEqual(link.resolve(), (moved / "skills/generate-custom-resume").resolve())
        self.assertIn("repointed", output)
        self.assertEqual(os.readlink(unrelated), str(self.base / "deleted/elsewhere"))

    def test_global_install_and_uninstall_touch_only_kit_files(self):
        foreign_target = self.base / "user-clarity"
        foreign_target.mkdir()
        foreign = self.link(self.home / ".claude/skills/clarity", foreign_target)
        self.setup("--global")
        command = self.home / ".claude/commands/generate-custom-resume.md"
        self.assertIn(str(self.root), command.read_text())
        self.assertTrue((self.home / ".cursor/skills/generate-custom-resume").is_symlink())
        self.assertEqual(foreign.resolve(), foreign_target.resolve())
        result = subprocess.run(["bash", str(self.root / "setup.sh"), "--uninstall-global"],
                                capture_output=True, text=True, env={**os.environ, "HOME": str(self.home)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(command.exists())
        self.assertFalse((self.home / ".cursor/skills/generate-custom-resume").is_symlink())
        self.assertEqual(foreign.resolve(), foreign_target.resolve())
        self.assertTrue((self.root / ".claude/skills/generate-custom-resume").is_symlink())


if __name__ == "__main__":
    unittest.main()
