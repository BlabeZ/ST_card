# 自制角色包对比与不足分析

分析对象：`role/` 下八个自制 SillyTavern 角色包

对照材料：第三方高风险专题样本的角色卡、世界书、多开局和状态机制

分析日期：2026-08-27

## 范围与方法

本次对比检查了八张角色卡、发行世界书、Quick Reply、安装文档、开发源、构建器和现有测试。第三方目录只用于比较产品形态和实现方法。

世界书和 QR 的运行判断基于静态字段、脚本控制流及现有测试。本次没有启动 SillyTavern，因此所有涉及实际注入、生成锁和聊天切换的结论都保留 UI 复现要求。

对比维度包括以下几项。

1. 默认开场和可选入口是否能立即开始游玩。
2. 人物性格是否通过行为、语言和示例稳定表达。
3. 世界书是否按人物、地点、规则、状态和事件拆分。
4. 关键词、常驻和禁用条目是否符合运行语义。
5. 长期状态能否查看、保存、恢复和避免漂移。
6. Quick Reply、脚本和世界书是否有清楚的职责边界。
7. 源文件、生成物、发行副本和测试是否可维护。

## 自制角色卡总览

| 包 | 可玩入口总数 | 世界书条目 | QR | 产品形态 |
| --- | ---: | ---: | ---: | --- |
| Boundless Private Collection | 3 | 13 | 3 | 通用系统沙盒 |
| Forbidden Courier | 3 | 39 | 9 | 固定与动态委托沙盒 |
| Jinghai Manor | 4 | 16 | 0 | 固定女主与庄园群像 |
| Lanjin Case 0 | 1 | 31 | 0 | 固定女主与案件阶段 |
| Nive | 3 | 19 | 0 | 长期陪伴与阶段成长 |
| Rosamund Hale | 3 | 62 | 20 | 侦探主线、城市与动态案件 |
| Zheng Jin Infinite Flow | 1 | 53 | 2 | 固定女主与任务制无限流 |
| Zhou Heng Marvel System | 1 | 78 | 9 | 长期系统战役 |

“可玩入口总数”包含一个默认开场和所有非空备用开场。后文单独使用“备用开场”时不包含 `first_mes`。

八张角色卡的 `description`、`personality`、`scenario`、`first_mes`、`mes_example`、`system_prompt` 和 `post_history_instructions` 均非空。字段覆盖明显优于第三方重点目录中把大部分内容集中到 `description` 和世界书的做法。

| 角色卡字段 | 八卡合计字符数 |
| --- | ---: |
| `description` | 8710 |
| `personality` | 7047 |
| `scenario` | 6136 |
| `first_mes` | 6463 |
| `mes_example` | 11957 |
| `system_prompt` | 14603 |
| `post_history_instructions` | 3314 |
| `alternate_greetings` | 11 条 |

自制卡的字段覆盖、非空示例对话和默认开场整体更好。主要差距集中在入口数量、群像拆分、状态可视化和真实 SillyTavern 运行验证。

## 总体优势

### 角色行为较容易审计

八张卡都将身份、人格、当前场景、示例对话和系统约束分开。模型可以从 `mes_example` 直接学习语气，也能从 `scenario` 判断当前起点。

第三方重点目录只有 2 张卡填写了非空示例对话，自制卡则八张全部填写，合计约 1.2 万字符。这是自制包最应保留的优势。

### 默认开场可直接使用

自制卡的 `first_mes` 都是实际剧情。第三方重点目录有 111 张卡把默认开场替换成统一外部说明。

自制包没有这一问题。即使缺少备用开场，首次导入仍然能进入故事。

### 外部脚本风险较低

自制包主要使用普通 JSON、STscript 和 Quick Reply，没有把远程 JavaScript、超大 HTML 数据库或 `<script>` 塞进 Regex。

这种克制提高了可移植性，也减少供应链和前端兼容风险。后续增加状态面板时不应牺牲这一优势。

### 开发工程已经形成梯度

- Zhou Heng 有拆分源、确定性构建、manifest 和测试。
- Rosamund 有拆分源、确定性构建和测试，但仍有语义问题需要修复。
- Forbidden Courier 有单一构建源，但缺少只读检查和测试。
- 其余包以直接维护为主，适合较小规模内容。

