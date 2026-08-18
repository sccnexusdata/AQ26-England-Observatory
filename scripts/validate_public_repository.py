from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PUBLIC_RELEASE_MANIFEST.json"
MAX_FILE_BYTES = 20 * 1024 * 1024
ALLOWED_RELEASE_ROOTS = {"site", "data", "reports", "provenance"}
FORBIDDEN_FILE_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
FORBIDDEN_PATH_PARTS = {
    "site_unredacted",
    "site_test",
    "protected",
    "internal-audit",
    "internal_audit",
    "raw-secrets",
    "raw_secrets",
}
SECRET_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    "github_pat": re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    "github_classic_pat": re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
}
TEXT_SCAN_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".html",
    ".css",
    ".js",
    ".py",
    ".csv",
    ".xml",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_RE = re.compile(r"^[0-9]+$")
ALLOWED_STATES = {
    "withheld_pending_reconciliation",
    "candidate",
    "published",
    "superseded",
    "withdrawn",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_tree(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if path.is_symlink():
            fail(errors, f"symlink not permitted: {rel}")
            continue
        if path.is_dir():
            continue
        if path.name in FORBIDDEN_FILE_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(errors, f"forbidden credential-like file: {rel}")
        if any(part.lower() in FORBIDDEN_PATH_PARTS for part in rel.parts):
            fail(errors, f"forbidden protected/internal path: {rel}")
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            fail(errors, f"file exceeds {MAX_FILE_BYTES} bytes: {rel} ({size})")
        if path.suffix.lower() in TEXT_SCAN_SUFFIXES and size <= 5 * 1024 * 1024:
            payload = path.read_bytes()
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(payload):
                    fail(errors, f"{label} marker detected in: {rel}")


def _release_files() -> set[str]:
    """Return every regular file in the governed release roots.

    This is deliberately closed-world. A file inside a governed root is either in the
    release manifest or it is a validation failure; there is no unmanifested side channel.
    """
    paths: set[str] = set()
    for root_name in sorted(ALLOWED_RELEASE_ROOTS):
        release_root = ROOT / root_name
        if not release_root.exists():
            continue
        if not release_root.is_dir() or release_root.is_symlink():
            continue
        for path in release_root.rglob("*"):
            if path.is_file() and not path.is_symlink():
                paths.add(path.relative_to(ROOT).as_posix())
    return paths


def _validate_source_metadata(errors: list[str], data: dict[str, Any], state: str | None) -> None:
    if state != "published":
        return
    source = data.get("source")
    if not isinstance(source, dict):
        fail(errors, "published release must contain source provenance metadata")
        return

    source_commit = source.get("source_commit")
    if not isinstance(source_commit, str) or not COMMIT_SHA_RE.fullmatch(source_commit):
        fail(errors, "published release source_commit must be a 40-character lowercase Git SHA")

    source_run_id = source.get("source_run_id")
    if not isinstance(source_run_id, str) or not RUN_ID_RE.fullmatch(source_run_id):
        fail(errors, "published release source_run_id must be a GitHub Actions numeric run id")

    repository_role = source.get("repository_role")
    if repository_role != "private_aq26_scientific_engine":
        fail(errors, "published release repository_role must be private_aq26_scientific_engine")


def _validate_v2_exporter_provenance(errors: list[str], data: dict[str, Any]) -> None:
    if data.get("schema_version") != 2:
        return

    if data.get("manifest_policy") != "closed_world_release_tree":
        fail(errors, "schema v2 manifest_policy must be closed_world_release_tree")

    release_roots = data.get("release_roots")
    if release_roots != sorted(ALLOWED_RELEASE_ROOTS):
        fail(errors, f"schema v2 release_roots must be {sorted(ALLOWED_RELEASE_ROOTS)!r}")

    publication = data.get("publication")
    if not isinstance(publication, dict):
        fail(errors, "schema v2 manifest must contain publication metadata")
    elif publication.get("mode") != "one_way_sanitized_export":
        fail(errors, "schema v2 publication mode must be one_way_sanitized_export")

    exporter = data.get("exporter")
    if not isinstance(exporter, dict):
        fail(errors, "schema v2 manifest must contain exporter provenance")
        return

    if exporter.get("config_path") != "configs/public_repo_export.yml":
        fail(errors, "schema v2 exporter config_path is not canonical")
    if exporter.get("script_path") != "scripts/aq26_prepare_public_repo_export.py":
        fail(errors, "schema v2 exporter script_path is not canonical")

    for key in ("config_sha256", "script_sha256"):
        value = exporter.get(key)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            fail(errors, f"schema v2 exporter {key} must be a lowercase SHA-256 digest")


def validate_manifest(errors: list[str]) -> None:
    if not MANIFEST.exists():
        fail(errors, "PUBLIC_RELEASE_MANIFEST.json missing")
        return
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - fail-closed validator
        fail(errors, f"manifest is not valid JSON: {exc}")
        return
    if not isinstance(data, dict):
        fail(errors, "manifest root must be an object")
        return

    schema_version = data.get("schema_version")
    if schema_version not in {1, 2}:
        fail(errors, "manifest schema_version must be 1 or 2")

    state = data.get("release_state")
    if state not in ALLOWED_STATES:
        fail(errors, f"invalid release_state: {state!r}")

    _validate_source_metadata(errors, data, state if isinstance(state, str) else None)
    _validate_v2_exporter_provenance(errors, data)

    entries = data.get("files")
    if not isinstance(entries, list):
        fail(errors, "manifest files must be a list")
        return
    if state == "published" and not entries:
        fail(errors, "published release must contain at least one manifested file")

    seen: set[str] = set()
    declared_total_bytes = 0
    valid_entry_count = 0

    for entry in entries:
        if not isinstance(entry, dict):
            fail(errors, "manifest file entry must be an object")
            continue

        rel_text = entry.get("path")
        if not isinstance(rel_text, str) or not rel_text:
            fail(errors, "manifest entry missing path")
            continue
        rel = Path(rel_text)
        if rel.is_absolute() or ".." in rel.parts:
            fail(errors, f"unsafe manifest path: {rel_text}")
            continue
        if not rel.parts or rel.parts[0] not in ALLOWED_RELEASE_ROOTS:
            fail(errors, f"manifest path outside approved release roots: {rel_text}")
            continue
        if rel_text in seen:
            fail(errors, f"duplicate manifest path: {rel_text}")
            continue
        seen.add(rel_text)

        expected_sha = entry.get("sha256")
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            fail(errors, f"invalid SHA-256 value in manifest: {rel_text}")
            continue

        expected_size = entry.get("bytes")
        if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
            fail(errors, f"invalid byte count in manifest: {rel_text}")
            continue

        valid_entry_count += 1
        declared_total_bytes += expected_size
        target = ROOT / rel
        if not target.is_file() or target.is_symlink():
            fail(errors, f"manifested file missing or not regular: {rel_text}")
            continue
        if expected_sha != sha256(target):
            fail(errors, f"SHA-256 mismatch: {rel_text}")
        if expected_size != target.stat().st_size:
            fail(errors, f"size mismatch: {rel_text}")

    file_count = data.get("file_count")
    if file_count != len(entries):
        fail(errors, f"manifest file_count mismatch: declared {file_count!r}, entries {len(entries)}")
    if valid_entry_count != len(entries):
        fail(errors, "one or more manifest file entries are structurally invalid")

    total_bytes = data.get("total_bytes")
    if total_bytes != declared_total_bytes:
        fail(
            errors,
            f"manifest total_bytes mismatch: declared {total_bytes!r}, entries total {declared_total_bytes}",
        )

    actual = _release_files()
    for rel_text in sorted(actual - seen):
        fail(errors, f"unmanifested release file: {rel_text}")
    for rel_text in sorted(seen - actual):
        fail(errors, f"manifest lists absent release file: {rel_text}")


def main() -> int:
    errors: list[str] = []
    validate_tree(errors)
    validate_manifest(errors)
    if errors:
        print("AQ26 PUBLIC REPOSITORY VALIDATION FAILED")
        for error in errors:
            print(f" - {error}")
        return 1
    print("AQ26 public repository validation passed: closed-world manifest, hashes and provenance verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
