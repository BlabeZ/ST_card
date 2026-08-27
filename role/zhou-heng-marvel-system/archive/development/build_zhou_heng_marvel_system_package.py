import argparse
import copy
import hashlib
import json
from pathlib import Path


OUTPUT_FILE = "zhou-heng-marvel-system-worldbook.json"
MANIFEST_FILE = Path(
    "archive/development/zhou-heng-marvel-system-package-manifest.json"
)
SOURCE_DIR = Path("archive/development/sources")
PACKAGE_VERSION = "1.0.0"
RUNTIME_NAME = "zhou-heng-marvel-system-worldbook"
SOURCES = (
    ("zhou-heng-marvel-system-core-lorebook.json", 8, "core"),
    ("zhou-heng-marvel-system-cast-lorebook.json", 10, "cast"),
    ("zhou-heng-marvel-system-system-lorebook.json", 18, "system"),
    ("zhou-heng-marvel-system-mcu-lorebook.json", 20, "mcu"),
    ("zhou-heng-marvel-system-comics-lorebook.json", 10, "comics"),
    ("zhou-heng-marvel-system-missions-lorebook.json", 6, "mission-archive"),
    ("zhou-heng-marvel-system-stages-lorebook.json", 6, "story-stage"),
)


def _load_json(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def _source_entries(package_dir, filename, expected_count):
    source = _load_json(package_dir / SOURCE_DIR / filename)
    entries = source.get("entries")
    if not isinstance(entries, dict) or len(entries) != expected_count:
        actual = len(entries) if isinstance(entries, dict) else "invalid entries"
        raise ValueError(f"{filename}: expected {expected_count} entries, got {actual}")
    expected_keys = [str(index) for index in range(expected_count)]
    if list(entries) != expected_keys:
        raise ValueError(f"{filename}: entries must use ordered zero-based keys")
    return entries.values()


def _normalized_entry(source_entry, uid, category):
    source_entry = copy.deepcopy(source_entry)
    comment = source_entry.pop("comment", None)
    content = source_entry.pop("content", None)
    if not isinstance(comment, str) or not comment.strip():
        raise ValueError("every entry needs a non-empty comment")
    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"{comment}: every entry needs non-empty content")

    entry = {
        "uid": uid,
        "key": [],
        "keysecondary": [],
        "comment": comment,
        "content": content,
        "constant": False,
        "vectorized": False,
        "selective": True,
        "selectiveLogic": 0,
        "addMemo": False,
        "order": 200,
        "position": 1,
        "disable": False,
        "ignoreBudget": False,
        "excludeRecursion": True,
        "preventRecursion": True,
        "matchPersonaDescription": False,
        "matchCharacterDescription": False,
        "matchCharacterPersonality": False,
        "matchCharacterDepthPrompt": False,
        "matchScenario": False,
        "matchCreatorNotes": False,
        "delayUntilRecursion": 0,
        "probability": 100,
        "useProbability": True,
        "depth": 4,
        "outletName": "",
        "group": "",
        "groupOverride": False,
        "groupWeight": 100,
        "scanDepth": 4,
        "caseSensitive": False,
        "matchWholeWords": False,
        "useGroupScoring": False,
        "automationId": "",
        "role": 0,
        "sticky": None,
        "cooldown": None,
        "delay": None,
        "triggers": [],
        "displayIndex": uid,
        "characterFilter": {"isExclude": False, "names": [], "tags": []},
    }
    unknown = set(source_entry) - set(entry)
    if unknown:
        raise ValueError(f"{comment}: unsupported source fields: {sorted(unknown)}")
    entry.update(source_entry)
    entry["uid"] = uid
    entry["displayIndex"] = uid
    entry["group"] = ""
    if category in {"mission-archive", "story-stage"}:
        entry["disable"] = True
        entry["sticky"] = None
    return entry


def build_complete_lorebook(package_dir):
    package_dir = Path(package_dir)
    merged_entries = {}
    comments = set()

    for filename, expected_count, category in SOURCES:
        for source_entry in _source_entries(package_dir, filename, expected_count):
            uid = len(merged_entries)
            entry = _normalized_entry(source_entry, uid, category)
            if entry["comment"] in comments:
                raise ValueError(f"duplicate entry comment: {entry['comment']}")
            comments.add(entry["comment"])
            merged_entries[str(uid)] = entry

    return {
        "name": RUNTIME_NAME,
        "description": (
            "周衡漫威系统完整世界书。由七份开发源确定性生成；"
            "固定任务档案与故事阶段仅供精确检索。"
        ),
        "scanDepth": 4,
        "tokenBudget": 12288,
        "recursiveScanning": False,
        "extensions": {
            "packageVersion": PACKAGE_VERSION,
            "runtimeName": RUNTIME_NAME,
        },
        "entries": merged_entries,
    }


def _sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def _formatted_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def build_manifest(package_dir):
    package_dir = Path(package_dir)
    lorebook = build_complete_lorebook(package_dir)
    output_bytes = _formatted_json(lorebook).encode("utf-8")
    sources = []
    for filename, count, category in SOURCES:
        sources.append(
            {
                "file": (SOURCE_DIR / filename).as_posix(),
                "entries": count,
                "category": category,
                "sha256": _sha256_bytes(
                    (package_dir / SOURCE_DIR / filename).read_bytes()
                ),
            }
        )

    artifacts = []
    for filename in (
        "README.md",
        "zhou-heng-marvel-system.character.json",
        OUTPUT_FILE,
        "zhou-heng-marvel-system-quick-replies.json",
        "zhou-heng-persona.md",
    ):
        value = output_bytes if filename == OUTPUT_FILE else (package_dir / filename).read_bytes()
        artifacts.append({"file": filename, "sha256": _sha256_bytes(value)})

    return {
        "schemaVersion": 1,
        "packageVersion": PACKAGE_VERSION,
        "runtimeLorebookName": RUNTIME_NAME,
        "output": OUTPUT_FILE,
        "outputEntries": len(lorebook["entries"]),
        "outputSha256": _sha256_bytes(output_bytes),
        "installArtifacts": artifacts,
        "sources": sources,
    }


def _write_or_check(path, value, check):
    expected = _formatted_json(value)
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"outdated generated artifact: {path.name}")
        return
    path.write_text(expected, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Build the Zhou Heng Marvel System package artifacts."
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
