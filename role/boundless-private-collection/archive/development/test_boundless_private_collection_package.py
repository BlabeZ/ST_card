#!/usr/bin/env python3

import json
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CHARACTER_PATH = PACKAGE_ROOT / "boundless-private-collection.character.json"
WORLDBOOK_PATH = PACKAGE_ROOT / "boundless-private-collection-worldbook.json"
QUICK_REPLIES_PATH = (
    PACKAGE_ROOT / "boundless-private-collection-random.quick-replies.json"
)
README_PATH = PACKAGE_ROOT / "README.md"
INSTALL_ROOT = PACKAGE_ROOT / "boundless-private-collection"


def load_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


class PackageContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.character = load_json(CHARACTER_PATH)
        cls.worldbook = load_json(WORLDBOOK_PATH)
        cls.quick_replies = load_json(QUICK_REPLIES_PATH)
        cls.readme = README_PATH.read_text(encoding="utf-8")
        cls.qrs_by_label = {
            item["label"]: item for item in cls.quick_replies["qrList"]
        }

    def test_character_card_v2_and_worldbook_binding(self):
        self.assertEqual(self.character["spec"], "chara_card_v2")
        self.assertEqual(self.character["spec_version"], "2.0")
        self.assertEqual(
            self.character["data"]["extensions"]["world"],
            "boundless-private-collection-worldbook",
        )

    def test_post_history_preserves_preset_instructions(self):
        instructions = self.character["data"]["post_history_instructions"]
        self.assertTrue(instructions.startswith("{{original}}"))

    def test_openings_include_recovery_and_multiple_play_modes(self):
        greetings = self.character["data"]["alternate_greetings"]
        self.assertGreaterEqual(len(greetings), 4)
        combined = "\n".join(greetings)
        self.assertIn("恢复状态注入", combined)
        self.assertIn("现成作品", combined)
        self.assertIn("原创副本", combined)
        self.assertIn("收藏", combined)

    def test_constant_worldbook_preserves_player_agency(self):
        constant_text = "\n".join(
            entry["content"]
            for entry in self.worldbook["entries"].values()
            if entry["constant"]
        )
        self.assertIn("不得替{{user}}说话、行动、选择", constant_text)
        self.assertIn("只在需要{{user}}作出实质决定时停下", constant_text)

    def test_nested_install_copies_match_release_sources(self):
        pairs = (
            (CHARACTER_PATH, INSTALL_ROOT / CHARACTER_PATH.name),
            (WORLDBOOK_PATH, INSTALL_ROOT / WORLDBOOK_PATH.name),
            (QUICK_REPLIES_PATH, INSTALL_ROOT / QUICK_REPLIES_PATH.name),
        )
        for source, install_copy in pairs:
            self.assertEqual(source.read_bytes(), install_copy.read_bytes())

    def test_art_archives_are_not_bundled(self):
        paths = (
            PACKAGE_ROOT / "user.jpg",
            PACKAGE_ROOT / "boundless-private-collection.character.png",
            INSTALL_ROOT / "boundless-private-collection.character.png",
            PACKAGE_ROOT / "boundless-private-collection.zip",
        )
        self.assertTrue(all(not path.exists() for path in paths))

    def test_only_two_compact_worldbook_entries_are_constant(self):
        entries = self.worldbook["entries"].values()
        constants = [entry for entry in entries if entry["constant"]]
        self.assertEqual(len(constants), 2)
        self.assertLessEqual(sum(len(entry["content"]) for entry in constants), 1600)
        self.assertTrue(all(entry["ignoreBudget"] for entry in constants))

    def test_nonconstant_worldbook_entries_use_direct_triggers(self):
        entries = self.worldbook["entries"].values()
        for entry in entries:
            if not entry["constant"]:
                self.assertFalse(entry["selective"], entry["comment"])
                self.assertTrue(entry["key"], entry["comment"])
                self.assertFalse(entry["ignoreBudget"], entry["comment"])

    def test_worldbook_avoids_broad_plaintext_keys(self):
        broad_keys = {"游戏", "小说", "原作", "角色", "NPC", "关系", "帮助", "功能", "开局"}
        actual_keys = {
            key
            for entry in self.worldbook["entries"].values()
            for key in entry["key"]
        }
        self.assertFalse(broad_keys & actual_keys)

    def test_random_scope_matches_confirmed_categories(self):
        random_entries = [
            entry["content"]
            for entry in self.worldbook["entries"].values()
            if "随机" in entry["comment"] or "D100" in entry["comment"]
        ]
        text = "\n".join(random_entries)
        self.assertIn("目标状态、形态、癖好、事件和处置结果", text)
        self.assertNotIn("局部关系状态", text)
        self.assertNotIn("最接近的有效表现", text)

    def test_state_and_collection_quick_replies_exist(self):
        required_labels = {
            "初始化状态",
            "查看状态",
            "保存状态检查点",
            "恢复状态注入",
            "显示紧凑状态栏",
            "登记新收藏",
            "更新收藏档案",
            "载入收藏档案",
            "查看收藏索引",
        }
        self.assertTrue(required_labels <= self.qrs_by_label.keys())

    def test_state_variables_are_chat_local_authority(self):
        messages = "\n".join(item["message"] for item in self.qrs_by_label.values())
        required_variables = {
            "wsc_schema_version",
            "wsc_current_world",
            "wsc_current_scene",
            "wsc_continuity_state",
            "wsc_next_collection_id",
            "wsc_collection_index",
            "wsc_collection_records",
            "wsc_active_target_id",
            "wsc_active_target_record",
        }
        for variable in required_variables:
            self.assertIn(variable, messages)
        self.assertIn("id=wsc_authoritative_state", messages)
        self.assertNotIn("globalvar", messages.lower())

    def test_collection_records_use_object_keys(self):
        register = self.qrs_by_label["登记新收藏"]["message"]
        update = self.qrs_by_label["更新收藏档案"]["message"]
        load = self.qrs_by_label["载入收藏档案"]["message"]
        self.assertIn("key=wsc_collection_records index=", register)
        self.assertIn("key=wsc_collection_index index=", register)
        self.assertIn("key=wsc_collection_records index=", update)
        object_read = (
            "/getvar index={{getvar::wsc_pending_collection_id}} "
            "wsc_collection_records"
        )
        self.assertIn(object_read, update)
        self.assertIn(object_read, load)

    def test_untrusted_text_flows_enable_strict_escaping(self):
        strict_prefix = (
            "/parser-flag REPLACE_GETVAR on | "
            "/parser-flag STRICT_ESCAPING on |"
        )
        labels = {
            "保存状态检查点",
            "登记新收藏",
            "更新收藏档案",
            "执行公开D100",
            "恢复D100",
        }
        strict_labels = {
            label
            for label, item in self.qrs_by_label.items()
            if item["message"].startswith(strict_prefix)
        }
        self.assertEqual(strict_labels, labels)

    def test_random_request_awaits_the_assistant_reply(self):
        request = self.qrs_by_label["随机当前情境"]["message"]
        self.assertIn("/send ", request)
        self.assertIn(" || /trigger await=true", request)
        self.assertLess(request.index("/send "), request.index("/trigger await=true"))

    def test_d100_is_never_auto_executed_after_ai_messages(self):
        self.assertFalse(
            any(item["executeOnAi"] for item in self.quick_replies["qrList"])
        )

    def test_d100_transaction_is_staged_and_recoverable(self):
        roll = self.qrs_by_label["执行公开D100"]["message"]
        recover = self.qrs_by_label["恢复D100"]["message"]
        self.assertLess(
            roll.index("wsc_random_txn_status prepared"),
            roll.index("{{roll 1d100}}"),
        )
        self.assertLess(roll.index("wsc_random_txn_status rolled"), roll.index("/send "))
        self.assertLess(
            roll.index("/trigger await=true"),
            roll.index("wsc_random_txn_status settled"),
        )
        self.assertIn("wsc_pending_roll", recover)
        self.assertIn("wsc_last_roll", recover)
        self.assertNotIn("{{roll 1d100}}", recover)

    def test_d100_requires_a_new_visible_assistant_reply_before_settlement(self):
        validation = (
            "/pass {{lastMessageId}} | /setvar key=wsc_generation_base_id | "
            "/trigger await=true | /messages names=off hidden=off role=assistant "
            "{{getvar::wsc_generation_base_id}}-{{lastMessageId}} | "
            '/test pattern="/\\S/" {{pipe}}'
        )
        failure_cleanup = (
            "/flushvar wsc_generation_base_id | "
            "/flushinject wsc_random_authority | /run 重建WSC状态注入 | "
            "/echo severity=error"
        )
        for label in ("执行公开D100", "恢复D100"):
            message = self.qrs_by_label[label]["message"]
            settled = message.index("/setvar key=wsc_random_txn_status settled")
            self.assertIn(validation, message, label)
            self.assertIn(failure_cleanup, message, label)
            self.assertLess(message.index(validation), settled, label)
            self.assertLess(
                message.rindex("/flushvar wsc_generation_base_id"), settled, label
            )
            self.assertLess(
                message.index("/abort", message.index(validation)), settled, label
            )

    def test_d100_rebuilds_rolled_state_before_random_authority(self):
        for label in ("执行公开D100", "恢复D100"):
            message = self.qrs_by_label[label]["message"]
            rolled = message.index("/setvar key=wsc_random_txn_status rolled")
            rebuild = message.index("/run 重建WSC状态注入", rolled)
            authority = message.index("/inject id=wsc_random_authority", rebuild)
            self.assertLess(rolled, rebuild, label)
            self.assertLess(rebuild, authority, label)

    def test_restore_flushes_random_authority_before_rebuilding_state(self):
        restore = self.qrs_by_label["恢复状态注入"]["message"]
        cleanup = (
            "/flushinject wsc_random_authority | /run 重建WSC状态注入"
        )
        self.assertIn(cleanup, restore)

    def test_chat_load_restores_snapshot_without_initializing(self):
        restore_items = [
            item
            for item in self.quick_replies["qrList"]
            if item["executeOnChatChange"]
        ]
        self.assertEqual(len(restore_items), 1)
        message = restore_items[0]["message"]
        self.assertIn("wsc_schema_version", message)
        self.assertIn("恢复状态注入", message)
        self.assertNotIn("key=wsc_schema_version 2", message)

    def test_readme_documents_state_and_recovery_workflow(self):
        required_phrases = {
            "聊天变量是唯一状态真值",
            "初始化状态",
            "保存状态检查点",
            "恢复状态注入",
            "登记新收藏",
            "恢复D100",
        }
        for phrase in required_phrases:
            self.assertIn(phrase, self.readme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
