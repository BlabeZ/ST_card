import argparse
import copy
import hashlib
import json
from pathlib import Path


OUTPUT_FILE = "rosamund-complete-lorebook.json"
MANIFEST_FILE = Path("archive/development/rosamund-package-manifest.json")
SOURCE_DIR = Path("archive/development/sources")
PACKAGE_VERSION = "3.0.0"
RUNTIME_NAME = "rosamund-complete-lorebook"
SOURCES = (
    ("rosamund-city-lorebook.json", 12, "rosamund-city"),
    ("rosamund-factions-lorebook.json", 12, "rosamund-factions"),
    ("rosamund-cast-lorebook.json", 9, "rosamund-cast"),
    ("rosamund-rules-lorebook.json", 11, "rosamund-rules"),
    ("rosamund-core-cases-lorebook.json", 12, "rosamund-core-case"),
    ("rosamund-hale-story-stages-lorebook.json", 6, "rosamund-story-stage"),
)


def _load_json(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def _source_entries(package_dir, filename, expected_count):
    source = _load_json(package_dir / SOURCE_DIR / filename)
    entries = source.get("entries")
    if not isinstance(entries, dict) or len(entries) != expected_count:
        raise ValueError(
            f"{filename}: expected {expected_count} entries, got "
            f"{len(entries) if isinstance(entries, dict) else 'invalid entries'}"
        )
    expected_keys = [str(index) for index in range(expected_count)]
    if list(entries) != expected_keys:
        raise ValueError(f"{filename}: entries must use ordered zero-based keys")
    return entries.values()


def build_complete_lorebook(package_dir):
    package_dir = Path(package_dir)
    merged_entries = {}
    comments = set()

    for filename, expected_count, group in SOURCES:
        for source_entry in _source_entries(package_dir, filename, expected_count):
            entry = copy.deepcopy(source_entry)
            comment = entry.get("comment")
            if not isinstance(comment, str) or not comment.strip():
                raise ValueError(f"{filename}: every entry needs a non-empty comment")
            if comment in comments:
                raise ValueError(f"duplicate entry comment: {comment}")
            comments.add(comment)

            index = len(merged_entries)
            entry["uid"] = index
            entry["displayIndex"] = index
            if group in {"rosamund-core-case", "rosamund-story-stage"}:
                entry["disable"] = True
            if group == "rosamund-core-case":
                entry["sticky"] = None
            merged_entries[str(index)] = entry

    return {
        "name": "Rosamund-Hale-Complete",
        "description": (
            "罗莎蒙德·黑尔完整世界书。由六份开发源确定性生成；"
            "核心案件与秘密阶段仅供 Quick Reply 精确读取。"
        ),
        "scanDepth": 4,
        "tokenBudget": 8192,
        "recursiveScanning": False,
        "extensions": {
            "rosamundPackageVersion": PACKAGE_VERSION,
            "runtimeName": RUNTIME_NAME,
        },
        "entries": merged_entries,
    }


def _sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def build_manifest(package_dir):
    package_dir = Path(package_dir)
    lorebook = build_complete_lorebook(package_dir)
    output_bytes = _formatted_json(lorebook).encode("utf-8")
    source_manifest = []
    for filename, count, group in SOURCES:
        source_manifest.append(
            {
                "file": (SOURCE_DIR / filename).as_posix(),
                "entries": count,
                "group": group,
                "sha256": _sha256_bytes(
                    (package_dir / SOURCE_DIR / filename).read_bytes()
                ),
            }
        )
    install_artifacts = []
    for filename in (
        "rosamund-hale.character.json",
        OUTPUT_FILE,
        "rosamund-quick-replies.json",
    ):
        artifact_bytes = output_bytes if filename == OUTPUT_FILE else (package_dir / filename).read_bytes()
        install_artifacts.append(
            {
                "file": filename,
                "sha256": _sha256_bytes(artifact_bytes),
            }
        )
    return {
        "schemaVersion": 1,
        "packageVersion": PACKAGE_VERSION,
        "runtimeLorebookName": RUNTIME_NAME,
        "output": OUTPUT_FILE,
        "outputEntries": len(lorebook["entries"]),
        "outputSha256": _sha256_bytes(output_bytes),
        "installArtifacts": install_artifacts,
        "sources": source_manifest,
    }


def _formatted_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _write_or_check(path, value, check):
    expected = _formatted_json(value)
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"outdated generated artifact: {path.name}")
        return
    path.write_text(expected, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Build the canonical Rosamund Hale lorebook from development sources."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if checked-in generated artifacts are missing or outdated",
    )
    args = parser.parse_args()
    package_dir = Path(__file__).resolve().parents[2]

    _write_or_check(
        package_dir / OUTPUT_FILE,
        build_complete_lorebook(package_dir),
        args.check,
    )
    _write_or_check(
        package_dir / MANIFEST_FILE,
        build_manifest(package_dir),
        args.check,
    )


if __name__ == "__main__":
    main()
