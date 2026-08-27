import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import build_zhou_heng_marvel_system_package as builder


EXPECTED_ENTRY_FIELDS = {
    "uid",
    "key",
    "keysecondary",
    "comment",
    "content",
    "constant",
    "vectorized",
    "selective",
    "selectiveLogic",
    "addMemo",
    "order",
    "position",
    "disable",
    "ignoreBudget",
    "excludeRecursion",
    "preventRecursion",
    "matchPersonaDescription",
    "matchCharacterDescription",
    "matchCharacterPersonality",
    "matchCharacterDepthPrompt",
    "matchScenario",
    "matchCreatorNotes",
    "delayUntilRecursion",
    "probability",
    "useProbability",
    "depth",
    "outletName",
    "group",
    "groupOverride",
    "groupWeight",
    "scanDepth",
    "caseSensitive",
    "matchWholeWords",
    "useGroupScoring",
    "automationId",
    "role",
    "sticky",
    "cooldown",
    "delay",
    "triggers",
    "displayIndex",
    "characterFilter",
}


def load_json(relative_path):
    with (PACKAGE_DIR / relative_path).open(encoding="utf-8") as source:
        return json.load(source)


def source_entries(filename):
    return load_json(f"archive/development/sources/{filename}")["entries"].values()


def source_text(filename):
    return "\n".join(entry["content"] for entry in source_entries(filename))


class BuildContractTests(unittest.TestCase):
    def test_source_order_and_counts_are_fixed(self):
        self.assertEqual(
            (
                ("zhou-heng-marvel-system-core-lorebook.json", 8, "core"),
                ("zhou-heng-marvel-system-cast-lorebook.json", 10, "cast"),
                ("zhou-heng-marvel-system-system-lorebook.json", 18, "system"),
                ("zhou-heng-marvel-system-mcu-lorebook.json", 20, "mcu"),
                ("zhou-heng-marvel-system-comics-lorebook.json", 10, "comics"),
                ("zhou-heng-marvel-system-missions-lorebook.json", 6, "mission-archive"),
                ("zhou-heng-marvel-system-stages-lorebook.json", 6, "story-stage"),
            ),
            builder.SOURCES,
        )

    def test_build_normalizes_and_merges_every_entry(self):
        lorebook = builder.build_complete_lorebook(PACKAGE_DIR)
        entries = lorebook["entries"]

        self.assertEqual(78, len(entries))
        self.assertEqual([str(index) for index in range(78)], list(entries))
        self.assertEqual(list(range(78)), [entry["uid"] for entry in entries.values()])
        self.assertEqual(
            list(range(78)),
            [entry["displayIndex"] for entry in entries.values()],
        )
        comments = [entry["comment"] for entry in entries.values()]
        self.assertEqual(len(comments), len(set(comments)))
        for entry in entries.values():
            self.assertEqual(EXPECTED_ENTRY_FIELDS, set(entry))

    def test_build_does_not_turn_source_categories_into_inclusion_groups(self):
        entries = list(builder.build_complete_lorebook(PACKAGE_DIR)["entries"].values())

        self.assertTrue(all(entry["group"] == "" for entry in entries))

    def test_retrieval_only_entries_are_forced_disabled(self):
        entries = builder.build_complete_lorebook(PACKAGE_DIR)["entries"].values()
        hidden = list(entries)[66:78]

        self.assertEqual(12, len(hidden))
        self.assertTrue(all(entry["disable"] for entry in hidden))
        self.assertTrue(all(entry["sticky"] is None for entry in hidden))

    def test_distribution_metadata_and_entry_scan_depth_are_stable(self):
        lorebook = builder.build_complete_lorebook(PACKAGE_DIR)

        self.assertEqual("zhou-heng-marvel-system-worldbook", lorebook["name"])
        self.assertEqual(4, lorebook["scanDepth"])
        self.assertEqual(12288, lorebook["tokenBudget"])
        self.assertFalse(lorebook["recursiveScanning"])
        self.assertEqual(
            "zhou-heng-marvel-system-worldbook",
            lorebook["extensions"]["runtimeName"],
        )
        self.assertEqual("1.0.0", lorebook["extensions"]["packageVersion"])
        self.assertTrue(
            all(entry["scanDepth"] == 4 for entry in lorebook["entries"].values())
        )

    def test_always_on_entries_fit_below_the_default_world_info_budget(self):
        entries = builder.build_complete_lorebook(PACKAGE_DIR)["entries"].values()
        always_on = [entry for entry in entries if entry["constant"] and not entry["disable"]]

        self.assertEqual(
            {"runtime contract", "MCU 主连续性边界与排除项"},
            {entry["comment"] for entry in always_on},
        )
        fallback_token_estimate = sum(
            len(entry["content"].encode("utf-8")) / 4 for entry in always_on
        )
        self.assertLess(fallback_token_estimate, 1200)


