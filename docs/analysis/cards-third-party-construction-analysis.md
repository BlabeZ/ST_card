# 第三方角色卡构建方法综合分析

分析对象为 `sillytavernassets-main/cards/`。

分析日期为 2026-08-28。

## 分析范围

仓库根目录没有 `cards/`，实际素材目录位于 `sillytavernassets-main/cards/`。本次将 3506 个文件作为总体样本，结合全量结构统计和代表卡深读，归纳角色卡的构建方式、设计思路、运行机制、配套预设、文字写法、引导方式与常见语法。

| 项目 | 数量 |
| --- | --- |
| 文件 | 3506 |
| PNG | 3273 |
| 带角色卡元数据的 PNG | 3269 |
| 独立 JSON | 129 |
| 独立 TXT | 62 |
| 文件名以 `.txt）` 结尾的说明文件 | 2 |
| 顶层分类 | 32 |

3269 张可解析 PNG 按优先读取 `ccv3`、缺失时读取 `chara` 的口径，可分为 1954 张声明 `chara_card_v3` 的卡、1241 张声明 `chara_card_v2` 的卡和 74 张未声明版本的旧卡。另有 4 张 PNG 只是普通图片。这里统计的是载荷中的版本标签，不是逐字段规范合规认证。

分析过程中只读取 PNG 文本块、JSON、TXT 和现有说明，没有执行第三方 JavaScript、STscript、HTML、安装器或远程资源。目录内包含成人、胁迫和未成年人相关素材。本文不复述相关文本，只提取人物模块化、叙事结构、检索、状态、交互和发行方面的通用经验。

另有一个影响全库判断的采集问题。可解析卡片的 `first_mes` 普遍被相同推广内容替换，部分非角色卡 JSON 也混入了同一字段。因此，本文对开场的判断主要依据仍然保留的 `alternate_greetings`。这个问题属于当前镜像的再包装痕迹，不能反推原作者都采用了相同开场。

## 总体判断

成熟角色卡的价值来自职责分层。表现较好的作品通常同时解决六件事。

| 层 | 解决的问题 | 常见载体 |
| --- | --- | --- |
| 人物层 | 角色是谁，怎样判断，怎样说话 | `description`、`personality`、`mes_example` |
| 场景层 | 当前发生什么，用户从哪里进入 | `scenario`、`first_mes`、`alternate_greetings` |
| 知识层 | 哪些资料需要常驻，哪些按需加载 | `character_book`、外挂世界书 |
| 协议层 | 模型每轮应输出哪些可识别区块 | XML 风格标签、YAML、JSON、轻量 DSL |
| 状态层 | 数值、事件和长期事实由谁保存 | 聊天变量、dataTable、MVU、动态世界书 |
| 表现层 | 怎样把机器数据转成玩家可读界面 | Regex、HTML/CSS、TavernHelper、Quick Reply |

单角色卡只需前三层也能稳定运行。大型世界卡和 RPG 卡通常加入协议层与状态层。少数复杂卡再叠加前端界面，已经接近安装在聊天客户端里的小型应用。

这套分层带来三个明显收益。

1. 角色事实、运行规则和显示代码可以分别修改，降低改一处坏三处的概率。
2. 世界资料能够按场景装载，长线聊天不必每轮携带整本设定。
3. 模型生成、状态保存和界面显示形成反馈回路，玩家能看见选择造成的持续后果。

## 三类产品形态

### 核心字段卡

这类卡主要依靠标准字段工作，扩展依赖很少。代表样本包括 `英文卡/main_Ada_tavern.png`、`英文卡/main_Blanchett_tavern.png` 和 `单人/圣女猫猫今天也在助人为乐.png`。

它们的优点是结构短、导入范围广、故障面小。角色身份放在 `description`，行为摘要放在 `personality`，当前关系和场景放在 `scenario`，语气由 `mes_example` 示范。即使客户端忽略所有扩展，角色仍有完整的文本人格。

这种形态适合固定人物、陪伴、轻冒险和短中篇剧情。最值得迁移的是人物资料与示例对话的配合。规则说明可以概括人物，示例对话负责证明人物实际怎样回应。

### 世界书驱动卡

这类卡把世界、人物、地点、组织、事件和规则拆进 `character_book`。代表样本包括 `正常向/传统文化 纸嫁衣.png`、`世界卡/蒸汽幻想曲.png`、`世界卡/托瑞尔之书：被遗忘的国度v0.1.png` 和 `同人/小说/庆余年.png`。

它们的优势是检索。基础法则可以常驻，人物与地点使用姓名和别名触发，专门规则只在有关场景进入提示。卡片因此能承载远大于单个 `description` 的资料量。

表现较好的世界书还会区分公开资料与幕后资料。玩家能查到的事实使用关键词条目，真相和作者时间线保持禁用，再由专门工具精确载入。推理剧情因此可以维持固定真相，同时允许不同调查路径。

### 嵌入式应用卡

这类卡把模型当作内容生成器，把 SillyTavern 当作宿主。代表样本包括 `世界卡/无限轮回.png`、`修仙/归墟/归墟6.9.png`、`修仙/凡人修仙传/V8.7.png`、`校园/谈一场甜甜的恋爱吗~ 通用手机卡.png` 和 `世界卡/搭载dataTable的万界IP系统/搭载dataTable的万界IP系统.png`。

它们通常按以下流程运行。

```text
角色卡与预设定义输出协议
→ 模型生成正文和机器区块
→ Regex 找到并隐藏机器区块
→ MVU、dataTable 或脚本应用状态更新
→ HTML/CSS 将状态渲染为界面
→ 新状态在下一轮重新注入模型
```

这类卡的产品思路很成熟。正文、状态、摘要、选项和界面拥有各自的数据通道。用户可以查看状态、编辑摘要、保存档案、恢复进度，部分卡还能生成新人物并写回世界书。

完整能力依赖 SillyTavern 版本、Regex、Quick Reply、TavernHelper、MVU 或特定表格扩展。迁移时应先保留文本可玩性，再把 UI 当作增强层。

## 破限、越狱与相近提示

### 统计口径

当前镜像不能直接按关键词计数。全部 3269 张可解析 PNG 的 `first_mes` 都含有同一类“内置破限”推广文案，其中 3229 张的开场文本 hash 完全相同。这个字段已经被镜像再包装污染，不能证明原卡带有破限提示。

