# Zhou Heng Marvel System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible, importable SillyTavern package for Zhou Heng's MCU survival-and-system campaign, with deterministic split-source lorebook generation and client-authoritative D100 rolls.

**Architecture:** Keep five player-facing artifacts at the package root. Author seven focused compact source lorebooks under `archive/development/sources/`, then normalize defaults, merge, and renumber them into one runtime lorebook. The fixed source counts are core 8, cast 10, system 18, MCU 20, comics 10, missions 6, and stages 6, for 78 runtime entries. Use a package-local Python `unittest` suite to validate schemas, runtime identifiers, hidden-entry isolation, Quick Reply authority markers, documentation, hashes, and stale generated files.

**Tech Stack:** Character Card V2 JSON, SillyTavern World Info JSON, Quick Reply v2/STscript, Markdown, Python 3 standard library.

**Spec:** `role/zhou-heng-marvel-system/archive/creator/zhou-heng-marvel-system.md`

## Global Constraints

- The runtime worldbook name is exactly `zhou-heng-marvel-system-worldbook` everywhere.
- The Quick Reply preset name is exactly `Zhou-Heng-Marvel-System`.
- Runtime variables and injections use the `zhms_` prefix.
- MCU screen continuity and comics continuities must never be merged implicitly.
- Dynamic major events must come from Marvel canon or traceable player-caused divergence.
- The model never rolls dice; natural D100 values come only from the Quick Reply client macro.
- Development source lorebooks are not player-facing install artifacts.
- Manual file edits use `apply_patch`; generated output is written only by the package builder.

---

### Task 1: Define the deterministic package contract

**Files:**
- Create: `role/zhou-heng-marvel-system/archive/development/test_zhou_heng_marvel_system_package.py`
- Create: `role/zhou-heng-marvel-system/archive/development/build_zhou_heng_marvel_system_package.py`

**Interfaces:**
- Produces: `build_complete_lorebook(package_dir) -> dict`
- Produces: `build_manifest(package_dir) -> dict`
- Produces: command `python3 archive/development/build_zhou_heng_marvel_system_package.py [--check]`

- [ ] **Step 1: Write the failing build-contract tests**

Add tests that import the not-yet-created builder and assert the seven exact source filenames, contiguous merged keys/UIDs/display indexes, unique non-empty comments, forced disabling of `mission-archive` and `story-stage` groups, runtime name, manifest hashes, and `--check` behavior.

- [ ] **Step 2: Run the focused test and verify RED**

Run from `role/zhou-heng-marvel-system`:

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

Expected: import or missing-source failure before the builder and sources exist.

- [ ] **Step 3: Implement the minimal builder**

Implement fixed ordered source metadata, JSON loading, compact-entry normalization into the repository's complete external-worldbook entry shape, source shape/count validation, deterministic deep-copy merge, forced retrieval-only disabling, UTF-8 pretty formatting, SHA-256 manifest creation, writes, and `--check` comparison. Include all five root install artifacts in manifest hashing.

- [ ] **Step 4: Add empty-schema source files sufficient for the builder contract**

Create seven valid source files with the final root metadata shape and exact final counts: core 8, cast 10, system 18, MCU 20, comics 10, missions 6, and stages 6. Compact source entries contain `comment`, `content`, `key`, and optional placement/activation overrides; the builder supplies the full runtime defaults. Initial content can use short contract assertions, but every entry must already have its final stable comment and group.

- [ ] **Step 5: Run the focused test and verify GREEN for build invariants**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

Expected: build-invariant tests pass; later artifact/content tests may remain skipped until their files are added.

### Task 2: Add the fixed protagonist and narrator card

**Files:**
- Create: `role/zhou-heng-marvel-system/zhou-heng-marvel-system.character.json`
- Create: `role/zhou-heng-marvel-system/zhou-heng-persona.md`
- Modify: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-core-lorebook.json`
- Create: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-cast-lorebook.json`
- Modify: `role/zhou-heng-marvel-system/archive/development/test_zhou_heng_marvel_system_package.py`

