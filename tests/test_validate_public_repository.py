from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_public_repository as validator


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PublicRepositoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_root = validator.ROOT
        self._original_manifest = validator.MANIFEST
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        validator.ROOT = self.root
        validator.MANIFEST = self.root / "PUBLIC_RELEASE_MANIFEST.json"

    def tearDown(self) -> None:
        validator.ROOT = self._original_root
        validator.MANIFEST = self._original_manifest
        self.tempdir.cleanup()

    def _write_release(self) -> Path:
        target = self.root / "data" / "latest" / "public_release_summary.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('{"status":"ok"}\n', encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "release_state": "published",
            "source": {
                "repository_role": "private_aq26_scientific_engine",
                "source_commit": "a" * 40,
                "source_run_id": "123456",
            },
            "file_count": 1,
            "total_bytes": target.stat().st_size,
            "files": [
                {
                    "path": "data/latest/public_release_summary.json",
                    "bytes": target.stat().st_size,
                    "sha256": _sha256(target),
                }
            ],
        }
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        return target

    def test_valid_closed_world_release_passes(self) -> None:
        self._write_release()
        errors: list[str] = []
        validator.validate_tree(errors)
        validator.validate_manifest(errors)
        self.assertEqual(errors, [])

    def test_unmanifested_release_file_fails(self) -> None:
        self._write_release()
        rogue = self.root / "data" / "latest" / "rogue.json"
        rogue.write_text("{}\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertIn("unmanifested release-tree file: data/latest/rogue.json", errors)

    def test_transitional_repository_metadata_is_explicitly_allowed(self) -> None:
        self._write_release()
        metadata = self.root / "provenance" / "README.md"
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text("# Public provenance\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertEqual(errors, [])

    def test_manifest_count_is_reconciled(self) -> None:
        self._write_release()
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["file_count"] = 2
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("manifest file_count mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
