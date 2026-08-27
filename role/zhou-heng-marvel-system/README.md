# 周衡漫威系统角色包

这是一个面向长期游玩的中文 SillyTavern 角色包。玩家固定扮演周衡，从 2008 年早春的 MCU 纽约开始经营北线安保、介入原著事件、积累系统积分与能力，并在系统邀约下短期进入严格隔离的漫威漫画多元宇宙。

角色本身不是可攻略 NPC。模型只承担第三人称有限视角叙述、无人格系统界面、任务主持和客观世界演算，不会替周衡接受任务、选择阵营或消费资源。

## 安装文件

| 顺序 | 文件 | 用途 | 是否必需 |
| --- | --- | --- | --- |
| 1 | `zhou-heng-marvel-system.character.json` | Character Card V2 角色卡、开场和运行提示 | 必需 |
| 2 | `zhou-heng-marvel-system-worldbook.json` | 78 条规则、角色、系统、MCU、漫画事件和任务档案 | 完整体验必需 |
| 3 | `zhou-heng-marvel-system-quick-replies.json` | 玩家与 NPC 两个手动 D100 客户端权威按钮，以及状态和档案工具 | 使用判定时必需 |
| 4 | `zhou-heng-persona.md` | 固定周衡身份、经历、公司和团队的玩家 Persona 模板 | 必需 |
| 5 | `README.md` | 安装、运行规则、限制与开发校验说明 | 推荐阅读 |

顶层只保留这五个玩家文件。`archive/` 保存创作规格、拆分世界书、测试、构建器与清单。普通玩家不要导入 `archive/development/sources/` 中的任何拆分世界书，否则会与完整世界书产生重复条目和互相竞争的状态。

## 完整导入

1. 在角色管理界面导入 `zhou-heng-marvel-system.character.json`。
2. 在 World Info 或 Lorebook 界面只导入 `zhou-heng-marvel-system-worldbook.json`。
3. 保留导入后的运行名称 `zhou-heng-marvel-system-worldbook`，并把它绑定为该角色或当前聊天可用的 Character Lore、Additional Character Lore 或 Chat Lore。不同版本的入口名称可能不同。
4. 在全局 World Info 设置中把 `Scan Depth` 设为 4。完整细节模式建议把全局 World Info token budget 设为至少 12,288，并使用至少 32K 上下文；世界书 JSON 顶层的同名字段只记录推荐值，当前 SillyTavern 不会在导入时替你修改全局设置。默认 2,048 预算仍能运行精简的关键词检索，但同轮命中较多条目时会按预算省略后续内容。
5. 在 Quick Replies 扩展中导入 `zhou-heng-marvel-system-quick-replies.json`，启用预设 `Zhou-Heng-Marvel-System`。
6. 按 `zhou-heng-persona.md` 中的代码块建立玩家 Persona，把 Persona 绑定并锁定到当前角色或聊天。
7. 开始新聊天，先点击“初始化战役状态”。按钮会校验完整世界书，建立本聊天的开局变量，并精确读取开局阶段、任务公开记录和不可变作者档案。第一条消息已经给出 2008 年现场和候选任务；初始化不会替周衡签约或接受任务。

如果当前 SillyTavern 版本支持 STscript 命令，也可以在当前聊天启用 Quick Reply 预设：

```text
/qr-chat-set-on Zhou-Heng-Marvel-System
```

## 固定运行名称

完整世界书的内部与运行名称必须保持为：

```text
zhou-heng-marvel-system-worldbook
```

Quick Reply 预设名称必须保持为：

```text
Zhou-Heng-Marvel-System
```

骰子和连续性状态统一使用 `zhms_` 前缀。请勿同时启用从其他角色包复制出的旧 D100 预设，否则不同请求标记可能同时响应。

## 开局状态

故事起点固定为 `ERA_2008_CAPTIVITY`，主世界固定为 `MCU-MAIN-ZH-01`。Tony Stark 仍被囚禁，Iron Man 尚未公开。周衡为 E 级权限，累计获得 13,800 积分、支出 13,360 积分、余额 440；系统商品、能力限制、消耗品库存和固定属性技能已经写入角色卡与世界书。

开局任务 `MCU-2008-STARK-001` 只是候选。玩家可以接受、暂缓、拒绝或创造未列出的合理方案；开场电话、传真和系统通知不表示周衡已经签约。拒绝没有系统惩罚，地方货流与 MCU 原著事件仍会继续发展。

