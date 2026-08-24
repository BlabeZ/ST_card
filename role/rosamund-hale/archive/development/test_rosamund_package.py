import json
import hashlib
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import build_complete_lorebook as builder


def load_json(name):
    with (PACKAGE_DIR / name).open(encoding="utf-8") as source:
        return json.load(source)


class CompleteLorebookTests(unittest.TestCase):
    def test_build_merges_every_source_entry_with_stable_indices(self):
        lorebook = builder.build_complete_lorebook(PACKAGE_DIR)
        entries = lorebook["entries"]

        self.assertEqual(62, len(entries))
        self.assertEqual([str(index) for index in range(62)], list(entries))
        self.assertEqual(list(range(62)), [entry["uid"] for entry in entries.values()])
        self.assertEqual(
            list(range(62)),
            [entry["displayIndex"] for entry in entries.values()],
        )
        comments = [entry["comment"] for entry in entries.values()]
        self.assertEqual(len(comments), len(set(comments)))

    def test_build_preserves_source_order_and_counts(self):
        lorebook = builder.build_complete_lorebook(PACKAGE_DIR)
        groups = [entry.get("group") for entry in lorebook["entries"].values()]

        self.assertEqual(["rosamund-city"] * 12, groups[0:12])
        self.assertEqual(["rosamund-factions"] * 12, groups[12:24])
        self.assertEqual(["rosamund-cast"] * 9, groups[24:33])
        self.assertEqual([""] * 11, groups[33:44])
        self.assertEqual(["rosamund-core-case"] * 12, groups[44:56])
        self.assertEqual(["rosamund-story-stage"] * 6, groups[56:62])

    def test_complete_book_keeps_retrieval_only_entries_disabled(self):
        lorebook = builder.build_complete_lorebook(PACKAGE_DIR)
        entries = list(lorebook["entries"].values())
        core_cases = [entry for entry in entries if entry["comment"].startswith("GH-")]
        stages = [
            entry for entry in entries if entry["comment"].startswith("罗莎蒙德阶段")
        ]

        self.assertEqual(12, len(core_cases))
        self.assertEqual(6, len(stages))
        self.assertTrue(all(entry["disable"] for entry in core_cases + stages))
        self.assertTrue(all(entry["sticky"] is None for entry in core_cases))

    def test_checked_in_artifacts_match_the_deterministic_build(self):
        self.assertEqual(
            builder.build_complete_lorebook(PACKAGE_DIR),
            load_json(builder.OUTPUT_FILE),
        )
        self.assertEqual(builder.build_manifest(PACKAGE_DIR), load_json(builder.MANIFEST_FILE))

    def test_manifest_hashes_exact_install_artifact_bytes(self):
        manifest = load_json(builder.MANIFEST_FILE)
        artifacts = {item["file"]: item["sha256"] for item in manifest["installArtifacts"]}

        for filename in (
            "rosamund-hale.character.json",
            builder.OUTPUT_FILE,
            "rosamund-quick-replies.json",
        ):
            with self.subTest(filename=filename):
                digest = hashlib.sha256((PACKAGE_DIR / filename).read_bytes()).hexdigest()
                self.assertEqual(digest, artifacts[filename])
        self.assertEqual(artifacts[builder.OUTPUT_FILE], manifest["outputSha256"])


class RuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quick_replies = load_json("rosamund-quick-replies.json")
        cls.by_label = {
            item["label"]: item["message"] for item in cls.quick_replies["qrList"]
        }

    def test_runtime_uses_only_the_complete_lorebook_name(self):
        messages = "\n".join(self.by_label.values())
        rules = load_json(builder.SOURCE_DIR / "rosamund-rules-lorebook.json")
        rule_text = "\n".join(entry["content"] for entry in rules["entries"].values())

        self.assertIn("rosamund-complete-lorebook", messages)
        self.assertNotIn("rosamund-core-cases-lorebook", messages)
        self.assertIn("rosamund-complete-lorebook", rule_text)
        self.assertNotIn("rosamund-core-cases-lorebook", rule_text)

    def test_core_case_lookup_verifies_the_exact_comment(self):
        launcher = self.by_label["选择并启动12个核心案件"]

        self.assertIn(
            "/getentryfield file=rosamund-complete-lorebook field=comment",
            launcher,
        )
        self.assertIn("rh_found_core_comment", launcher)
        self.assertIn("left=rh_found_core_comment right=rh_pending_core rule=neq", launcher)

    def test_core_completion_uses_exact_ids_separate_from_dynamic_cases(self):
        launcher = self.by_label["选择并启动12个核心案件"]
        settlement = self.by_label["结算当前案件"]

        self.assertIn("rh_completed_core", launcher)
        self.assertIn("rh_completed_core", settlement)
        self.assertIn("rh_case_id", settlement)
        self.assertNotIn("right=rh_pending_core rule=in", launcher)

    def test_case_history_and_active_ledger_are_bounded(self):
        board = self.by_label["整理案件板"]
        settlement = self.by_label["结算当前案件"]

        self.assertIn("rh_active_case_state", board)
        self.assertIn("/inject id=rh_active_case_state", board)
        self.assertIn("/trimtokens limit=700", board)
        self.assertIn("/substr start=0 end=4000", board)
        self.assertIn("/trimtokens limit=1200 direction=end", settlement)
        self.assertIn("/substr start=-6000", settlement)
        self.assertIn("[RH-CONTINUITY/INERT-DATA]", settlement)

    def test_stage_state_is_retrieved_and_injected_per_chat(self):
        initialize = self.by_label["初始化状态"]
        stage = self.by_label["设置剧情阶段"]
        repair = self.by_label["诊断与修复状态"]

        self.assertIn("/run 诊断与修复状态", initialize)
        for message in (stage, repair):
            self.assertIn("rosamund-complete-lorebook", message)
            self.assertIn("/inject id=rh_story_stage_state", message)
            self.assertNotIn("/setentryfield", message)

    def test_quick_reply_ids_and_closures_are_balanced(self):
        items = self.quick_replies["qrList"]
        ids = [item["id"] for item in items]

        self.assertEqual(list(range(1, 21)), ids)
        for item in items:
            with self.subTest(label=item["label"]):
                self.assertEqual(
                    item["message"].count("{:"),
                    item["message"].count(":}"),
                )

    def test_critical_updates_use_journal_and_force_save(self):
        labels = (
            "确认并锁定动态案件",
            "选择并启动12个核心案件",
            "结算当前案件",
            "记录五轴结局",
            "应用限定改案",
        )

        for label in labels:
            with self.subTest(label=label):
                message = self.by_label[label]
                self.assertIn("rh_txn_kind", message)
                prepared = message.index("/setvar key=rh_txn_phase prepared")
                first_save = message.index("/forcesave", prepared)
                applied = message.index("/setvar key=rh_txn_phase applied", first_save)
                second_save = message.index("/forcesave", applied)
                cleared = message.index("/flushvar rh_txn_kind", second_save)
                final_save = message.index("/forcesave", cleared)
                self.assertLess(prepared, first_save)
                self.assertLess(first_save, applied)
                self.assertLess(applied, second_save)
                self.assertLess(second_save, cleared)
                self.assertLess(cleared, final_save)

    def test_package_has_schema_migration_and_recovery_action(self):
        repair = self.by_label["诊断与修复状态"]

        self.assertIn("rh_schema_version", repair)
        self.assertIn("rh_completed_core", repair)
        self.assertIn("rh_active_case", repair)
        self.assertIn("rh_active_case_state", repair)
        self.assertIn("rh_case_continuity", repair)
        self.assertIn("rh_story_stage_state", repair)
        self.assertIn("rh_daily_name_state", repair)
        self.assertIn("rh_ending_state", repair)
        self.assertIn("/substr start=-6000", repair)
        for operation in (
            "start-core",
            "start-dynamic",
            "settle-case",
            "set-ending",
            "patch-case",
        ):
            self.assertIn(f"left=rh_recovered_txn right={operation}", repair)
        self.assertIn("rh_quarantine_case_file", repair)
        self.assertIn("rh_quarantine_case_history", repair)
        self.assertIn("rh_quarantine_active_case_state", repair)
        for variable in ("rh_case_history", "rh_active_case_state", "rh_daily_name"):
            self.assertIn(f'left={variable} right="\\{{\\{{"', repair)
            self.assertIn(f'left={variable} right="}}}}"', repair)
        self.assertIn('left=rh_case_candidate right="【真相锁】"', repair)
        for axis in "hvapl":
            self.assertIn(f"rh_valid_ending_{axis}", repair)
        self.assertIn("multiple=true", repair)
        self.assertIn("/forcesave", repair)

    def test_triggers_wait_for_generation_completion(self):
        for label, message in self.by_label.items():
            if "/trigger" not in message:
                continue
            with self.subTest(label=label):
                self.assertNotIn("/trigger |", message)
                self.assertNotEqual("/trigger", message.rstrip().rsplit(" ", 1)[-1])
                self.assertIn("/trigger await=true", message)

    def test_generated_state_rejects_macro_delimiters(self):
        generated_values = {
            "整理案件板": ("rh_case_board",),
            "提议动态案件": ("rh_case_proposal",),
            "确认并锁定动态案件": ("rh_case_candidate",),
            "结算当前案件": ("rh_case_result", "rh_case_summary"),
            "NPC暗D100": ("rh_hidden_consequence",),
        }

        for label, variables in generated_values.items():
            message = self.by_label[label]
            for variable in variables:
                with self.subTest(label=label, variable=variable):
                    self.assertIn(f'left={variable} right="\\{{\\{{"', message)
                    self.assertIn(f'left={variable} right="}}}}"', message)

    def test_dynamic_dossier_has_machine_checked_shape_and_size(self):
        dynamic = self.by_label["确认并锁定动态案件"]
        required_markers = (
            "【案件标题】",
            "【唯一真相】",
            "【完整时间线】",
            "【核心线索1】",
            "【核心线索4】",
            "【可行结局1】",
            "【可行结局2】",
            "【真相锁】",
        )

        for marker in required_markers:
            self.assertIn(marker, dynamic)
        self.assertIn("rh_case_candidate_length", dynamic)
        self.assertIn("right=800 rule=lt", dynamic)
        self.assertIn("right=12000 rule=gt", dynamic)

    def test_scoped_patch_preserves_the_original_dossier_bytes(self):
        patch = self.by_label["应用限定改案"]

        self.assertNotIn("/gen lock=on", patch)
        self.assertIn("/getvar rh_case_file | /setvar key=rh_case_patch_base", patch)
        self.assertIn("[RH-AUTHORIZED-PATCH]", patch)
        self.assertIn("rh_case_patch_base", patch)
        self.assertIn("rh_pending_case_patch", patch)

    def test_settlement_enforces_the_documented_character_limit(self):
        settlement = self.by_label["结算当前案件"]

        self.assertIn("/substr start=0 end=180", settlement)

    def test_transaction_counters_have_explicit_zero_defaults(self):
        cases = {
            "确认并锁定动态案件": "rh_dynamic_counter",
            "结算当前案件": "rh_completed_count",
            "应用限定改案": "rh_case_patch_count",
        }

        for label, variable in cases.items():
            with self.subTest(label=label):
                message = self.by_label[label]
                self.assertIn(
                    f'/getvar {variable} | /if left={variable} right="" rule=eq '
                    f'{{: /setvar key={variable} 0 :}}',
                    message,
                )

    def test_mutations_cannot_overwrite_an_unfinished_journal(self):
        labels = (
            "初始化状态",
            "整理案件板",
            "确认并锁定动态案件",
            "选择并启动12个核心案件",
            "结算当前案件",
            "清除当前案件",
            "设置剧情阶段",
            "记录日常名字",
            "记录五轴结局",
            "应用限定改案",
        )

        for label in labels:
            with self.subTest(label=label):
                self.assertIn("未完成事务", self.by_label[label])
                self.assertIn("/run 诊断与修复状态", self.by_label[label])

    def test_dynamic_title_is_checked_at_the_dossier_prefix(self):
        dynamic = self.by_label["确认并锁定动态案件"]

        self.assertIn("rh_expected_case_title", dynamic)
        self.assertIn("rh_actual_case_title", dynamic)
        self.assertIn("left=rh_actual_case_title right=rh_expected_case_title rule=neq", dynamic)

    def test_legacy_macro_forms_are_rejected_before_persistence(self):
        labels = (
            "整理案件板",
            "确认并锁定动态案件",
            "结算当前案件",
            "记录日常名字",
        )
        legacy_macros = ("<USER>", "<BOT>", "<CHAR>", "<GROUP>", "<CHARIFNOTGROUP>")

        for label in labels:
            for macro in legacy_macros:
                with self.subTest(label=label, macro=macro):
                    self.assertIn(macro, self.by_label[label])

    def test_scoped_patch_requires_a_machine_selected_field(self):
        patch = self.by_label["应用限定改案"]
        repair = self.by_label["诊断与修复状态"]

        self.assertIn("rh_pending_patch_field", patch)
        self.assertIn("rh_pending_patch_value", patch)
        self.assertIn("字段={{getvar::rh_pending_patch_field}}", patch)
        self.assertIn("rh_recovered_patch_prefix", repair)
        self.assertIn("left=rh_recovered_patch_prefix right=rh_case_patch_base rule=neq", repair)

    def test_repair_finishes_or_preserves_transactions_and_migrations(self):
        repair = self.by_label["诊断与修复状态"]

        self.assertIn("/setvar key=rh_txn_phase applied", repair)
        self.assertIn("确认零个核心案件", repair)
        self.assertIn("取消迁移", repair)
        self.assertIn("/abort", repair)
        self.assertIn("left=rh_case_status right=active rule=neq", repair)
        self.assertIn("/flushinject rh_active_case", repair)

    def test_history_fallback_preserves_the_newest_record(self):
        settlement = self.by_label["结算当前案件"]
        repair = self.by_label["诊断与修复状态"]

        self.assertIn("rh_txn_hard_history_tail", settlement)
        self.assertIn("right=rh_case_summary rule=nin", settlement)
        self.assertIn("rh_repair_history_tail_marker", repair)
        self.assertIn("right=rh_repair_history_tail_marker rule=nin", repair)

    def test_freeform_identifiers_are_length_limited(self):
        dynamic = self.by_label["确认并锁定动态案件"]
        daily_name = self.by_label["记录日常名字"]

        self.assertIn(r'/^[^\r\n|]{1,40}$/', dynamic)
        self.assertIn(r'/^[^\r\n|]{1,24}$/', daily_name)