class CharacterAndPersonaContractTests(unittest.TestCase):
    def test_character_card_v2_has_the_repository_standard_shape(self):
        card = load_json("zhou-heng-marvel-system.character.json")
        data = card["data"]

        self.assertEqual("chara_card_v2", card["spec"])
        self.assertEqual("2.0", card["spec_version"])
        self.assertEqual(
            {
                "name",
                "description",
                "personality",
                "scenario",
                "first_mes",
                "mes_example",
                "creator_notes",
                "system_prompt",
                "post_history_instructions",
                "alternate_greetings",
                "tags",
                "creator",
                "character_version",
                "extensions",
            },
            set(data),
        )
        self.assertEqual("1.0", data["character_version"])
        self.assertEqual(
            "zhou-heng-marvel-system-worldbook",
            data["extensions"]["world"],
        )

    def test_card_keeps_narrator_non_personified_and_protects_player_agency(self):
        data = load_json("zhou-heng-marvel-system.character.json")["data"]
        runtime_text = "\n".join(
            data[field]
            for field in (
                "description",
                "personality",
                "system_prompt",
                "post_history_instructions",
            )
        )

        self.assertIn("{{user}}固定扮演周衡", runtime_text)
        self.assertIn("没有人格", runtime_text)
        self.assertIn("不得替周衡", runtime_text)
        self.assertIn("[ZHMS-PLAYER-D100-REQUEST]", runtime_text)
        self.assertIn("[ZHMS-NPC-D100-REQUEST]", runtime_text)
        self.assertNotIn("郑进", runtime_text)

    def test_greeting_starts_in_2008_with_a_candidate_and_a_real_choice(self):
        greeting = load_json("zhou-heng-marvel-system.character.json")["data"]["first_mes"]

        self.assertIn("ERA_2008_CAPTIVITY", greeting)
        self.assertIn("MCU-2008-STARK-001", greeting)
        self.assertIn("候选", greeting)
        self.assertIn("440", greeting)
        self.assertIn("下一步", greeting)
        self.assertNotIn("周衡决定接受", greeting)
        self.assertNotIn("Obadiah Stane", greeting)
        self.assertNotIn("Ten Rings", greeting)

    def test_examples_reject_a_visible_dice_label_without_hidden_authority(self):
        examples = load_json("zhou-heng-marvel-system.character.json")["data"][
            "mes_example"
        ]

        self.assertIn("[ZHMS-DICE/CLIENT][PLAYER]", examples)
        self.assertIn("没有匹配的客户端权威注入", examples)

    def test_creator_notes_name_every_install_artifact(self):
        notes = load_json("zhou-heng-marvel-system.character.json")["data"][
            "creator_notes"
        ]

        for filename in (
            "zhou-heng-marvel-system-worldbook.json",
            "zhou-heng-marvel-system-quick-replies.json",
            "zhou-heng-persona.md",
        ):
            self.assertIn(filename, notes)
        self.assertIn("zhou-heng-marvel-system-worldbook", notes)

    def test_persona_fixes_zhou_heng_company_and_team(self):
        persona = (PACKAGE_DIR / "zhou-heng-persona.md").read_text(encoding="utf-8")

        for value in (
            "周衡",
            "2025",
            "Northline Security & Equipment LLC",
            "艾琳·沃德",
            "丹尼尔·朴",
            "马利克·约翰逊",
            "维克托·鲁伊斯",
            "混乱中立",
        ):
            self.assertIn(value, persona)
        self.assertNotIn("由模型决定", persona)