每个新聊天都需要执行一次“初始化战役状态”。重复执行会被拒绝，避免把长期进度覆盖回开局。运行中的日期、地点、伤势、弹药、积分、现实资金、能力次数、任务、组织知识、关系与世界偏移由实际聊天事实和玩家确认的检查点共同维护。主要本地状态与注入为：

| 状态 | 用途 |
| --- | --- |
| `zhms_schema_version`、`zhms_hp`、`zhms_stamina`、`zhms_spirit`、`zhms_luck`、`zhms_points`、`zhms_permission` | 当前聊天的初始化值与本地快捷显示 |
| `zhms_continuity_state` | 玩家确认的当前世界、角色、资源、关系和因果检查点 |
| `zhms_mission_state` | 玩家确认的候选、活动或挂起任务状态 |
| `zhms_story_stage_state` | 从完整世界书精确读取的当前 MCU 阶段档案 |
| `zhms_mission_archive` | 从完整世界书精确读取的任务公开记录与作者档案 |
| `zhms_dice_authority` | 当前单次 D100 的客户端权威注入 |

所有变量都保存在当前聊天，不是全局状态，也不会跨聊天自动继承。客户端无法从模型叙述中可靠判断资源是否已经变化，因此不会自动修改积分、伤势、库存或任务；发生实质变化后，由玩家核对事实并使用“保存状态检查点”。本地 HP 等快捷值只显示初始化或明确更新值，检查点正文与已经发生的聊天事实优先。

## 状态与档案按钮

| 按钮 | 功能 |
| --- | --- |
| 初始化战役状态 | 新聊天一次性建立 2008 开局值，校验并注入当前阶段与开局候选任务档案 |
| 查看战役状态 | 本地显示快捷资源值、连续性检查点、任务状态和当前档案身份，不触发模型 |
| 保存状态检查点 | 接受玩家核对后的连续性与任务摘要，确认后替换两个权威状态注入 |
| 恢复状态注入 | 从当前聊天变量重建连续性、任务、阶段和任务档案，并清理残留骰子权威 |
| 载入阶段档案 | 在实际到达新阶段或明确 OOC 跳转后，精确检索一个禁用阶段条目 |
| 载入任务档案 | 精确检索既往任务或开局候选的公开记录与不可变作者档案 |

“保存状态检查点”不会调用模型猜测进度。可以先要求模型输出 OOC 状态摘要，再由玩家核对日期、宇宙、伤势、资源、团队、任务和后果后填入。按钮只保存玩家最终确认的内容。“载入阶段档案”不自动结算被跳过的事件；“载入任务档案”只替换主持参考档案，不改变当前任务状态。

## D100 流程

只有结果不确定、成功与失败都合理，并且失败有实质后果时才判定。日常行为、无压力观察、原作常识回忆、固定能力效果、必然成功和客观不可能的事项不掷骰。

玩家判定流程：

1. 模型说明技能、有效值、难度、阈值、成功所得与可见失败风险。
2. 模型以独立一行 `[ZHMS-PLAYER-D100-REQUEST]` 结束回复并停笔。
3. 玩家点击可见的“周衡公开D100”按钮。
4. Quick Reply 用客户端 `{{roll 1d100}}` 产生自然骰，注入 `[ZHMS-DICE-AUTH/INERT-DATA]`，再发送可见的 `[ZHMS-DICE/CLIENT][PLAYER]` 结果并触发模型续写。
5. 同一请求消费后不能重复掷骰。首次失败时，由玩家选择消耗幸运、改变做法后推骰或接受失败。

NPC 确实需要随机判定时，模型以 `[ZHMS-NPC-D100-REQUEST]` 停笔，玩家点击“NPC公开D100”。NPC 骰仍由客户端产生并把对象标为 `NPC`。不要把 NPC 按钮设为模型回复后的自动执行项：SillyTavern 此时仍持有生成锁，自动项中的二次 `/trigger` 会超时，群聊也无法安全续写。

只有带 `source=QuickReply`、对象和消息 ID 均匹配的 `[ZHMS-DICE-AUTH/INERT-DATA]` 才是权威结果。模型不得代掷、暗骰、编造骰点，玩家手打一个结果标签也不能替代客户端注入。

