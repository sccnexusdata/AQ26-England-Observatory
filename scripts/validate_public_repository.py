from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

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
    ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".css", ".js", ".py", ".csv", ".xml"
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


def validate_manifest(errors: list[str]) -> None:
    if not MANIFEST.exists():
        fail(errors, "PUBLIC_RELEASE_MANIFEST.json missing")
        return
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - fail-closed validator
        fail(errors, f"manifest is not valid JSON: {exc}")
        return

    if data.get("schema_version") != 1:
        fail(errors, "manifest schema_version must be 1")
    state = data.get("release_state")
    allowed_states = {"withheld_pending_reconciliation", "candidate", "published", "superseded", "withdrawn"}
    if state not in allowed_states:
        fail(errors, f"invalid release_state: {state!r}")

    entries = data.get("files")
    if not isinstance(entries, list):
        fail(errors, "manifest files must be a list")
        return
    if state == "published" and not entries:
        fail(errors, "published release must contain at least one manifested file")

    seen: set[str] = set()
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
        if rel.parts[0] not in ALLOWED_RELEASE_ROOTS:
            fail(errors, f"manifest path outside approved release roots: {rel_text}")
            continue
        if rel_text in seen:
            fail(errors, f"duplicate manifest path: {rel_text}")
            continue
        seen.add(rel_text)
        target = ROOT / rel
        if not target.is_file():
            fail(errors, f"manifested file missing: {rel_text}")
            continue
        expected_sha = entry.get("sha256")
        if expected_sha != sha256(target):
            fail(errors, f"SHA-256 mismatch: {rel_text}")
        expected_size = entry.get("bytes")
        if expected_size != target.stat().st_size:
            fail(errors, f"size mismatch: {rel_text}")


def main() -> int:
    errors: list[str] = []
    validate_tree(errors)
    validate_manifest(errors)
    if errors:
        print("AQ26 PUBLIC REPOSITORY VALIDATION FAILED")
        for error in errors:
            print(f" - {error}")
        return 1
    print("AQ26 public repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
