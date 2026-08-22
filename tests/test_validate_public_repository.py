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
        source_run_id = "123456"
        source_created_at = "2026-08-22T12:34:56Z"
        manifest: dict[str, object] = {
            "schema_version": schema_version,
            "release_state": "published",
            "source": {
                "repository_role": "private_aq26_scientific_engine",
                "source_commit": "a" * 40,
                "source_run_id": source_run_id,
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
            manifest["source"] = {
                **manifest["source"],
                "source_workflow": "AQ26 Daily and Weekly Scientific Observatory",
                "source_run_attempt": "2",
                "source_run_created_at": source_created_at,
                "source_artifact": f"aq26-weekly-build-{source_run_id}",
            }
            manifest.update(
                {
                    "manifest_policy": "closed_world_release_tree",
                    "release_roots": ["data", "provenance", "reports", "site"],
                    "generated_utc": source_created_at,
                    "manifest_timestamp_basis": "source_run_created_at",
                    "publication": {
                        "mode": "one_way_sanitized_export",
                        "target_repository": "sccnexusdata/AQ26-England-Observatory",
                        "authorization": "manual_governed_workflow_dispatch",
                    },
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

    def _rewrite_manifest_hashes(self, target: Path) -> None:
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["file_count"] = 1
        manifest["total_bytes"] = target.stat().st_size
        manifest["files"][0]["bytes"] = target.stat().st_size
        manifest["files"][0]["sha256"] = _sha256(target)
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

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

    def test_valid_schema_v2_exporter_and_source_provenance_passes(self) -> None:
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

    def test_schema_v2_rejects_wrong_workflow_attempt_and_artifact(self) -> None:
        self._write_release(schema_version=2)
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["source"]["source_workflow"] = "Other workflow"
        manifest["source"]["source_run_attempt"] = "0"
        manifest["source"]["source_artifact"] = "aq26-daily-build-123456"
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("source_workflow must be" in error for error in errors))
        self.assertTrue(any("source_run_attempt must be" in error for error in errors))
        self.assertTrue(any("source_artifact must be" in error for error in errors))

    def test_schema_v2_rejects_noncanonical_timestamp_or_timestamp_basis(self) -> None:
        self._write_release(schema_version=2)
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["source"]["source_run_created_at"] = "2026-08-22T13:34:56+01:00"
        manifest["manifest_timestamp_basis"] = "publication_wall_clock"
        manifest["generated_utc"] = "2026-08-22T12:35:00Z"
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("must be normalised UTC ending in Z" in error for error in errors))
        self.assertTrue(any("manifest_timestamp_basis must be" in error for error in errors))
        self.assertTrue(any("generated_utc must exactly equal" in error for error in errors))

    def test_schema_v2_rejects_wrong_publication_target_or_authorization(self) -> None:
        self._write_release(schema_version=2)
        manifest = json.loads(validator.MANIFEST.read_text(encoding="utf-8"))
        manifest["publication"]["target_repository"] = "other/repository"
        manifest["publication"]["authorization"] = "automatic_gate"
        validator.MANIFEST.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("target_repository must be" in error for error in errors))
        self.assertTrue(any("publication authorization must be" in error for error in errors))

    def test_schema_v2_rejects_execution_path_in_release_text(self) -> None:
        target = self._write_release(schema_version=2)
        target.write_text(
            json.dumps({"artifact_path": "/home/runner/work/repo/repo/outputs/result.json"}) + "\n",
            encoding="utf-8",
        )
        self._rewrite_manifest_hashes(target)
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("execution path marker detected" in error for error in errors))

    def test_schema_v2_rejects_blocked_credential_metadata_key(self) -> None:
        target = self._write_release(schema_version=2)
        target.write_text(
            json.dumps({"status": "ok", "credential_name": "private-secret-alias"}) + "\n",
            encoding="utf-8",
        )
        self._rewrite_manifest_hashes(target)
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertTrue(any("blocked credential metadata key" in error for error in errors))

    def test_schema_v2_preserves_scientific_decisions_key(self) -> None:
        target = self._write_release(schema_version=2)
        target.write_text(
            json.dumps({"decisions": [{"status": "retain-scientific-decision"}]}) + "\n",
            encoding="utf-8",
        )
        self._rewrite_manifest_hashes(target)
        errors: list[str] = []
        validator.validate_manifest(errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