class DocumentationContractTests(unittest.TestCase):
    def test_character_card_describes_the_three_artifact_install(self):
        card = load_json("rosamund-hale.character.json")["data"]
        notes = card["creator_notes"]

        self.assertEqual("3.0", card["character_version"])
        self.assertIn("rosamund-complete-lorebook.json", notes)
        self.assertIn("rosamund-quick-replies.json", notes)
        self.assertIn("跳过Import Card Lore", notes)
        self.assertNotIn("rosamund-core-cases-lorebook", notes)

    def test_user_docs_use_local_stage_injection_and_recovery(self):
        readme = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8")
        ooc = (PACKAGE_DIR / "rosamund-ooc-commands.md").read_text(encoding="utf-8")

        self.assertIn("只导入 `rosamund-complete-lorebook.json`", readme)
        self.assertIn("rh_story_stage_state", readme)
        self.assertIn("诊断与修复状态", readme)
        self.assertIn("rh_story_stage_state", ooc)
        self.assertIn("recovery-required", ooc)
        self.assertNotIn("rosamund-core-cases-lorebook` 读取", ooc)

    def test_stage_sources_no_longer_require_global_manual_toggles(self):
        stages = load_json(
            builder.SOURCE_DIR / "rosamund-hale-story-stages-lorebook.json"
        )
        content = "\n".join(entry["content"] for entry in stages["entries"].values())

        self.assertNotIn("手动仅启用阶段", content)
        self.assertNotIn("SillyTavern不会自动切换", content)
        self.assertIn("聊天局部注入", content)

    def test_package_root_contains_only_distribution_files(self):
        root_files = sorted(path.name for path in PACKAGE_DIR.iterdir() if path.is_file())

        self.assertEqual(
            [
                "README.md",
                "rosamund-complete-lorebook.json",
                "rosamund-hale.character.json",
                "rosamund-ooc-commands.md",
                "rosamund-quick-replies.json",
            ],
            root_files,
        )


if __name__ == "__main__":
    unittest.main()
