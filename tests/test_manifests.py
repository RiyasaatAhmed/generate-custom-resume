"""Keep the Claude Code, Cursor, and Agent Skills metadata consistent with each other."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/generate-custom-resume/SKILL.md"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def frontmatter() -> str:
    match = re.match(r"---\n(.*?)\n---\n", SKILL.read_text(encoding="utf-8"), re.S)
    assert match, "SKILL.md needs YAML frontmatter"
    return match.group(1)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.claude = load(".claude-plugin/plugin.json")
        self.claude_market = load(".claude-plugin/marketplace.json")
        self.cursor = load(".cursor-plugin/plugin.json")
        self.cursor_market = load(".cursor-plugin/marketplace.json")

    def test_versions_match_everywhere(self):
        skill_version = re.search(r'^\s+version:\s*"?([^"\n]+)"?$', frontmatter(), re.M).group(1)
        versions = {
            ".claude-plugin/plugin.json": self.claude["version"],
            ".claude-plugin/marketplace.json": self.claude_market["plugins"][0]["version"],
            ".cursor-plugin/plugin.json": self.cursor["version"],
            "SKILL.md metadata.version": skill_version,
        }
        self.assertEqual(len(set(versions.values())), 1, versions)

    def test_names_and_sources_point_at_this_plugin(self):
        name = re.search(r"^name:\s*(\S+)$", frontmatter(), re.M).group(1)
        self.assertEqual(name, SKILL.parent.name)  # Agent Skills: name matches its folder
        for manifest in (self.claude, self.cursor):
            self.assertEqual(manifest["name"], name)
        for market, folder in ((self.claude_market, ".claude-plugin"), (self.cursor_market, ".cursor-plugin")):
            entry = market["plugins"][0]
            self.assertEqual(entry["name"], name)
            self.assertTrue((ROOT / entry["source"] / folder / "plugin.json").is_file(), entry["source"])

    def test_cursor_manifest_uses_only_fields_its_schema_allows(self):
        # From cursor/plugins schemas/plugin.schema.json; the author object rejects extra keys.
        self.assertLessEqual(set(self.cursor["author"]), {"name", "email"})
        self.assertTrue((ROOT / self.cursor["skills"]).is_dir())
        for entry in self.cursor_market["plugins"]:
            self.assertLessEqual(set(entry), {"name", "source", "description", "minClientVersions"})

    def test_skill_frontmatter_meets_agent_skills_limits(self):
        meta = frontmatter()
        name = re.search(r"^name:\s*(\S+)$", meta, re.M).group(1)
        description = re.search(r"^description:\s*(.+)$", meta, re.M).group(1)
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(description), 1024)


if __name__ == "__main__":
    unittest.main()