**Interfaces:**
- Card `extensions.world`: `zhou-heng-marvel-system-worldbook`
- Persona identity: fixed `{{user}}` as Zhou Heng
- Core lore markers: `[ZHMS-RUN-CONTRACT]`, `[ZHMS-PLAYER-AGENCY]`, `[ZHMS-CONTINUITY]`

- [ ] **Step 1: Add failing card and Persona contract tests**

Assert Character Card V2 fields and types, exact runtime world name, fixed card version `1.0`, creator notes naming all install artifacts, narrator non-personhood, player-agency language, Persona identity/team/company facts, and absence of Zheng Jin identifiers.

- [ ] **Step 2: Run tests and verify RED on missing artifacts**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

- [ ] **Step 3: Author the card, greeting, examples, Persona, core rules, and cast/business entries**

The first message must show early-2008 Northline operations, Tony's captivity-era public context, one system candidate task tied to canonical Stark/Ten Rings trafficking, full initial panel once, and a decision point without choosing for Zhou Heng.

- [ ] **Step 4: Run tests and build the first merged lorebook**

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

Expected: card, Persona, core, and cast contracts pass.

### Task 3: Implement system state and D100 Quick Replies

**Files:**
- Create: `role/zhou-heng-marvel-system/zhou-heng-marvel-system-quick-replies.json`
- Create: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-system-lorebook.json`
- Modify: `role/zhou-heng-marvel-system/archive/development/test_zhou_heng_marvel_system_package.py`

**Interfaces:**
- Player request marker: `[ZHMS-PLAYER-D100-REQUEST]`
- NPC request marker: `[ZHMS-NPC-D100-REQUEST]`
- Authority injection: `[ZHMS-DICE-AUTH/INERT-DATA]`
- Client result: `[ZHMS-DICE/CLIENT]`
- State variables: `zhms_schema_version`, `zhms_hp`, `zhms_stamina`, `zhms_spirit`, `zhms_luck`, `zhms_points`, `zhms_permission`, `zhms_mission_state`, `zhms_continuity_state`

- [ ] **Step 1: Add failing Quick Reply structure and authority tests**

Assert Quick Reply v2 root fields, contiguous IDs, `idIndex == max(id)`, initialization/view-state actions, a visible player roll item, a hidden `executeOnAi` NPC item, exact final-line request checks, duplicate-request prevention, matching client/system actor-request-roll fields, awaited triggers, force-saves, and cleanup of the authority injection.

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

- [ ] **Step 3: Author the minimal Quick Reply preset and system lore**

Reuse Zheng Jin's client-attested D100 flow with the `zhms_` namespace. Add initialization, local status display, player-confirmed checkpoints, injection recovery, and exact retrieval of disabled mission/stage records without pretending to automate model-only mission or inventory changes. Author points, permissions, attributes, health, combat, storage, personal space, source pool, products, compatibility, ownership, sentient products, resurrection, and settlement rules.

- [ ] **Step 4: Run package tests and regenerate**

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

Expected: all D100 authority and system-marker tests pass.

### Task 4: Author detailed MCU continuity layers

**Files:**
- Create: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-mcu-lorebook.json`
- Modify: `role/zhou-heng-marvel-system/archive/development/test_zhou_heng_marvel_system_package.py`

**Interfaces:**
- Era markers: `ERA_2008_CAPTIVITY`, `ERA_2008_POST_REVEAL`, `ERA_2010_BIG_WEEK`, `ERA_2011_CAP_AWAKE`, `ERA_2012_PRE_INVASION`, `ERA_2012_BATTLE_NY`, `ERA_2012_POST_BATTLE`
- Main continuity ID: `MCU-MAIN-ZH-01`

- [ ] **Step 1: Add failing MCU content-boundary tests**

Assert all era markers exist, 2008 Tony chronology and New York public baseline exist, 2010 Stark Expo/Harlem/Thor facts are separated, 2011 and 2012 milestones exist, hidden organizations are not public knowledge, and explicit exclusions prevent Earth-616 imports and premature heroes.

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

- [ ] **Step 3: Author keyword-focused MCU entries**