## 共性不足

### 多开局覆盖不均

八张卡共有 11 个备用开场。Lanjin、Zheng 和 Zhou 只有一个默认开场。

成熟世界卡常用多个开场切换玩家身份、地点、时间点和玩法模式。自制包中的多个长线项目却把所有玩家都固定在同一入口，降低了重开价值，也让长开场承担过多说明责任。

建议每个长线包至少提供三个入口。

1. 标准主线入口。
2. 低压力关系或日常入口。
3. 跳过教程、直接进入任务或事件的入口。

### 群像仍由主卡统一代演

八个包都没有完整的多角色独立卡套件。Jinghai 已经为未来群聊预留边界，Rosamund 与 Zhou 拥有丰富配角资料，但实际仍由一张主卡代演所有 NPC。

统一代演便于控制主线，代价是不同人物共享同一角色提示，语气容易趋同。多人同场时，模型还要同时处理主角身份和主持人职责。

适合优先拆分的对象包括 Jinghai 的常驻住户、Rosamund 的高频同伴，以及 Zhou 的固定行动团队。拆分应保持可选，不能破坏单卡运行模式。

### 状态能力分化明显

Rosamund、Zhou 和 Forbidden 已经提供查看、恢复或任务锁定工具。Boundless 只有骰子和随机入口，Jinghai、Lanjin、Nive 基本依赖聊天文本或手工切换世界书。

第三方卡常见的视觉状态栏虽然工程风险高，但“状态可见、可恢复”这一目标是正确的。自制包可以用纯文本 QR 和结构化变量实现，不需要引入远程脚本或大型 HTML。

### 缺少真实 UI 冒烟测试

现有静态测试能验证 JSON、哈希、字符串契约和构建一致性，不能证明以下行为在目标 SillyTavern 版本中成立。

- QR 能否成功导入和绑定。
- `/trigger await=true` 是否符合预期。
- 生成中断和聊天切换后锁状态是否恢复。
- 世界书 Inclusion Group 是否按预期互斥。
- PNG、JSON 和 ZIP 副本是否在 UI 中表现一致。

每个带 QR 或阶段系统的包都应保留一份人工冒烟测试清单。

## 逐包分析

### Boundless Private Collection

主要文件：

- `role/boundless-private-collection/boundless-private-collection.character.json`
- `role/boundless-private-collection/boundless-private-collection-worldbook.json`
- `role/boundless-private-collection/boundless-private-collection-random.quick-replies.json`

#### 优点

- 一个默认开场和两个备用开场覆盖命令面板、世界入口和私藏域编辑。
- 角色卡标准字段完整，并提供 1172 字符示例对话。
- 13 条世界书中 5 条常驻、8 条按关键词触发，规模紧凑。
- 自动骰与手动 D100 后备按钮兼顾便利和兼容性。
- 角色卡通过 `extensions.world` 绑定固定世界书名称。

#### 不足

- 它更接近主持框架，缺少固定人物、地点和事件素材。
- 长线内容高度依赖模型即席生成，重开后难以保持世界质量。
- 收藏、改造和当前世界状态依赖聊天记忆，没有结构化检查点。
- 没有构建器或自动测试，后续规则增多时容易出现 QR 与世界书漂移。

#### 优先改进

增加一组可选人物、地点和事件模板，同时增加“查看当前世界”“保存私藏状态”“恢复状态”QR。保持 13 条核心世界书的轻量结构，不要把模板全部改成常驻。

### Forbidden Courier

主要文件：

- `role/forbidden-courier/forbidden-courier.character.json`
- `role/forbidden-courier/forbidden-courier-worldbook.json`
- `role/forbidden-courier/forbidden-courier-quick-replies.json`
- `role/forbidden-courier/build.mjs`

#### 优点

- 三个开场提供固定委托板、港口悬疑和政治异常入口。
- 默认开场一次展示四份性质不同的委托，可玩目标清楚。
- 39 条世界书中 8 条幕后档案默认禁用，避免普通关键词直接泄露。
- 动态委托使用“提议、确认、锁定”的两阶段流程。
- 9 个 QR 覆盖骰子、任务锁定、结案、清理和状态修复。
- 角色卡、世界书、QR 和 README 由同一构建源生成。