下面的 PNG 统计排除了 `first_mes`、`creator_notes`、`creatorcomment` 和 `declaration`。独立 JSON 按 UTF-8 with BOM 兼容方式解析，129 个文件中有 128 个成功，1 个空内容文件解析失败。

| 词面 | PNG 文件数 | 复核结果 |
| --- | --- | --- |
| `jailbreak` | 21 | 16 张属于同一套 `/jb` 条件后门；其余是已启用提示、角色扮演题材、监狱逃脱资料或社区称谓 |
| `破限` | 34 | 包含“突破限制”“打破限制”等普通短语；去掉这些组合后还剩 16 张使用独立词形 |
| `破甲` | 44 | 43 张指武器、护甲或战斗属性；1 张用它形容预设绕过能力较弱 |
| `越狱` | 41 | 36 张是逃离监狱或比喻性逃脱；5 张涉及模型或酒馆预设语境 |
| `解禁` | 31 | 都是剧情、游戏解锁、禁制解除或内容阶段变化，没有明确用作模型越狱标签 |
| `uncensor` | 8 | 7 张要求无遮拦的成人描写，1 张要求无遮拦的暴力描写 |

这些集合彼此重叠，不能相加得到“破限卡总数”。关键词也只能证明文本存在，不能证明提示有效。高召回语义扫描还能找到大量“不得拒绝”“忽略限制”和“最高权限”一类候选，但角色设定、游戏规则和普通叙事会产生很多误报，因此没有把这部分候选数当作越狱数量。

### 已确认的装载方式

| 方式 | 代表样本 | 静态状态 | 作用范围 |
| --- | --- | --- | --- |
| 条件世界书后门 | `2025年3月前/RPG跑团/豆之RPG_V3.2【正式版】.png` | 同系列 16 张均为 `enabled: true`、`constant: false`、`keys: ["/jb"]` | 只有扫描到 `/jb` 时才把对应条目放入上下文 |
| 角色级末端指令 | `2025年3月前/男性向/王道征途/奶子痛的萝莉kanae.png` | `post_history_instructions` 非空 | 在启用 Character's Instructions 时靠近生成端注入 |
| 常驻世界书指令 | `世界卡/媚华/媚华世界交换生.png` | 条目已启用且常驻，插入深度为 0 | 每轮进入上下文，持续要求放宽内容限制 |
| 扩展任务生成前缀 | `御姐，人妻/反差性瘾班主任.png` | `xiaobaix-tasks` 任务未禁用，触发点为 `after_ai` | 对应扩展运行时，由 JavaScript 组装额外请求前缀 |
| 禁用的可选条目 | `乱伦/纯爱、全家桶.png`、`萝莉/莉娜.png` | 两条都为 `enabled: false` | 导入后默认不进入提示，用户手动开启才生效 |
| 旧式独立预设 | `2025年3月前/重口注意！/人外/我的同学是巨大娘？(特殊XP谨慎下载)/配套破限.json` | `mainPrompt` 和 `jailbreak` 均有正文，格式顺序包含 `jailbreak` | 导入预设后替换或补充全局提示 |
| 现代独立预设 | `2025年3月前/男性向/乱∠和其他/萝莉性教育学校角色卡/辉夜自用破限3 (1).json` | `Jailbreak Prompt` 为 system 角色且已启用 | 随预设提示顺序进入请求 |
| 助手预填充槽 | `修仙/归墟/【归墟】【小猫大仙】3.0pp-0908.json` | `identifier` 为 `jailbreak` 且已启用 | 内容实际是继续游戏的多轮预填充，标识名本身不能证明它在绕过安全策略 |

`世界卡/异世界，奇幻/🎆异世界预设3.1🎆.json` 中名为 `✅Gemini越狱` 的助手提示处于禁用状态，通用 `jailbreak` 槽也是空白且禁用。`世界卡/女仆庄园/Lyean3.13奈亚子角色生成.json` 的非空 `jailbreak` 槽同样禁用。这些样本说明审计必须同时检查正文、角色、顺序和 `enabled`，不能看到字段名就判定正在运行。

部分卡只声明外部依赖。`生命线-异形` 要求删除外部主提示并改用豆系列越狱，`悲歌` 声明必须配合外部破限，女性向豆 RPG 则明确说本卡不包含破限。另一些卡要求关闭破限中的思维链或保留外部破限再执行制卡任务。这些内容属于安装与兼容说明，不是内嵌越狱正文。

### 风险判断

文本型破限只能影响发送给模型的上下文。服务端 system 指令、模型策略和版本变化仍可能覆盖它，静态文件也无法证明实际请求成功绕过限制。`enabled: false` 的条目、空白 `jailbreak` 槽和未命中关键词的条件条目不会按同一种方式生效。

能执行代码或改写请求的扩展任务风险最高。`反差性瘾班主任.png` 中的任务脚本只有在对应扩展已经安装并允许运行时才会执行，但一旦运行，它拥有读取酒馆变量、拼装请求和处理返回结果的能力。此类载荷应按第三方扩展代码审计，不能只按角色文案审阅。

导入前应先查看角色级 Prompt Overrides、常驻世界书、Post-History Instructions、扩展任务、Regex 和预设顺序。默认保持第三方任务与脚本禁用，在隔离配置中测试，并避免把真实 API 密钥交给未知预设、代理或前端。只想保留人物设定时，可以删除相关提示条目和扩展数据，再用纯文本模式验证角色是否仍能运行。

## 标准字段的构建思路

Character Card V2 和 V3 的核心字段承担不同职责。优秀设计会让每个事实只有一个主要归属位置。

| 字段 | 推荐职责 | 优点 |
| --- | --- | --- |
| `name` | 稳定运行名 | 支撑 `{{char}}` 替换和群聊身份 |
| `description` | 身份、经历、能力、关系、长期目标 | 每轮都能获得稳定人物基础 |
| `personality` | 决策方式、冲突反应、表达习惯、盲区 | 让性格成为可执行规则 |
| `scenario` | 当前时点、地点、关系阶段、眼前问题 | 给本轮提供明确起点 |
| `first_mes` | 默认可玩开场 | 建立第一轮节奏与回应空间 |
| `alternate_greetings` | 互斥的不同入口 | 提供重开、测试和路线选择 |
| `mes_example` | 语气、节奏、边界和玩法示范 | 用实例消除抽象规则歧义 |
| `system_prompt` | 卡级总约束 | 适合短而稳定的主持契约 |
| `post_history_instructions` | 临近生成端的短提醒 | 长对话中抵抗格式漂移 |
| `creator_notes` | 依赖、安装、版本和操作说明 | 将玩家说明与模型提示分开 |
| `character_book` | 条件资料、事件和规则模块 | 控制上下文成本 |
| `extensions.depth_prompt` | 指定深度的短规则 | 强化近期行为与输出格式 |