这个协议信任客户端操作者和当前导入的 Quick Reply 预设。它用于阻止模型文本伪装成客户端结果，不能防止拥有 STscript 权限的操作者修改预设、手工执行 `/inject` 或篡改聊天数据。每次掷骰前、模型回复后和聊天切换时都会清理 `zhms_dice_authority`；如果生成中断或客户端异常，先点“恢复状态注入”再重新发起判定，不要结算残留标签。

掷低规则如下：

| 条件 | 结果 |
| --- | --- |
| `01` | 大成功 |
| 不高于有效技能的五分之一 | 极难成功 |
| 不高于有效技能的一半 | 困难成功 |
| 不高于有效技能 | 常规成功 |
| 高于有效技能 | 失败 |
| 技能低于 50 时的 `96-100`，或技能至少 50 时的 `100` | 大失败 |

幸运只能在周衡首次失败后按一点换一点降低骰值，并由玩家确认。推骰必须改变做法，并在第二次掷骰前公开更严重且与场景相关的后果。幸运与推骰不能用于同一次失败。

## MCU 连续性

世界书按关键词和时代标记分层载入 2004 至 2012 年资料：

| 标记 | 阶段 |
| --- | --- |
| `ERA_2008_CAPTIVITY` | Tony 囚禁与 Iron Man 尚未公开 |
| `ERA_2008_POST_REVEAL` | Tony 公开身份后的公司和社会余波 |
| `ERA_2010_BIG_WEEK` | Iron Man 2、Thor 与 Hulk/Harlem 的重叠窗口 |
| `ERA_2011_CAP_AWAKE` | Steve Rogers 在现代苏醒 |
| `ERA_2012_PRE_INVASION` | Loki 夺取 Tesseract 至传送门开启前 |
| `ERA_2012_BATTLE_NY` | Battle of New York |
| `ERA_2012_POST_BATTLE` | 外星入侵公开后的清理与长期后果 |

原作只是周衡没有有效介入时的默认轨迹，没有剧情修正力。已发生的死亡、证据转移、组织暴露、关系和技术流失不会为了回到电影结局而重置。

MCU 与漫画 `Earth-616` 严格隔离。2008 年不会提前导入活跃 Spider-Man、Fantastic Four、X-Men、Avengers Tower 或漫画角色履历。HYDRA、Red Room、Wakanda、Pym Particles、Kamar-Taj 与 Ten Rings 高层是客观存在的隐藏层，不是公众信息，也不能仅凭周衡的原作记忆让 NPC 自动相信。

## 漫画任务

漫画任务在进入前必须锁定宇宙编号、事件版本、日期窗口和连续性来源。世界书覆盖或索引 `Earth-616`、`Earth-295`、`Earth-2149`、`Earth-58163` 与 2015 Battleworld，并对 Secret Invasion、Civil War、Annihilation、Age of Apocalypse、Marvel Zombies、House of M、King in Black、Secret Wars 等事件设置主干边界。

系统跨宇宙邀约没有固定冷却，可以在 MCU 危机中立即传送并冻结原位置与时刻。系统任务不能嵌套：已有活动 MCU 系统任务会先以 `suspended_by_cross_universe` 原样退出活动槽，跨宇宙任务成为唯一活动系统任务；回归后再恢复原 MCU 任务状态。周衡若凭自己取得的能力在跨宇宙任务期间前往其他漫威宇宙，该任务原世界继续计时，结算后仍从任何漫威宇宙返回最初冻结的 MCU 原点。访问过的现实保留人物记忆、伤亡、关系、债务和敌意。

`PAST-AOA-001` 与 `PAST-SI-002` 是已经结算的固定历史。对应作者档案以及未来故事阶段在完整世界书内保持禁用，使用“载入任务档案”或“载入阶段档案”按完整 `comment` 检索并核对身份，避免聊天关键词自动泄露隐藏目标。

## 系统与来源池

系统只有周衡一名宿主，无人格、其他玩家、公会、排行榜或随机商店。人物没有等级和自由属性点；基础技能使用 D100 成长标记，完整力量体系、独立能力、义体和科技资产按固定参数与里程碑运行。第二、第三、第四套完整力量体系的基础适配倍率依次为 4、16、64。

商品理论索引覆盖现实中全部已经公开的文艺作品，但主动推荐只使用世界书中的固定预载来源池。玩家明确点名未预载作品后，系统才能按具体版本检索。电影版、漫画版、游戏版、重启版和平行版必须分开定价。