#### 不足

- 三条长期阴谋全部常驻，每轮都携带多套幕后事实。
- `build.mjs` 通过大量字符串替换修补 STscript，修改风险较高。
- 构建器无 `--check`、manifest 或自动测试。
- 构建命令会直接重写四个发行文件，无法安全地只做一致性检查。

#### 优先改进

为构建器增加 `--check` 和确定性 manifest，再为委托锁、宏定界符、结案及状态恢复增加协议测试。长期阴谋可保留简短常驻总纲，详细真相改为禁用档案并按当前委托精确载入。

### Jinghai Manor

主要文件：

- `role/jinghai-manor/gu-mizhen.character.json`
- `role/jinghai-manor/jinghai-manor-worldbook.json`
- `role/jinghai-manor/su-qibai-persona.md`

#### 优点

- 默认加三个备用开场，是八个包中入口覆盖最完整的项目。
- 训练、日常、自我改写和新增角色设计四种入口差异明确。
- `description`、`personality` 和示例对话的内容量为八卡前列。
- 顾弥真的专业、强势和玩家边界表达稳定。
- 16 条世界书规模适中，足以支撑低冲突庄园沙盒。

#### 不足

- 长期住户、关系和庄园改写依赖最新聊天事实，没有状态查看或恢复工具。
- 主卡需要代演多名住户，群像扩大后容易出现声音趋同。
- 没有 QR、测试或同步工具。
- 世界书内容较轻，长期游玩更依赖模型即兴补充人物和事件。

#### 优先改进

先增加纯文本“庄园现状”和“关系摘要”QR，再为高频住户制作可选独立角色卡。保持顾弥真主卡可以单独运行，避免把群聊变成强制依赖。

### Lanjin Case 0

主要文件：

- `role/lanjin-case-0/qin-zheng.character.json`
- `role/lanjin-case-0/lanjin-worldbook.json`
- `role/lanjin-case-0/xie-zhaoning-persona.md`

#### 优点

- 秦峥的角色表现较强，八段示例覆盖揶揄、程序正义、保护和问责。
- 默认开场同时建立生活关系、异常证据和可拒绝的调查入口。
- 31 条世界书包含城市、机构、规则、配角、能力阶段和首案阶段。
- 角色卡与世界书内容量并不薄弱。

#### 不足

- 没有备用开场，所有新聊天都从同一早餐场景开始。
- 没有 README、安装说明或世界书绑定说明。
- 能力阶段和案件阶段是两套独立轴，用户不知道如何正确切换。
- 没有 QR、状态查看、恢复或阶段诊断。
- JSON 与 PNG 同时存在，但没有同步工具。

#### 优先改进

这是发行层最需要补齐的包。首先增加 README，解释 Persona、角色卡、世界书和两套阶段轴。随后增加“查看阶段”“推进能力阶段”“推进案件阶段”“恢复阶段”QR，并提供至少两个备用开场。

### Nive

主要文件：

- `role/nive/nive.character.json`
- `role/nive/nive-shared-lorebook.json`
- `role/nive/nive-story-stages-lorebook.json`
- `role/nive/nive-dnd-lorebook.json`
- `role/nive/nive-long-rp-setup.md`

#### 优点

- 三个开场覆盖安抚、共同生活和装备测试。
- 示例对话明确限制模板化哭泣、争宠和自我贬低。
- 共同生活、隐藏阶段和 D&D 舞台由三本世界书分别负责。
- setup 文档是没有 QR 的项目中最完整的一份。
- 世界书总量轻，长期上下文成本低。

#### 不足

- 七个阶段同一时间只能启用一个，推进依赖人工编辑世界书。
- 没有状态查看、阶段切换或恢复 QR。
- 世界和 NPC 密度较低；如果希望减少模型即兴生成，可继续补充按需触发的条目。
- JSON 与 PNG 的 `system_prompt` 已有轻微差异。

#### 优先改进

增加阶段查看、切换和恢复 QR，并为 JSON 与 PNG 建立同步或校验工具。随后扩充少量按关键词触发的地点和 NPC，不增加常驻规则。

### Rosamund Hale

主要文件：