在 SillyTavern 中，`system_prompt` 和 `post_history_instructions` 是角色级 Prompt Overrides。它们分别只有在启用 **Prefer Char. Prompt** 和 **Prefer Char. Instructions** 时才替代对应默认提示；需要保留默认内容时，可在覆盖文本中插入 `{{original}}`。

V3 在 V2 字段基础上增加了必需的 `group_only_greetings`，以及可选的 `nickname`、`creator_notes_multilingual`、`source`、`assets`、`creation_date` 和 `modification_date`。V3 的 `character_book` 还要求世界书及每个条目保留 `extensions` 对象。只写入 `spec: "chara_card_v3"` 和 `spec_version: "3.0"` 并不能证明其余必需字段、类型和 PNG 块位置都符合规范。

现代大型卡经常把 `personality`、`scenario` 和 `mes_example` 留空，将全部内容放进世界书。这样便于在编辑器中开关模块，代价是人物声音更依赖世界书成功载入。可迁移方案适合保留一份短而完整的标准字段基础，再用世界书扩展规模。

## 人物文字的有效写法

### 用因果链代替形容词堆叠

人物资料最有用的结构由经历、当前目标、矛盾、判断规则和边界组成。

`英文卡/main_kiala-your-goblin-squire-30aa2378da34_spec_v2.png` 先写童年获救、长期准备和外出受训，再落到当前目标。角色想证明自己能够胜任侍从工作，紧张、忠诚、经验不足和冒险选择都能从这个目标推出。

`单人/林晓婉的物理学除灵记录.png` 把人物的认知偏差与情节机制绑在一起。角色拥有很强的行动能力，却会用日常逻辑解释异常。她的性格会直接改变冲突怎样发生，因而不只是装饰。

`英文卡/main_Blanchett_tavern.png` 使用一个集中概念统领能力、喜好、语言和开场。角色的每个小能力都服务于安稳睡眠，设定很短，辨识度仍然很高。

可复用的人物内核如下。

```yaml
character_core:
  identity: 当前社会身份
  formative_event: 仍在影响人物的过去事件
  current_goal: 眼下主动争取的结果
  fear_or_cost: 最不愿承受的损失
  contradiction: 会反复产生戏剧行为的内在矛盾
  decision_rule: 信息不足时怎样选择
  boundary: 哪些事不会做，遇到时怎样替代处理
```

### 把语气写成行为矩阵

只写“冷静”“温柔”“强势”很难约束输出。`单人/林晓婉的物理学除灵记录.png` 的人物语料按情绪和对话对象组织，给出句长、常用话题、身体动作和不同压力下的表达变化。

一份可迁移的语气表可以包含以下维度。

| 维度 | 需要说明的内容 |
| --- | --- |
| 句法 | 长短句比例、停顿、反问和省略习惯 |
| 词汇 | 专业词、口头词、禁用表达、称呼 |
| 普通状态 | 怎样发起话题，怎样结束对话 |
| 压力状态 | 会加快、沉默、解释还是转向行动 |
| 冲突状态 | 如何拒绝、谈判、追问和修复 |
| 对象差异 | 面对熟人、陌生人、上级和对手的变化 |
| 非语言行为 | 目光、距离、手部动作和注意对象 |

`mes_example` 至少应覆盖日常、压力、边界和机制交互。每段示例承担一种校准任务，避免用四段相似对白重复人物简介。

### 让人物保有独立目标

`世界卡/雨泊.png` 给 NPC 设置独立利益和风险判断。NPC 可以帮助、拒绝、误导或离开，行为取决于自身处境。世界因此不会围着玩家即时改变。

可迁移的人物条目适合记录当前需要、已知信息、未知信息、风险承受度、对玩家的条件性态度和离场后活动。这个结构能够减少群像声音趋同，也能支持 NPC 在画面外继续行动。

## 开场与引导

### 四拍开场

保存完好的优秀开场通常经过四个动作。

| 拍点 | 任务 |
| --- | --- |
| 定位 | 给出地点、时间、日常动作和少量感官信息 |
| 扰动 | 引入一个异常、来客、短缺、消息或矛盾 |
| 利害 | 让用户知道这件事为何需要现在处理 |
| 交接 | 在选择、问题、命令界面或未完成动作处停下 |

`正常向/星间旅行.png` 先建立长期休眠和飞船日常，再出现远方来信，最后让船载系统等待指令。世界设定、孤独感和玩家操作入口在同一场景完成。

`世界卡/雨泊.png` 给出两个风险收益明显不同的探索目标，结尾要求玩家决定先处理哪一个。选项会改变资源和危险，具有真实后果。

`正常向/暮光.png` 围绕同一固定案件准备三种身份入口。身份改变权限、初始知识和私人风险，案件真相保持一致。这是高质量多开局的典型。

### 多开场的五种变化轴

| 变化轴 | 适用玩法 |
| --- | --- |
| 玩家身份 | 调查、职业、阵营和权限差异 |
| 地点 | 城市、旅途、室内和危险区域 |
| 关系阶段 | 初识、稳定合作、冲突后修复 |
| 时间点 | 教程、主线中段、事件结束后 |
| 压力类型 | 日常、资源短缺、谜题、追逐和谈判 |

每个备用开场应完整初始化自己的事实和状态。只换名字、天气或一段措辞，重玩价值很低。

### 把控制权写进主持契约

`世界卡/锈蚀穹顶.png`、`2025年3月前/RPG跑团/Civ Simulator.png` 和 `2025年3月前/RPG跑团/反重力赛车模拟器.png` 都明确区分主持系统与玩家的控制范围。

有效契约会回答以下问题。

