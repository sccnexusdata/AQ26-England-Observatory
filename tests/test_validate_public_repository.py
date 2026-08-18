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

    def _write_release(self, *, schema_version: int = 1) -> Path:
        target = self.root / "data" / "latest" / "public_release_summary.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('{"status":"ok"}\n', encoding="utf-8")
        manifest: dict[str, object] = {
            "schema_version": schema_version,
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
        if schema_version == 2:
            manifest.update(
                {
                    "manifest_policy": "closed_world_release_tree",
                    "release_roots": ["data", "provenance", "reports", "site"],
                    "publication": {"mode": "one_way_sanitized_export"},
                    "exporter": {
                        "config_path": "configs/public_repo_export.yml",
                        "config_sha256": "b" * 64,
                        "script_path": "scripts/aq26_prepare_public_repo_export.py",
                        "script_sha256": "c" * 64,
                    },
                }
            )
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        return target

    def test_valid_schema_v1_closed_world_release_passes(self) -> None:
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
        self.assertIn("unmanifested release file: data/latest/rogue.json", errors)

    def test_manifested_but_absent_file_fails(self) -> None:
        target = self._write_release()
        target.unlink()
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("manifested file missing or not regular" in error for error in errors))
        self.assertTrue(any("manifest lists absent release file" in error for error in errors))

    def test_manifest_count_and_total_are_reconciled(self) -> None:
        self._write_release()
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["file_count"] = 2
        manifest["total_bytes"] += 1
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("manifest file_count mismatch" in error for error in errors))
        self.assertTrue(any("manifest total_bytes mismatch" in error for error in errors))

    def test_valid_schema_v2_exporter_provenance_passes(self) -> None:
        self._write_release(schema_version=2)
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertEqual(errors, [])

    def test_schema_v2_rejects_noncanonical_exporter_provenance(self) -> None:
        self._write_release(schema_version=2)
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["exporter"]["config_path"] = "other/config.yml"
        manifest["exporter"]["script_sha256"] = "not-a-sha"
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("config_path is not canonical" in error for error in errors))
        self.assertTrue(any("script_sha256 must be a lowercase SHA-256" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