- `role/rosamund-hale/rosamund-hale.character.json`
- `role/rosamund-hale/rosamund-complete-lorebook.json`
- `role/rosamund-hale/rosamund-quick-replies.json`
- `role/rosamund-hale/archive/development/`

#### 优点

- 角色、调查、关系、固定案件、动态案件、阶段和后期沙盒形成完整玩法循环。
- 62 条世界书覆盖城区、组织、配角、案件和阶段。
- 20 个 QR 支持日志、状态、恢复、案件锁定、档案载入和连续性修复。
- 六份世界书源经确定性构建生成发行文件。
- 现有测试和 `--check` 能验证大部分静态契约。

#### 严重问题

城市、组织和配角条目被写入各自的 Inclusion Group。按 SillyTavern 当前官方文档中的 [Inclusion Group](https://docs.sillytavern.app/usage/core-concepts/worldinfo/#inclusion-group) 语义，同组条目属于互斥候选。同一轮触发多个城区资料、多个组织或多个同场 NPC 时，客户端会从组内选择条目，而不会把分类下所有命中项都当作普通条目注入。

问题来源于：

- `role/rosamund-hale/archive/development/build_complete_lorebook.py`
- `role/rosamund-hale/archive/development/test_rosamund_package.py`

当前测试把错误分组固定成了预期行为，因此“测试通过”不能证明运行语义正确。

建议在目标 SillyTavern 版本中执行以下复现。

1. 导入角色卡和完整世界书。
2. 在同一条用户消息中同时提及两个同组城区、组织或配角的触发键。
3. 打开 Prompt Itemization 或同等提示检查界面。
4. 确认实际注入项是否只保留一个组内条目。

#### 其他不足

- `rosamund-quick-replies.json` 已有 ID 20，但 `idIndex` 仍为 19。
- “诊断与修复状态”脚本超过三万字符，维护和版本兼容成本较高。
- 只有三个开场，尚未覆盖直接案件入口或主线后沙盒入口。
- 角色卡内嵌 3 条基础世界书，同时还要求外部完整世界书，需要文档持续强调职责差异。

#### 优先改进

第一优先级是移除城市、组织和配角普通条目的 Inclusion Group，并增加“普通分类条目不得进入 group”的测试。随后把 `idIndex` 修正为 20，并增加 `idIndex === max(qrList.id)` 断言。

### Zheng Jin Infinite Flow

主要文件：

- `role/zheng-jin-infinite-flow/zheng-jin.character.json`
- `role/zheng-jin-infinite-flow/zheng-jin-worldbook.json`
- `role/zheng-jin-infinite-flow/zheng-jin-d100.quick-replies.json`

#### 优点

- 五个固定副本都预写了真相、拓扑、人物、时间表、结局和学习机会。
- 53 条世界书全部有内容，资料规模充足。
- 玩家公开 D100 和 NPC 自动 D100 的权威边界清楚。
- ZIP 中发行文件与根目录版本哈希一致。

#### 不足

- 53 条世界书全部启用，30 条设置 `ignoreBudget`。
- 按世界书 `keys` 做静态命中模拟时，一个固定副本 ID 会同时匹配简报、真相、地图、人物、时间表、大量场景和结局，匹配正文合计约九千字。实际注入量还受全局预算、递归和扫描设置影响。
- 幕后答案持续交给模型，防剧透主要依赖系统提示服从。
- 1212 字默认开场一次展示大量面板和任务信息，首轮认知负担较高。
- 没有备用开场、README、Persona、状态查看、任务锁定或检查点恢复。
- JSON、PNG 和 ZIP 三份发行副本没有可重现构建器。

#### 优先改进

将公开简报保留为关键词触发，把真相、结局和作者时间表改为禁用档案，通过 QR 精确载入当前副本。增加初始化、任务载入、状态检查点和恢复 QR，再补两个不同入口。

### Zhou Heng Marvel System

主要文件：

- `role/zhou-heng-marvel-system/zhou-heng-marvel-system.character.json`
- `role/zhou-heng-marvel-system/zhou-heng-marvel-system-worldbook.json`
- `role/zhou-heng-marvel-system/zhou-heng-marvel-system-quick-replies.json`
- `role/zhou-heng-marvel-system/archive/development/`

#### 优点

- 七份开发源确定性生成 78 条完整世界书。
- MCU、漫画宇宙、任务档案和商品来源分开，减少版本混写。
- 隐藏档案默认禁用，普通条目不滥用 Inclusion Group。
- 9 个 QR 覆盖骰子、初始化、查看、检查点、恢复和档案载入。
- manifest、字段归一化和现有测试构成当前仓库的工程基准。
- 常驻条目只有 2 条，固定上下文成本较低。

#### 不足

- 只有一个 1335 字符的默认开场，入口单一且偏长。
- 长期状态仍需要玩家核对并手工保存检查点。
- NPC 骰需要手动点击，游玩流程感较强。
- 78 条世界书的信息量大，但缺少更直观的玩家可见战役摘要。

#### 优先改进

增加两个备用入口，例如低等级街头事件和直接任务入口。保持 Quick Reply 作为权威状态层，补充简短战役摘要输出，不引入远程 UI 脚本。

## 与第三方重点目录的差距

| 维度 | 第三方重点目录 | 自制角色包 | 判断 |
| --- | --- | --- | --- |
| 标准字段 | 多数集中在 `description` | 八卡字段完整 | 自制更好 |
| 默认开场 | 大量失效 | 全部可直接游玩 | 自制更好 |
| 示例对话 | 几乎没有 | 八卡全部提供 | 自制更好 |
| 备用开场 | 246 条，部分卡很多 | 合计 11 条，三包无备用 | 第三方更丰富 |
| 群像 | 大型人物索引常见 | 主卡统一代演 | 自制仍需拆分 |
| 状态 UI | 丰富但依赖脚本 | 以纯文本 QR 为主 | 自制更安全，表现较朴素 |
| 世界书预算 | 大量常驻和误触发 | 多数较克制 | 自制更好，Zheng 例外 |
| 状态恢复 | 部分卡有复杂框架 | 三个包较成熟 | 其余自制包不足 |
| 脚本安全 | 大量远程依赖 | 基本本地、可读 | 自制明显更好 |
| 发布工程 | 多为成品复制 | 部分有构建与测试 | 自制更好但不统一 |

## 改进优先级

### P0 运行正确性

1. 修复 Rosamund 普通条目的 Inclusion Group。
2. 修复 Rosamund QR `idIndex`，补对应测试。
3. 在真实 SillyTavern 中验证五套 QR 的导入、点击、中断、聊天切换和恢复。

### P1 可玩性和上下文

1. 重构 Zheng 的幕后档案载入和 `ignoreBudget`。
2. 为 Lanjin 增加 README、阶段 QR 和备用开场。
3. 为 Zheng 与 Zhou 增加至少两个真正不同的开场。
4. 为 Jinghai 与 Nive 增加纯文本状态查看和恢复能力。

### P2 工程维护

1. 为 Forbidden 构建器增加 `--check`、manifest 和自动测试。
2. 为 Nive、Lanjin 与 Zheng 的 JSON、PNG、ZIP 建立一致性检查。
3. 为所有带阶段和 QR 的包增加人工 UI 冒烟测试清单。

### P3 内容扩展

1. 为 Boundless 增加可选人物、地点和事件模板。
2. 将 Jinghai、Rosamund 或 Zhou 的高频配角拆成可选独立角色卡。
3. 为缺少地点和事件条目的长期包增加按关键词触发的场景材料，降低对模型即兴推进的依赖。

## 后续创作基线

新角色包建议继续采用自制包的标准字段、示例对话、本地脚本和可测试构建，同时吸收第三方卡的多入口和模块化方法。

推荐的职责边界如下。

- 角色卡保存身份、人格、当前关系、场景、开场和示例对话。
- 世界书保存人物、地点、事实、事件和少量状态协议。
- Quick Reply 保存骰子、初始化、检查点、恢复和精确档案载入。
- Regex 只做纯文本或安全 HTML 展示，不保存权威状态。
- 构建器只从明确开发源生成发行文件，并提供只读 `--check`。
- 测试同时检查 JSON 结构、运行语义、ID、分组和副本一致性。

第三方重点目录的完整结构分析见 [`cards-high-risk-analysis.md`](cards-high-risk-analysis.md)。