| 问题 | 推荐答案 |
| --- | --- |
| `{{char}}` 是谁 | 角色、主持人、裁判或世界模拟器 |
| `{{char}}` 控制什么 | 环境、NPC、后果、时间和公开状态 |
| `{{user}}` 控制什么 | 自己的选择、言语、行动意图和私人判断 |
| 怎样结算 | 依据规则、状态、骰点和已知事实 |
| 一轮在哪里停止 | 下一个有意义的玩家决定之前 |

单纯禁止代写玩家还不够，契约应给出替代动作。主持人读取玩家行为，结算后果，推进相关 NPC 和时钟，随后停在新的决定面前。

### 固定真相与开放路径

`正常向/暮光.png` 将案件真相预先锁定，把线索分成表层、深层和隐藏层。玩家可以通过技术、社交或推理接近真相，也可能遗漏证据。这个结构兼顾因果稳定和行动自由。

谜题、调查和阴谋卡可以采用同样方法。

```yaml
mystery:
  fixed_truth: 已经发生且不会因玩家猜测改变的事实
  public_facts: 开局可知内容
  clue_layers:
    surface: 容易发现但解释不完整
    deep: 需要行动或关系条件
    hidden: 接近真相后才可载入
  routes: 技术、社交、现场、档案
  clocks: 证据消失、对手行动、期限
  endings: 完整、部分、误判、超时
```

## 世界书的机制与优点

### 条目字段

世界书条目能否运行，取决于激活、筛选、排序和插入四组字段。样本同时出现 CCv3 嵌入世界书和 SillyTavern 独立 World Info JSON，两种结构不能按同一套字段名直接读写。

CCv3 的 `data.character_book.entries` 是数组，使用以下标准字段。

| 字段 | 运行作用 | 适合用途 |
| --- | --- | --- |
| `constant` | 无关键词也进入候选 | 核心公理和短协议 |
| `keys` | 主触发词或正则 | 人名、地点、组织、稳定 ID |
| `secondary_keys` | 主键命中后的附加筛选 | 地点加事件状态、人物加关系 |
| `selective` | 开启二级条件逻辑 | 减少宽词误触发 |
| `enabled` | 条目总开关 | 可选模块和幕后档案 |
| `insertion_order` | 同位置的顺序和预算优先级 | 公理、细节和格式的相对位置 |
| `position` | 角色定义前后等粗位置 | 广泛兼容的放置方式 |
| `use_regex` | 将 `keys` 解释为正则 | 动态触发模式 |
| `extensions` | 客户端专属附加字段 | 保存 SillyTavern 等宿主能力 |

SillyTavern 独立 World Info JSON 的 `entries` 是以 UID 为键的对象。`深渊/!随机事件生成器 0.72111.json` 使用 `key`、`keysecondary`、`disable`、`order`、`position`、`depth`、`role` 等字段，并通过以下扩展控制调度。

| 独立 World Info 字段 | 运行作用 | 适合用途 |
| --- | --- | --- |
| `probability`、`useProbability` | 候选后的概率筛选 | 氛围和随机事件 |
| `group`、`groupWeight` | 多个候选中加权选择 | 互斥事件、随机人物组件 |
| `groupOverride`、`useGroupScoring` | 确定性优先或按键命中评分 | 更精确的组内选择 |
| `sticky` | 激活后保留若干消息 | 短期场景提示 |
| `cooldown` | 激活后暂时不能再次触发 | 降低事件重复 |
| `delay` | 聊天达到一定消息数后生效 | 延迟事件 |
| `excludeRecursion`、`preventRecursion` | 控制递归进入和继续传播 | 防止无意激活链 |
| `delayUntilRecursion` | 只允许递归阶段激活 | 事件组件和收束条目 |

嵌入卡常把 SillyTavern 专属值映射到条目的 `extensions` 中，命名也可能改成 snake_case。转换时应显式映射，不能只把独立世界书对象复制进 `character_book`。`insertion_order` 或独立格式的 `order` 只影响提示顺序和预算竞争，不会建立剧情时间或状态覆盖关系。`sticky` 只保持提示注入，也不会把随机结果保存为权威事件。

### 有效分层

`世界卡/蒸汽幻想曲.png` 和 `世界卡/托瑞尔之书：被遗忘的国度v0.1.png` 展示了大型资料库的合理分层。少量世界公理常驻，种族、城市、组织和历史使用关键词检索。

推荐结构如下。

| 层 | 内容 | 触发方式 |
| --- | --- | --- |
| L0 | 玩家代理权、事实优先级、状态权威 | 极短常驻 |
| L1 | 世界物理、社会和经济公理 | 短常驻或高层关键词 |
| L2 | 人物、地点、组织、物品 | 精确主键与稳定别名 |
| L3 | 场景规则、事件组件、随机池 | 主键加二级条件 |
| L4 | 当前状态快照 | 固定 ID 注入或表格 |
| L5 | 幕后真相和完整档案 | 默认禁用，工具精确载入 |
| L6 | 历史归档 | 索引常驻，正文按需载入 |

这套布局既控制 token，也减少未来阶段和幕后事实提前泄漏。

### 正交事件组件

`深渊/!随机事件生成器 0.72111.json` 使用递归、Inclusion Group、概率、sticky 和 cooldown 组合事件。根条目先按地点激活，再递归选择人物头、场景、身份和状态组件，最后由收束条目统一格式。

这种方法把多个维度拆开，可以组合出大量结果，无需手写所有组合。适合天气、遭遇、任务委托、NPC 生成和旅行事件。

需要长期稳定的事件应在首次选中后保存 `event_id`、随机 seed、已选组件和阶段。分组与 sticky 可以负责提示调度，聊天变量或表格负责权威状态。

## 配套预设

`cards/` 内 129 个 JSON 中只有 6 个是真正带 `prompts` 和 `prompt_order` 的 Chat Completion 预设。其余文件还包括角色卡、世界书、Regex、Quick Reply、表格配置和自定义包。导入时必须按结构判断，不能只看扩展名。

### 预设的两层结构

预设先定义 prompt 对象，再通过 `prompt_order` 选择启用项和顺序。

```json
{
  "name": "Output Contract",
  "identifier": "output.contract",
  "role": "system",
  "content": "...",
  "system_prompt": false,
  "marker": false,
  "injection_position": 0,
  "injection_depth": 4,
  "injection_order": 100,
  "forbid_overrides": true
}
```