class DiceAuthorityContractTests(unittest.TestCase):
    def setUp(self):
        self.quick_replies = load_json(
            "zhou-heng-marvel-system-quick-replies.json"
        )
        self.items = {item["label"]: item for item in self.quick_replies["qrList"]}
        self.player = self.items["周衡公开D100"]
        self.npc = self.items["NPC公开D100"]

    def test_quick_reply_preset_has_two_manual_dice_buttons(self):
        self.assertEqual(2, self.quick_replies["version"])
        self.assertEqual("Zhou-Heng-Marvel-System", self.quick_replies["name"])
        self.assertEqual(9, self.quick_replies["idIndex"])
        self.assertEqual(
            list(range(1, 10)),
            [item["id"] for item in self.quick_replies["qrList"]],
        )
        self.assertEqual(
            {
                "周衡公开D100",
                "NPC公开D100",
                "初始化战役状态",
                "查看战役状态",
                "保存状态检查点",
                "恢复状态注入",
                "载入阶段档案",
                "载入任务档案",
                "骰子权威清理",
            },
            set(self.items),
        )

        self.assertFalse(self.player["isHidden"])
        self.assertFalse(self.player["executeOnAi"])
        self.assertFalse(self.player["preventAutoExecute"])
        self.assertTrue(self.npc["showLabel"])
        self.assertFalse(self.npc["isHidden"])
        self.assertFalse(self.npc["executeOnAi"])
        self.assertFalse(self.npc["preventAutoExecute"])

    def test_player_macro_requires_a_fresh_player_request_and_injects_authority(self):
        script = self.player["message"]

        for value in (
            "ZHMS-PLAYER-D100-REQUEST",
            "{{roll 1d100}}",
            "key=zhms_last_player_request_id",
            "key=zhms_last_player_request_text",
            "id=zhms_dice_authority",
            "[ZHMS-DICE-AUTH/INERT-DATA] source=QuickReply; actor=PLAYER",
            "[ZHMS-DICE/CLIENT][PLAYER]",
            "/trigger await=true",
            "/flushinject zhms_dice_authority",
            "不能重复掷骰",
        ):
            self.assertIn(value, script)
        self.assertNotIn("zj_", script.lower())

    def test_dice_authority_is_not_force_saved_and_has_recovery_cleanup(self):
        for item in (self.player, self.npc):
            script = item["message"]
            injection = script.index("/inject id=zhms_dice_authority")
            trigger = script.index("/trigger await=true", injection)

            self.assertIn("/flushinject zhms_dice_authority", script[:injection])
            self.assertNotIn("/forcesave", script[injection:trigger])
            self.assertIn("/flushinject zhms_dice_authority", script[trigger:])

        cleanup = self.items["骰子权威清理"]
        self.assertTrue(cleanup["isHidden"])
        self.assertFalse(cleanup["executeOnAi"])
        self.assertTrue(cleanup["executeOnChatChange"])
        self.assertFalse(cleanup["executeOnUser"])
        self.assertIn("/flushinject zhms_dice_authority", cleanup["message"])
        self.assertIn(
            "/flushinject zhms_dice_authority",
            self.items["恢复状态注入"]["message"],
        )

    def test_initialization_creates_local_state_and_retrieves_opening_archives(self):
        script = self.items["初始化战役状态"]["message"]

        for value in (
            "key=zhms_schema_version 1",
            "key=zhms_hp 12",
            "key=zhms_stamina 15",
            "key=zhms_spirit 16",
            "key=zhms_luck 60",
            "key=zhms_points 440",
            "key=zhms_permission E",
            "key=zhms_continuity_state",
            "key=zhms_mission_state",
            "file=zhou-heng-marvel-system-worldbook",
            "ZHMS 阶段 2008 Tony囚禁期",
            "ZHMS 任务 MCU-2008-STARK-001 公开候选与发布规则",
            "ZHMS 任务 MCU-2008-STARK-001 不可变作者档案",
            "/getentryfield",
            "id=zhms_continuity_state",
            "id=zhms_mission_state",
            "id=zhms_story_stage_state",
            "id=zhms_mission_archive",
            "/forcesave",
            "候选任务=MCU-2008-STARK-001；活动槽=空；状态=candidate",
        ):
            self.assertIn(value, script)
        self.assertNotIn("活动槽=MCU-2008-STARK-001", script)

    def test_status_checkpoint_and_restore_are_explicit_and_recoverable(self):
        view = self.items["查看战役状态"]["message"]
        checkpoint = self.items["保存状态检查点"]["message"]
        restore = self.items["恢复状态注入"]["message"]

        for value in (
            "zhms_hp",
            "zhms_stamina",
            "zhms_spirit",
            "zhms_luck",
            "zhms_points",
            "zhms_permission",
            "zhms_continuity_state",
            "zhms_mission_state",
        ):
            self.assertIn(value, view)
        self.assertIn("/input", checkpoint)
        self.assertIn("key=zhms_continuity_state", checkpoint)
        self.assertIn("key=zhms_mission_state", checkpoint)
        self.assertIn("id=zhms_continuity_state", checkpoint)
        self.assertIn("id=zhms_mission_state", checkpoint)
        self.assertIn("/forcesave", checkpoint)
        for value in (
            "/getvar zhms_continuity_state",
            "/getvar zhms_mission_state",
            "id=zhms_continuity_state",
            "id=zhms_mission_state",
            "id=zhms_story_stage_state",
            "id=zhms_mission_archive",
            "/forcesave",
        ):
            self.assertIn(value, restore)

    def test_stage_and_mission_archives_have_exact_identity_checked_retrieval(self):
        stage = self.items["载入阶段档案"]["message"]
        mission = self.items["载入任务档案"]["message"]

        for value in (
            "ZHMS 阶段 2008 Tony囚禁期",
            "ZHMS 阶段 2008 钢铁侠公开后",
            "ZHMS 阶段 2010 Fury Big Week",
            "ZHMS 阶段 2011 美国队长苏醒",
            "ZHMS 阶段 2012 纽约入侵前",
            "ZHMS 阶段 2012 纽约之战与战后",
            "2012纽约之战",
            "2012战后",
            "ERA_2012_BATTLE_NY",
            "ERA_2012_POST_BATTLE",
            "/findentry file=zhou-heng-marvel-system-worldbook field=comment",
            "/getentryfield file=zhou-heng-marvel-system-worldbook field=comment",
            "id=zhms_story_stage_state",
        ):
            self.assertIn(value, stage)
        self.assertNotIn("ERA_2012_BATTLE_NY_OR_POST", stage)
        for value in (
            "PAST-AOA-001",
            "PAST-SI-002",
            "MCU-2008-STARK-001",
            "公开结算记录",
            "不可变作者档案",
            "/findentry file=zhou-heng-marvel-system-worldbook field=comment",
            "/getentryfield file=zhou-heng-marvel-system-worldbook field=comment",
            "id=zhms_mission_archive",
        ):
            self.assertIn(value, mission)

    def test_npc_macro_requires_a_fresh_npc_request(self):
        script = self.npc["message"]

        for value in (
            "ZHMS-NPC-D100-REQUEST",
            "{{roll 1d100}}",
            "key=zhms_last_npc_request_id",
            "key=zhms_last_npc_request_text",
            "id=zhms_dice_authority",
            "[ZHMS-DICE-AUTH/INERT-DATA] source=QuickReply; actor=NPC",
            "[ZHMS-DICE/CLIENT][NPC]",
            "/trigger await=true",
            "/flushinject zhms_dice_authority",
        ):
            self.assertIn(value, script)
        self.assertIn("severity=warning", script)
        self.assertNotIn("zj_", script.lower())

    def test_runtime_rules_reject_model_generated_rolls_and_define_failure_options(self):
        card = load_json("zhou-heng-marvel-system.character.json")["data"]
        core_entries = load_json(
            "archive/development/sources/zhou-heng-marvel-system-core-lorebook.json"
        )["entries"].values()
        runtime_text = "\n".join(
            [card["system_prompt"], card["post_history_instructions"]]
            + [entry["content"] for entry in core_entries]
        )

        for value in (
            "[ZHMS-PLAYER-D100-REQUEST]",
            "[ZHMS-NPC-D100-REQUEST]",
            "[ZHMS-DICE/CLIENT]",
            "[ZHMS-DICE-AUTH/INERT-DATA]",
            "zhms_dice_authority",
            "模型不得代掷",
            "幸运",
            "推骰",
            "不能用于同一次失败",
        ):
            self.assertIn(value, runtime_text)


