"""A changed/deleted/added protected file must fail the preservation gate."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/check-preservation.py"


class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for directory in ("src", "public", "tests/site"):
            (self.root / directory).mkdir(parents=True)
        self.files = {"src/index.astro": "approved copy", "public/logo.svg": "approved asset",
                      "astro.config.mjs": "static config", "package.json": "{}", "package-lock.json": "{}"}
        for name, text in self.files.items():
            (self.root / name).write_text(text)
        baseline = {"sourceSha": "a" * 40, "protectedFileSha256": {
            name: hashlib.sha256(text.encode()).hexdigest() for name, text in self.files.items()}}
        (self.root / "tests/site/repository-baseline.json").write_text(json.dumps(baseline))

    def run_check(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_unchanged_passes(self):
        code, report = self.run_check()
        self.assertEqual(code, 0)
        self.assertEqual(report["protectedFiles"], 5)

    def test_changed_copy_fails(self):
        (self.root / "src/index.astro").write_text("unreviewed claim")
        code, report = self.run_check()
        self.assertEqual(code, 1)
        self.assertEqual(report["changed"], ["src/index.astro"])

    def test_missing_asset_fails(self):
        (self.root / "public/logo.svg").unlink()
        code, report = self.run_check()
        self.assertEqual(code, 1)
        self.assertEqual(report["missing"], ["public/logo.svg"])

    def test_added_file_fails(self):
        (self.root / "public/new.html").write_text("new unreviewed content")
        code, report = self.run_check()
        self.assertEqual(code, 1)
        self.assertEqual(report["added"], ["public/new.html"])

    def test_infrastructure_file_does_not_change_site(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/operations.md").write_text("operating instructions")
        self.assertEqual(self.run_check()[0], 0)