```json
{
  "character_id": 100001,
  "order": [
    { "identifier": "output.contract", "enabled": true },
    { "identifier": "worldInfoBefore", "enabled": true },
    { "identifier": "chatHistory", "enabled": true }
  ]
}
```

`identifier` 是 prompt 与排序表之间的连接键。`name` 主要服务编辑器显示。样本中 prompt 对象自身的 `enabled` 经常过期，`prompt_order[].order[].enabled` 更接近实际保存状态。

`marker: true` 表示由宿主插入动态内容。常见 marker 包括 `worldInfoBefore`、`personaDescription`、`charDescription`、`charPersonality`、`scenario`、`worldInfoAfter`、`dialogueExamples` 和 `chatHistory`。

### 有效模块顺序

卡内成熟预设常采用以下顺序。

| 顺序 | 模块 | 作用 |
| --- | --- | --- |
| 1 | 核心契约 | 权限、事实优先级、玩家边界 |
| 2 | 模拟规则 | 因果、世界自主性、角色知识边界 |
| 3 | 文风与视角 | 只启用一个主风格和一个视角 |
| 4 | 动态 marker | Persona、角色、世界书、场景和示例 |
| 5 | 聊天历史 | 当前对话 |
| 6 | 私下规划要求 | 检查连续性和下一事件，不要求输出过程 |
| 7 | 输出协议 | 正文、摘要、状态更新和选项 |
| 8 | 最终检查 | 标签、长度和内部内容隐藏 |

`修仙/凡人修仙传/【Dreammini】3.92-Ultra-0907(凡人修仙传).json` 的长处是高度模块化，语言、节奏、视角和文风可以独立选择。它还将正文、情节摘要、变量更新和分支选项分开。

`修仙/归墟/【归墟】4.3+适配【普赛克】长夜月，厌梦眠，碎漪彷徨避风期.json` 对剧情构建、反思和输出格式的分工更清楚，并使用较常规的 system 角色放置动态上下文。

`世界卡/女仆庄园/Lyean3.13奈亚子角色生成.json` 是任务型预设。它围绕角色生成安排已有角色列表、设计要求、YAML 输出和深度提示，再由 Quick Reply 提取字段并创建世界书条目。

可迁移重点是模块边界与顺序。原文件保存的超长上下文、超大输出、`top_k`、`reasoning_effort` 和 provider 选项依赖具体后端，换模型后需要重新测量。

## 输出协议与语法

复杂卡同时使用多种语法。它们的解析者不同，构建时必须标明每一层由谁处理。

### SillyTavern 宏

```text
{{user}}
{{char}}
{{random::a::b::c}}
{{roll::1d100}}
{{original}}
```

这些宏由宿主展开。当前 SillyTavern 明确支持双冒号参数和 droll 骰点，因此 `{{roll::1d100}}` 是有效写法。`{{getvar::name}}` 也是 SillyTavern 核心本地变量宏；`{{get_chat_variable::...}}`、`{{get_message_variable::...}}` 等形式来自其他运行层或扩展，不能默认跨客户端可用。若目标是跨 CCv3 客户端移植，还要按目标客户端测试宏子集，不能把 SillyTavern 的完整宏表当作 CCv3 的最低实现要求。

### 示例对话边界

```text
<START>
{{user}}: ...
{{char}}: ...
```

`<START>` 在 `mes_example` 中有专门语义，用于分隔示例。示例应展示输入、角色反应和回应结束位置，不宜写成第二份人物百科。

### XML 风格语义标签

```xml
<response>
  <story>可见正文</story>
  <summary>事实摘要</summary>
  <state_update schema="1">[]</state_update>
  <choices></choices>
</response>
```

模型容易识别带语义的区块，Regex 和脚本也能找到稳定边界。标签名应统一大小写，保持浅层嵌套，并且每个区块只有一个消费者。

`世界卡/雨泊.png` 还使用 `trigger_condition`、`protocol` 和 `action_steps` 一类标签，将触发条件与执行步骤分开。这种标签有实际语义，能帮助模型判断何时使用一条规则。

### YAML

```yaml
state:
  time: day-12 18:40
  location: north-gate
  active_event: event-91
```

YAML 适合人物档案、世界层级和人类可读配置。字段名稳定时，模型更容易维持结构。脚本真正消费 YAML 时，应使用解析器和 schema 校验。用一个跨越整段文本的正则提取 YAML，容易受缩进和额外说明影响。

### JSON 与 JSON Patch 风格更新

```json
[
  { "op": "replace", "path": "/time", "value": "day-12 19:10" },
  { "op": "add", "path": "/events/-", "value": { "id": "event-92" } }
]
```

JSON 更适合机器状态。解析器应限制允许的操作、路径和类型，拒绝未知字段，并将整批修改原子应用。部分第三方卡把框线状态栏放进 `json` 代码块，视觉上可读，却不能交给 `JSON.parse`。

### 自定义轻量 DSL

`校园/谈一场甜甜的恋爱吗~ 通用手机卡.png` 使用管道分隔记录表达消息、电话、论坛和地图对象。`归墟` 系列使用 `<UpdateVariable>` 包裹路径更新命令。它们的优点是输出短、便于正则定位，代价是需要自定义解析器。

新卡如果需要 DSL，应提供版本号、正式语法、转义规则、允许操作和错误处理。不能用 `eval` 或 `new Function` 解析模型输出。

### STscript 与 Quick Reply

`世界卡/女仆庄园/女仆庄园角色生成QR.json` 展示了较完整的 STscript 流程。

```text
/let
/input
/popup
/preset
/model
/trigger await=true
/regex name=...
/createentry
/setentryfield
/getentryfield
/abort
```

它先收集要求，再切换专用预设生成 YAML，随后用命名 Regex 提取字段，最后创建世界书条目并恢复原配置。这个流程把生成、提取、持久化和显示拆成独立步骤，适合人物生成器、任务生成器和档案导入。

## 状态机制

### 三种状态等级

| 等级 | 保存位置 | 例子 | 可靠性 |
| --- | --- | --- | --- |
| 软状态 | 正文、YAML 状态栏、自然语言摘要 | `修仙/凡人修仙传/V8.7.png` 的部分状态规则 | 依赖模型复写，容易漂移 |
| 调度状态 | 世界书 group、sticky、cooldown、delay | 随机事件生成器 | 能控制提示资格，不能证明世界事实 |
| 硬状态 | 聊天变量、dataTable、消息 metadata、动态世界书 | 万界 IP 表格、归墟 MVU、女仆庄园 QR | 可校验、可恢复、适合数值和阶段 |