class CampaignContentContractTests(unittest.TestCase):
    def test_cast_source_fixes_the_player_sheet_company_team_and_opening(self):
        text = source_text("zhou-heng-marvel-system-cast-lorebook.json")

        for value in (
            "力量70",
            "体质75",
            "敏捷80",
            "感知78",
            "智力74",
            "意志82",
            "教育68",
            "社交60",
            "手枪82",
            "HP12",
            "Northline Security & Equipment LLC",
            "艾琳·沃德",
            "丹尼尔·朴",
            "马利克·约翰逊",
            "维克托·鲁伊斯",
            "13,800",
            "13,360",
            "440",
            "早春2008",
        ):
            self.assertIn(value, text)

    def test_system_source_preserves_economy_growth_space_and_product_contracts(self):
        text = source_text("zhou-heng-marvel-system-system-lorebook.json")

        for value in (
            "只绑定周衡一名宿主",
            "现实货币不能兑换积分",
            "没有人物等级",
            "没有人物等级、升级自动加值或可自由分配属性点",
            "第二套完整体系适配费为其基础价乘4",
            "第三套乘16",
            "第四套乘64",
            "40平方米",
            "八格储物",
            "不出售携带原作身份",
            "绝对支配",
            "13,800-13,360=440",
        ):
            self.assertIn(value, text)

    def test_preloaded_source_pool_is_search_only_and_does_not_create_worlds(self):
        text = source_text("zhou-heng-marvel-system-system-lorebook.json")

        for value in (
            "全部已经公开的文艺作品",
            "《西游记》",
            "《龙珠》",
            "《龙与地下城》",
            "《战锤40K》",
            "DC漫画",
            "《哈利·波特》",
            "《星球大战》",
            "《奥特曼》",
            "不创建任何非漫威来源世界",
        ):
            self.assertIn(value, text)

    def test_mcu_source_has_every_era_and_keeps_public_knowledge_separated(self):
        text = source_text("zhou-heng-marvel-system-mcu-lorebook.json")

        for value in (
            "MCU-MAIN-ZH-01",
            "ERA_2008_CAPTIVITY",
            "ERA_2008_POST_REVEAL",
            "ERA_2010_BIG_WEEK",
            "ERA_2011_CAP_AWAKE",
            "ERA_2012_PRE_INVASION",
            "ERA_2012_BATTLE_NY",
            "ERA_2012_POST_BATTLE",
            "Tony Stark 在阿富汗展示",
            "Stark Expo",
            "Harlem",
            "New Mexico",
            "Times Square",
            "Project P.E.G.A.S.U.S.",
            "Chitauri",
            "Department of Damage Control",
            "不是 2008 年公众信息",
            "HYDRA",
            "Red Room",
            "Hank Pym",
            "Wakanda",
            "Tony 公开身份约两年后",
            "zhms_continuity_state",
        ):
            self.assertIn(value, text)
        self.assertNotIn("Tony 公开身份约六个月后", text)
        self.assertNotIn("`zhms_continuity`", text)

    def test_mcu_source_explicitly_blocks_wrong_continuities_and_premature_heroes(self):
        text = source_text("zhou-heng-marvel-system-mcu-lorebook.json")

        for value in (
            "漫画 Earth-616",
            "2008 年不得出现 Oscorp",
            "Peter Parker 此时尚非活跃英雄",
            "神奇四侠",
            "X 战警",
            "Avengers 尚未成立",
            "AOS-CONTINUITY-UNRESOLVED",
        ):
            self.assertIn(value, text)

    def test_comics_source_isolates_realities_and_covers_locked_event_indexes(self):
        text = source_text("zhou-heng-marvel-system-comics-lorebook.json")

        for value in (
            "Earth-616",
            "Earth-295",
            "Earth-2149",
            "Earth-58163",
            "Battleworld",
            "[强制重构警告]",
            "Secret Invasion",
            "Civil War",
            "Annihilation",
            "King in Black",
            "Dark Reign",
            "Siege",
            "World War Hulk",
            "Absolute Carnage",
            "War of the Realms",
            "Infinity",
            "Empyre",
            "Spider-Verse",
        ):
            self.assertIn(value, text)
        self.assertIn("绝不与漫画`Earth-616`合并", text)

    def test_mission_archives_lock_history_opening_and_publication_state_machine(self):
        text = source_text("zhou-heng-marvel-system-missions-lorebook.json")

        for value in (
            "PAST-AOA-001",
            "31人活着抵达",
            "评分87/100",
            "2,100积分",
            "PAST-SI-002",
            "16:52交付",
            "评分89/100，S",
            "2,800积分",
            "MCU-2008-STARK-001",
            "system-only publication",
            "接受/accepted",
            "暂缓/deferred",
            "拒绝/rejected",
            "自动激活/auto-activated",
            "no dynamic difficulty",
            "no cross-task cooldown",
            "immediate frozen-origin transfer",
            "no nested system tasks",
            "suspended_by_cross_universe",
            "return from anywhere",
            "world persistence",
            "隐藏目标只给额外奖励",
        ):
            self.assertIn(value, text)

        public_opening = list(
            source_entries("zhou-heng-marvel-system-missions-lorebook.json")
        )[4]["content"]
        self.assertNotIn("Obadiah Stane", public_opening)
        self.assertNotIn("Ten Rings", public_opening)

    def test_cross_universe_task_handoff_suspends_instead_of_nesting(self):
        core = source_text("zhou-heng-marvel-system-core-lorebook.json")
        stages = source_text("zhou-heng-marvel-system-stages-lorebook.json")

        for value in (
            "suspended_by_cross_universe",
            "跨宇宙任务成为唯一活动系统任务",
            "恢复到接受邀约前的状态",
            "跨宇宙任务期间",
        ):
            self.assertIn(value, core)
        self.assertIn("suspended_by_cross_universe", stages)

    def test_every_hidden_archive_and_stage_requires_explicit_retrieval(self):
        built_entries = list(
            builder.build_complete_lorebook(PACKAGE_DIR)["entries"].values()
        )
        missions = built_entries[66:72]
        stages = built_entries[72:78]

        self.assertEqual(6, len(missions))
        self.assertEqual(6, len(stages))
        self.assertTrue(all(entry["disable"] for entry in missions))
        self.assertTrue(all(entry["disable"] for entry in stages))
        self.assertTrue(all(entry["group"] == "" for entry in missions + stages))