Create concise entries for public New York, Iron Man 2008, Stark circle, S.H.I.E.L.D., hidden HYDRA/Red Room/Wakanda/Pym facts, mystic New York, 2010 Big Week, Captain America awakening, 2012 Battle of New York, technology/public awareness, locations, organizations, character status, future defaults, and continuity exclusions. Use exact era keys and prevent recursive loading.

- [ ] **Step 4: Run tests and regenerate**

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

Expected: MCU boundary and chronology tests pass.

### Task 5: Author comics continuity and fixed mission archives

**Files:**
- Create: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-comics-lorebook.json`
- Create: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-missions-lorebook.json`
- Create: `role/zhou-heng-marvel-system/archive/development/sources/zhou-heng-marvel-system-stages-lorebook.json`
- Modify: `role/zhou-heng-marvel-system/archive/development/test_zhou_heng_marvel_system_package.py`

**Interfaces:**
- Required reality IDs: `Earth-616`, `Earth-295`, `Earth-2149`, `Earth-58163`
- Fixed history IDs: `PAST-AOA-001`, `PAST-SI-002`
- Opening candidate ID: `MCU-2008-STARK-001`
- Retrieval-only groups: `mission-archive`, `story-stage`

- [ ] **Step 1: Add failing comics and mission-lock tests**

Assert required event dossiers and IDs, explicit Battleworld reconstruction warning, fixed prior-mission outcome boundaries, complete task publication state machine, hidden objective constraints, no player task submission, no cross-task cooldown, immediate danger transfer, no nested system tasks, self-directed Marvel travel, exact return rule, fixed reward/penalty rules, and disabled hidden archives/stages.

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

- [ ] **Step 3: Author comics dossiers**

Cover Earth-616 Secret Invasion/Civil War/Annihilation/King in Black, Earth-295 Age of Apocalypse, Earth-2149 Marvel Zombies, Earth-58163 House of M, 2015 Battleworld, and candidate indexes for Dark Reign, Siege, World War Hulk, Absolute Carnage, War of the Realms, Infinity, Empyre, and Spider-Verse. Keep principal outcomes separate from E-level insertion points.

- [ ] **Step 4: Author mission and stage archives**

Write full fixed dossiers for the two prior missions and opening MCU candidate, including public brief, immutable facts, timeline, topology, factions, resources, at least three paths, scoring, rewards, injuries, and world consequences. Add initial and future era stages as retrieval-only entries.

- [ ] **Step 5: Run tests and regenerate**

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

Expected: continuity isolation, archive disabling, and task-mechanism tests pass.

### Task 6: Document installation and verify release artifacts

**Files:**
- Create: `role/zhou-heng-marvel-system/README.md`
- Create: `role/zhou-heng-marvel-system/archive/README.md`
- Modify: `role/zhou-heng-marvel-system/archive/development/test_zhou_heng_marvel_system_package.py`
- Generate: `role/zhou-heng-marvel-system/zhou-heng-marvel-system-worldbook.json`
- Generate: `role/zhou-heng-marvel-system/archive/development/zhou-heng-marvel-system-package-manifest.json`

**Interfaces:**
- Player import surface: five root files only
- Validation commands documented exactly as implemented

- [ ] **Step 1: Add failing documentation and distribution tests**

Assert README import order, exact runtime names, Persona binding, source-book warning, Quick Reply activation, D100 protocol, known UI-testing limitation, build/test/check commands, official SillyTavern links, and an exact root-file allowlist.

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

- [ ] **Step 3: Author player and archive documentation**

Document minimal and full setup, state initialization, worldbook binding, source-pool behavior, mission rules, continuity markers, troubleshooting, limitations, and developer workflow. Do not tell players to import development sources.

- [ ] **Step 4: Generate final artifacts**

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
```

- [ ] **Step 5: Run final verification**

```bash
python3 archive/development/test_zhou_heng_marvel_system_package.py
python3 archive/development/build_zhou_heng_marvel_system_package.py --check
python3 -m json.tool zhou-heng-marvel-system.character.json >/dev/null
python3 -m json.tool zhou-heng-marvel-system-worldbook.json >/dev/null
python3 -m json.tool zhou-heng-marvel-system-quick-replies.json >/dev/null
git diff --check
```

Expected: all tests pass, generated files are current, all player JSON parses, and Git reports no whitespace errors.