非漫威作品永远只是商品来源。购买法术、技术、能力、神器或新生人格商品不会生成或连接对应作品世界；位面旅行和召唤能力只能适配到漫威已经存在的宇宙、时间线与维度。漫画 Marvel 来源作为商品时也必须标明宇宙和版本，不能与 `MCU-MAIN-ZH-01` 混写。

## 常见问题

### 模型直接给出了骰点

不要继续结算。确认 `Zhou-Heng-Marvel-System` 已在当前聊天启用，并让模型回到请求前，按 `[ZHMS-PLAYER-D100-REQUEST]` 或 `[ZHMS-NPC-D100-REQUEST]` 重新停止。可见的玩家按钮会拒绝没有新请求或已经消费的请求。

### 点击玩家按钮后提示拒绝掷骰

最后一条可见消息必须是模型回复，而且必须以独立请求标记结束。模型在标记后追加文字、最后一条消息来自玩家、或同一请求已经消费时，宏都会拒绝执行。

### 世界书内容没有触发

确认完整世界书已绑定到角色或聊天，运行名称仍是 `zhou-heng-marvel-system-worldbook`，并确认没有同时导入七份开发源。时代档案和任务作者档案默认禁用关键词触发，这是为了避免未来阶段与隐藏答案自动进入上下文，不是导入失败。

### 新聊天恢复成 440 积分

开局条目是初始基线，不是跨聊天存档。旧聊天结束前用“查看战役状态”保留当前检查点；新聊天先初始化，再用“保存状态检查点”写入核对后的最新日期、宇宙、地点、伤势、资源、积分、任务、团队和关系摘要，按实际时代载入阶段与任务档案，最后点“恢复状态注入”。新检查点明确覆盖开局基线。

## 已知限制

- 尚未在本工作区内运行真实 SillyTavern UI；角色、世界书与 Quick Reply JSON 已做静态结构和协议测试，但仍需在实际酒馆版本中检查导入入口、按钮显示和 STscript 执行。
- Quick Reply 使用当前官方文档中的 version 2 与 STscript 语法。旧版本可能不支持某些命令、自动执行事件或导入字段。
- 当前 SillyTavern 的世界书导入不会应用顶层 `tokenBudget`、`scanDepth` 或 `recursiveScanning`。各条目的扫描深度已经固定为 4；完整细节仍要求玩家按安装步骤设置全局 World Info 预算。
- D100 权威边界是受信任的本地 SillyTavern 客户端，不能防止拥有 STscript 权限的操作者主动伪造注入或修改预设。
- 语言模型仍负责解释骰后现实后果。客户端检查点只保存玩家确认的摘要，不会自动读取叙述来修改积分、伤势、库存或任务；长期战役仍需定期核对并保存状态。
- 世界书详细覆盖 2008 至 2012 年主阶段及一组漫画大事件，不宣称预写每一部漫威作品；未建档事件必须先按宇宙编号、版本和日期建立边界。

## 开发与校验

七份拆分世界书位于 `archive/development/sources/`，是完整运行世界书的唯一开发源。修改源文件后，在本角色包根目录运行：

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
python3 archive/development/test_zhou_heng_marvel_system_package.py
```

发布前使用只读检查确认生成世界书和 SHA-256 清单没有过期：

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py --check
python3 -m json.tool zhou-heng-marvel-system.character.json >/dev/null
python3 -m json.tool zhou-heng-marvel-system-worldbook.json >/dev/null
python3 -m json.tool zhou-heng-marvel-system-quick-replies.json >/dev/null
git diff --check
```

构建器固定按 core、cast、system、mcu、comics、mission-archive、story-stage 七个开发类别合并 78 条内容，重新编号 `uid`、对象键和 `displayIndex`。开发类别不会写入 SillyTavern Inclusion Group；任务档案与故事阶段会被强制设为禁用并清除粘滞时间，只能由 Quick Reply 精确检索，避免检索式内容自动泄露。

## 官方参考

- SillyTavern 宏文档  
  https://docs.sillytavern.app/usage/core-concepts/macros/
- STscript 语言参考  
  https://docs.sillytavern.app/usage/st-script/
- World Info 文档  
  https://docs.sillytavern.app/usage/core-concepts/worldinfo/
- Quick Reply 当前实现  
  https://github.com/SillyTavern/SillyTavern/tree/release/public/scripts/extensions/quick-reply