class DistributionContractTests(unittest.TestCase):
    def test_package_root_exposes_only_five_player_files(self):
        root_files = {path.name for path in PACKAGE_DIR.iterdir() if path.is_file()}
        root_directories = {path.name for path in PACKAGE_DIR.iterdir() if path.is_dir()}

        self.assertEqual(
            {
                "README.md",
                "zhou-heng-marvel-system.character.json",
                "zhou-heng-marvel-system-worldbook.json",
                "zhou-heng-marvel-system-quick-replies.json",
                "zhou-heng-persona.md",
            },
            root_files,
        )
        self.assertEqual({"archive"}, root_directories)

    def test_readme_documents_order_names_binding_and_source_warning(self):
        readme = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8")
        ordered_steps = (
            "zhou-heng-marvel-system.character.json",
            "zhou-heng-marvel-system-worldbook.json",
            "zhou-heng-marvel-system-quick-replies.json",
            "zhou-heng-persona.md",
        )

        positions = [readme.index(value) for value in ordered_steps]
        self.assertEqual(sorted(positions), positions)
        for value in (
            "zhou-heng-marvel-system-worldbook",
            "Zhou-Heng-Marvel-System",
            "Character Lore",
            "Chat Lore",
            "/qr-chat-set-on Zhou-Heng-Marvel-System",
            "不要导入",
            "archive/development/sources/",
            "Persona",
            "锁定",
            "初始化战役状态",
            "查看战役状态",
            "保存状态检查点",
            "恢复状态注入",
            "载入阶段档案",
            "载入任务档案",
            "NPC公开D100",
            "全局 World Info token budget",
            "12,288",
            "32K",
        ):
            self.assertIn(value, readme)

    def test_readme_documents_d100_state_limits_and_exact_validation_commands(self):
        readme = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8")

        for value in (
            "[ZHMS-PLAYER-D100-REQUEST]",
            "[ZHMS-NPC-D100-REQUEST]",
            "[ZHMS-DICE-AUTH/INERT-DATA]",
            "zhms_continuity_state",
            "zhms_mission_state",
            "zhms_dice_authority",
            "真实 SillyTavern UI",
            "python3 archive/development/build_zhou_heng_marvel_system_package.py",
            "python3 archive/development/test_zhou_heng_marvel_system_package.py",
            "python3 archive/development/build_zhou_heng_marvel_system_package.py --check",
            "https://docs.sillytavern.app/usage/core-concepts/macros/",
            "https://docs.sillytavern.app/usage/st-script/",
            "https://docs.sillytavern.app/usage/core-concepts/worldinfo/",
            "https://github.com/SillyTavern/SillyTavern/tree/release/public/scripts/extensions/quick-reply",
            "信任客户端操作者",
            "不能防止拥有 STscript 权限的操作者",
        ):
            self.assertIn(value, readme)

    def test_archive_readme_marks_every_development_asset_non_installable(self):
        readme = (PACKAGE_DIR / "archive/README.md").read_text(encoding="utf-8")

        for value in (
            "普通玩家无需导入",
            "creator/zhou-heng-marvel-system.md",
            "development/sources/",
            "build_zhou_heng_marvel_system_package.py",
            "test_zhou_heng_marvel_system_package.py",
            "zhou-heng-marvel-system-package-manifest.json",
        ):
            self.assertIn(value, readme)

    def test_generated_worldbook_and_manifest_are_current(self):
        self.assertEqual(
            builder.build_complete_lorebook(PACKAGE_DIR),
            load_json("zhou-heng-marvel-system-worldbook.json"),
        )
        self.assertEqual(
            builder.build_manifest(PACKAGE_DIR),
            load_json(
                "archive/development/zhou-heng-marvel-system-package-manifest.json"
            ),
        )


if __name__ == "__main__":
    unittest.main()