状态栏本身是显示和提醒。金币、库存、伤势、任务阶段、关系边界、永久死亡和幕后真相需要硬状态源。

### 单一真值

大型卡最容易出现的故障是正文一份数值、状态栏一份数值、脚本变量又有一份数值。可迁移设计应确定一个权威来源。

```json
{
  "schema_version": 1,
  "revision": 17,
  "world": {
    "time": "day-12 18:40",
    "location": "north-gate",
    "active_scene": "scene-42"
  },
  "player": {
    "hp": 73,
    "currency": 1240,
    "inventory": ["item-7"]
  },
  "event": {
    "id": "event-91",
    "phase": "active",
    "seed": 4812
  },
  "pending_transaction": null
}
```

世界书定义字段和规则，变量或表格保存当前值，Regex 只显示快照。这样可以在重生成、切换聊天和上下文裁剪后恢复。

### 事务更新

`世界卡/搭载dataTable的万界IP系统/表格预设.json` 使用 `insertRow`、`updateRow` 和 `deleteRow` 将叙事与表格修改分开。样本本身没有 revision、事务 ID、幂等键或原子提交协议，下面是迁移时建议补充的可靠性设计，不是对原文件现有能力的描述。

```text
读取 revision
→ 生成 transaction_id 和 patch
→ 保存 prepared 状态
→ 校验路径、类型、范围和资源
→ 只应用一次
→ revision 加一
→ 重建固定 ID 状态快照
→ 标记 committed
```

随机值一旦生成就随事务保存。中断恢复时复用原值，避免通过重试重复抽取更有利的结果。

## Regex、脚本和 UI

### Regex 的正确职责

角色卡内常见规则结构如下。

```json
{
  "id": "uuid",
  "scriptName": "Render status block",
  "findRegex": "<status>([\\s\\S]*?)</status>",
  "replaceString": "$1",
  "placement": [2],
  "disabled": false,
  "markdownOnly": true,
  "promptOnly": false,
  "runOnEdit": true
}
```

当前 SillyTavern 中，`markdownOnly` 对应显示处理，`promptOnly` 对应发给模型的提示处理。两者都不选时，Regex 默认会直接改写聊天文件中的源文本，这种变更不可逆；两者都选时则同时影响显示和提示，但不写回聊天文件。字段行为仍应在目标 SillyTavern 版本中复测。

Regex 最适合做三件事。

| 职责 | 例子 |
| --- | --- |
| 定位 | 捕获 `<status>`、`<summary>` 和 `<choices>` |
| 隐藏 | 从显示或后续提示移除机器区块 |
| 轻量渲染 | 把结构化字段映射成受限 HTML |

Regex 不适合作为权威数据库、事务引擎或任意代码容器。

导入卡片或预设中的 Regex 也不等于自动授权运行。当前 SillyTavern 源码分别用 `character_allowed_regex` 和 `preset_allowed_regex` 记录用户允许的角色与预设，实际处理文本时只读取已允许脚本。发行说明应要求用户先检查脚本内容、影响范围和写回策略，再显式允许；不要建议关闭这一保护。

### UI 的优势

`插图卡/初晴时雨.png` 将状态读取与显示分开，界面从消息 metadata 读取 `stat_data`，并使用 `innerText` 写入部分动态值。`插图卡/维多利亚女仆玛利亚（134插图）.png` 用简短标签选择远程插图。`世界卡/无限轮回.png` 和 `修仙/凡人修仙传/V8.7.png` 则提供完整的保存、摘要、编辑和恢复界面。

这些设计改善了玩家对长期状态的理解，也把重复命令变成按钮。更可迁移的实现会使用固定组件、转义后的文本和资源清单，让模型只输出 `view_id`、字段值或 `image_id`。

独立前端样本存在可定位的风险，而不只是抽象的“第三方 HTML 不可信”。`修仙/修仙之旅v1.0/index.html` 将主 API 和额外 API 的密钥写入普通 `localStorage` 的 `gameConfig`，同源脚本一旦执行即可读取。它虽然用 `textContent` 显示故事正文，却把模型返回的选项、推理字段、关系和历史值，以及存档名称等动态内容拼入 `innerHTML`。未经可信消毒时，这些路径会形成持久或反射型 DOM 注入面。该文件还会直接向用户填写的 API 端点发起请求，因此只能在隔离环境中审计后运行，不能把真实密钥交给未经审查的副本。

### TavernHelper 和 MVU

`世界卡/无限轮回.png` 与 `修仙/归墟/归墟6.9.png` 使用 TavernHelper 读取消息、生成内容、修改世界书和写回消息 metadata。MVU 消费 `<UpdateVariable>` 并生成下一轮变量状态。

它们的长处是反馈回路完整，状态、摘要、世界书与 UI 可以相互同步。实际移植时要处理远程依赖固定、权限申请、跨卡存储命名空间、输入转义和失败回滚。第三方脚本拥有改聊天和世界书的能力，应按扩展代码审计。

## PNG、版本和发行结构

### PNG 载荷

角色卡通常放在 PNG 的 `tEXt` 块中。

```text
PNG
├── tEXt keyword=chara value=base64(UTF-8 JSON)
├── tEXt keyword=ccv3 value=base64(UTF-8 JSON)
└── image data
```

兼容性较好的双载荷使用真实 V2 数据写入 `chara`，真实 V3 数据写入 `ccv3`，两者的 `data` 语义保持一致。把 V3 原样复制到两个块只能提供冗余，不能提供 V2 后备。

全库可见的主要形态如下。

| `chara` / `ccv3` | 文件数 | 说明 |
| --- | --- | --- |
| V3 / V3 | 1408 | 两个块都声明 V3，属于冗余而非 V2 后备 |
| V2 / 缺失 | 1240 | 常规 V2 卡 |
| V2 / V3 | 534 | 具有双版本载荷形态，仍需逐字段验证 |
| 旧格式 / 缺失 | 74 | 无 spec 的历史卡 |
| V3 / 缺失 | 12 | V3 只放在 `chara` |
| V2 / V2 | 1 | `ccv3` 中仍是 V2 |
| 无卡片载荷 | 4 | 普通图片 |

这些分类只检查两个载荷的 `spec` 标签，没有证明必需字段、字段类型、V3 `group_only_greetings`、世界书 `extensions` 或两份数据语义都合规。CCv3 规范要求 V3 PNG 载荷位于名为 `ccv3` 的 `tEXt` 块；把 V3 只写进 `chara` 是客户端兼容现象，不是规范 V3 容器。

多兆字节 HTML、字体和脚本同时复制进两个未压缩 Base64 文本块，会显著放大文件。复杂应用包更适合将资源拆成版本化附件，或使用支持资源归档的 CHARX 等容器格式。

### 配套文件并不会自动连接

同一目录中的 PNG、预设、世界书、Regex 和 Quick Reply 只是物理上相邻。除非卡片内嵌数据或通过固定名称引用，客户端不会自动把它们组装起来。

成熟发行包应在 `creator_notes` 或 README 中列出以下信息。

| 信息 | 内容 |
| --- | --- |
| 导入顺序 | 角色卡、世界书、预设、Regex、QR |
| 运行名称 | 世界书名、预设名、Regex 名和变量前缀 |
| 版本要求 | SillyTavern 与扩展的最低版本 |
| 权限 | 网络、世界书写入、消息写入和本地存储 |
| Regex 授权 | 卡片与预设脚本的名称、作用域、写回策略和允许步骤 |
| 降级模式 | 不装扩展时仍可玩的文本模式 |
| 恢复方法 | 清理变量、恢复预设和载入检查点 |

## 最值得迁移的优点

### 可直接迁移

| 方法 | 来源代表 | 迁移价值 |
| --- | --- | --- |
| 因果型人物内核 | Kiala、林晓婉、Blanchett | 角色行为可预测且有辨识度 |
| 四拍开场 | 星间旅行、雨泊 | 快速进入行动，不淹没在说明中 |
| 多身份开局 | 暮光 | 同一真相产生不同权限和风险 |
| 固定真相、开放路径 | 暮光 | 保持推理因果和玩家自由 |
| 用户控制边界 | 锈蚀穹顶、Civ Simulator | 减少代写玩家和强行推进 |
| 示例演示完整循环 | Civ Simulator、深岩星系 | 校准输入、结算、状态和交接 |
| 人物地点分条 | 蒸汽幻想曲、托瑞尔之书 | 降低固定上下文成本 |
| 数值转叙事 | 雨泊 | 让状态变化进入感官和行动 |
| 人物资料与开场分源 | 多个 TXT 人物包 | 便于复用、评审和版本管理 |

### 改造后迁移

| 方法 | 需要补的工程条件 |
| --- | --- |
| 随机事件递归组合 | 冻结 `event_id`、seed 和阶段 |
| YAML 人物生成 | 正式解析器、schema、重复检测和回滚 |
| dataTable 状态 | revision、事务 ID、幂等和恢复 |
| MVU 变量更新 | 本地固定版本、路径白名单和原子更新 |
| HTML 状态栏 | 组件隔离、转义、内容安全策略和降级文本 |
| 动态世界书写入 | 固定逻辑 ID、权限确认和事务日志 |
| 自动摘要 | 来源范围、hash、版本和重新生成规则 |
| 插图选择 | 本地或内容寻址资源清单 |

### 只保留思路

以下做法体现了真实需求，现有实现不适合原样复制。

| 现有做法 | 可保留的需求 | 推荐替代 |
| --- | --- | --- |
| Regex 内嵌数兆字节应用 | 题材化界面 | 宿主安装的可信组件 |
| 从 `main`、`beta` 远程加载脚本 | 自动更新扩展 | 固定版本与哈希 |
| `new Function` 解析状态 | 灵活读取对象 | JSON 解析加 schema |
| 模型输出直接进入 `innerHTML` | 富文本状态展示 | 转义文本和受限组件 |
| 大量条目全部 constant | 保证规则不漏 | 短常驻加精确检索 |
| 复制目录保存版本 | 保留历史版本 | 开发源、构建器和 manifest |
| 用 Regex 同时保存和显示状态 | 降低文件数量 | 状态层与显示层分开 |

## 推荐的可迁移架构

### 运行流程

```text
标准 V3 角色卡
→ 短核心字段保证纯文本可玩
→ 世界书按人物、地点和事件检索
→ 预设组织动态上下文和输出协议
→ 模型输出 story、summary、state_update、choices
→ 可信运行时校验并提交 state_update
→ 固定 ID 注入最新状态快照
→ 安全组件显示状态和选项
```

### 角色卡模板

```jsonc
{
  "spec": "chara_card_v3",
  "spec_version": "3.0",
  "data": {
    "name": "角色名",
    "description": "稳定身份、经历、能力、关系和长期目标",
    "personality": "决策方式、冲突反应、盲区和语言习惯",
    "scenario": "当前时点、地点、关系阶段和眼前问题",
    "first_mes": "一个完整、可回应的默认开场",
    "alternate_greetings": [
      "改变身份、地点或关系阶段的完整入口"
    ],
    "group_only_greetings": [],
    "mes_example": "<START>\n{{user}}: ...\n{{char}}: ...",
    "system_prompt": "短主持契约和用户代理权",
    "post_history_instructions": "短格式提醒",
    "creator_notes": "依赖、版本、导入和降级说明",
    "creator": "作者",
    "character_version": "1.0.0",
    "tags": ["题材", "语言"],
    "character_book": {
      "name": "角色世界书",
      "scan_depth": 4,
      "token_budget": 2048,
      "recursive_scanning": false,
      "extensions": {},
      "entries": []
    },
    "extensions": {
      "depth_prompt": {
        "prompt": "只放近期必须保持的短规则",
        "depth": 4,
        "role": "system"
      }
    }
  }
}
```

### 世界书条目模板

```json
{
  "id": "location-library",
  "name": "地点名",
  "comment": "编辑器标签",
  "keys": ["地点名", "稳定别名"],
  "secondary_keys": [],
  "content": "只写该地点的事实、行动机会和当前有效限制。",
  "enabled": true,
  "insertion_order": 100,
  "case_sensitive": false,
  "use_regex": false,
  "constant": false,
  "selective": false,
  "position": "after_char",
  "extensions": {}
}
```

### 输出协议模板

```xml
<response version="1">
  <story>只包含玩家可见叙事。</story>
  <summary>只记录本轮新增且会影响连续性的事实。</summary>
  <state_update schema="1">
    []
  </state_update>
  <choices>
    <choice id="1">可选行动</choice>
  </choices>
</response>
```

应用状态更新时，应验证 schema、操作、路径、值类型、revision 和 transaction ID。解析失败时保留原始文本供恢复，不执行部分修改。

### 五步构建流程

1. 写一句产品承诺，明确人物体验或玩法循环。
2. 完成人物因果内核、主持契约、默认开场和四类示例。
3. 将世界资料拆为短常驻、关键词资料、事件和幕后档案。
4. 只有在长期状态确实需要时才增加结构化输出与权威状态层。
5. 最后增加 UI、自动化、构建器和发行包，并保留纯文本降级模式。

## 发布检查

### 文本

- 人物的目标、矛盾和边界能共同解释其下一步行动。
- 默认开场能够直接回应，结尾停在玩家决定之前。
- 备用开场改变一项主要轴，并初始化一致状态。
- 示例覆盖日常、压力、边界和机制循环。
- NPC 有独立目标、知识边界和离场后的活动。
- 主持契约不代写玩家选择、言语和私人结论。

### 世界书

- 常驻正文有明确预算，只保留公理和短协议。
- 非 constant 条目都有可验证的触发入口。
- 中文关键词避免单字符、宽泛词和无意义重复。
- 二级键、递归、group 和 timed effects 各有测试场景。
- 幕后档案默认禁用，未来阶段不会提前载入。
- 状态只有一个权威来源。

### 协议与状态

- 每个标签只有一个定义和一个主要消费者。
- JSON 和 YAML 通过正式解析器及 schema 校验。
- 所有状态修改都有 revision、事务 ID 和幂等处理。
- 随机结果生成后立即冻结，恢复时不会重掷。
- 重生成、swipe、聊天切换和中断后能够恢复。
- 摘要记录来源范围、版本和内容 hash。

### 工程

- `chara` 是真实 V2 后备，`ccv3` 是真实 V3。
- 角色卡、世界书、预设、Regex 和 QR 有稳定版本。
- 固定名称、变量前缀、注入 ID 和逻辑记录 ID 有文档。
- 第三方脚本不从可变分支加载，资源可校验。
- 卡片与预设 Regex 经人工检查后再在宿主中显式允许。
- 模型文本进入 HTML 前完成转义或消毒。
- API 密钥不存入角色卡、世界书或普通 `localStorage`。
- 构建器能确定性生成发行文件，并提供只读检查。
- 在纯文本、SillyTavern 核心和完整扩展三种环境分别测试。

## 规范与运行依据

- [Character Card V3 Specification](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md) 用于核对 V3 JSON、PNG `ccv3` 块、Lorebook 和宏的最低规范。
- [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/) 用于核对字段进入提示的方式、Prompt Overrides、Character's Note 和 `<START>`。
- [SillyTavern World Info](https://docs.sillytavern.app/usage/core-concepts/worldinfo/) 用于核对触发、插入、分组、递归、预算和 timed effects 的当前语义。
- [SillyTavern Macros](https://docs.sillytavern.app/usage/core-concepts/macros/) 用于核对双冒号参数、变量和 droll 语法。
- [SillyTavern Regex](https://docs.sillytavern.app/extensions/regex/) 与当前 [Regex engine source](https://github.com/SillyTavern/SillyTavern/blob/release/public/scripts/extensions/regex/engine.js) 用于核对脚本作用域、写回方式和角色、预设 allowlist。

## 代表样本索引

| 主题 | 代表路径 | 主要参考点 |
| --- | --- | --- |
| 简洁人物卡 | `sillytavernassets-main/cards/英文卡/main_Blanchett_tavern.png` | 集中概念、语气和示例 |
| 人物与机制结合 | `sillytavernassets-main/cards/单人/林晓婉的物理学除灵记录.png` | 因果人格、语料矩阵 |
| 情绪型开场 | `sillytavernassets-main/cards/正常向/星间旅行.png` | 世界信息与行动交接 |
| 固定真相 | `sillytavernassets-main/cards/正常向/暮光.png` | 多身份、线索层级、开放路径 |
| 生存模拟 | `sillytavernassets-main/cards/世界卡/雨泊.png` | NPC 自主、状态转叙事、节奏时钟 |
| RPG 契约 | `sillytavernassets-main/cards/世界卡/锈蚀穹顶.png` | 控制权、骰点、遭遇规则 |
| 紧凑循环 | `sillytavernassets-main/cards/2025年3月前/RPG跑团/Civ Simulator.png` | 示例展示完整输入输出循环 |
| 大型检索世界书 | `sillytavernassets-main/cards/世界卡/蒸汽幻想曲.png` | 常驻公理与关键词资料 |
| 随机事件 | `sillytavernassets-main/cards/深渊/!随机事件生成器 0.72111.json` | 递归、分组和概率组合 |
| 表格状态 | `sillytavernassets-main/cards/世界卡/搭载dataTable的万界IP系统/表格预设.json` | 结构化修改与状态反馈回路 |
| 动态人物生成 | `sillytavernassets-main/cards/世界卡/女仆庄园/女仆庄园角色生成QR.json` | 生成、提取和世界书写入 |
| MVU 应用 | `sillytavernassets-main/cards/修仙/归墟/归墟6.9.png` | 状态、摘要、UI 和恢复 |
| 独立前端 | `sillytavernassets-main/cards/修仙/修仙之旅v1.0/index.html` | 浏览器存储、检索和 API 调用 |

## 结论

第三方卡最值得学习的部分可以压缩成一条构建原则。

先用标准字段做出完整可玩的角色，再用世界书扩大世界，用结构化协议表达状态，用可信客户端保存状态，最后用 UI 改善可见性。

优秀文本卡依靠清楚的人物因果、可回应的开场和具体示例。优秀世界卡依靠短常驻、精确检索、固定真相和独立 NPC。优秀系统卡还会把正文、摘要、状态和选项分流，并给状态提供单一真值、事务与恢复。

第三方复杂卡已经证明这些产品目标有价值。迁移时应保留目标与数据流，重写远程脚本、巨型 Regex、未校验 DSL 和多处状态真值。这样可以获得相近的可玩深度，同时维持可审计、可测试和跨版本维护能力。
