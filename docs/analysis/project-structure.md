# 项目结构分析

分析日期：2026-08-27

## 项目定位

这是一个以 SillyTavern 角色包创作为核心的内容仓库，同时保存了一个大型第三方角色卡与预设镜像。仓库不是单一应用，没有根级依赖清单、统一构建命令或统一测试入口。

## 根目录

| 路径 | 职责 |
| --- | --- |
| `AGENTS.md` | 仓库级工作规则、制作基线、分析文档路由和验证入口 |
| `role/` | 自制 SillyTavern 角色包；每个一级子目录是一个独立发行单元 |
| `docs/` | 世界观参考、实施计划和分析文档 |
| `sillytavernassets-main/` | 下载的第三方角色卡、世界书、预设及附件镜像 |

根目录未发现 `package.json`、`pyproject.toml`、`requirements.txt`、`Makefile`、CI 配置或统一测试脚本。Python 和 Node.js 只在个别角色包中使用，并且均不依赖第三方包。

## 自制角色包

### 总览

| 目录 | 主题 | 主要发行内容 | 开发方式 |
| --- | --- | --- | --- |
| `role/boundless-private-collection/` | 全能玩家的世界穿越与收藏沙盒 | 角色卡、世界书、随机 Quick Reply、README | 直接维护 |
| `role/forbidden-courier/` | 星际黑色公路与禁物委托 | 角色卡、世界书、Quick Reply、世界观、README | `build.mjs` 是生成源 |
| `role/jinghai-manor/` | 2035 镜海庄园低冲突沙盒 | 顾弥真角色卡、苏栖白 Persona、世界书、图像提示词 | 直接维护 |
| `role/lanjin-case-0/` | 架空华夏隐秘超凡调查 | 秦峥角色卡、谢昭宁 Persona、世界书、PNG 卡和立绘 | 直接维护，多份发行副本 |
| `role/nive/` | 被遗忘国度白狼女仆长期 RP | 角色卡、Persona、三本世界书、设定、PNG 卡 | 直接维护，多份发行副本 |
| `role/rosamund-hale/` | 失忆侦探主线与城市案件沙盒 | 角色卡、62 条完整世界书、Quick Reply、玩家文档 | 六份开发源经 Python 构建 |
| `role/zheng-jin-infinite-flow/` | 固定女主的任务制无限流 | 角色卡、53 条世界书、D100 Quick Reply、PNG 卡、ZIP | 直接维护，多份发行副本 |
| `role/zhou-heng-marvel-system/` | 2008 MCU 起步的长期系统战役 | 角色卡、78 条完整世界书、Quick Reply、Persona、README | 七份开发源经 Python 构建 |

### `boundless-private-collection`

- `boundless-private-collection.character.json`：Character Card V2。
- `boundless-private-collection-worldbook.json`：权限、目标、世界、收藏、改造和随机规则。
- `boundless-private-collection-random.quick-replies.json`：按需 D100。
- 固定运行名称为 `boundless-private-collection-worldbook`，Quick Reply 预设名为 `Boundless-Private-Collection-Random`。
- 没有构建器或测试套件，修改后至少验证三个 JSON。

### `forbidden-courier`

- `forbidden-courier.character.json`：Character Card V2。
- `forbidden-courier-worldbook.json`：七大霸权、三条长期阴谋和八份固定委托。
- `forbidden-courier-quick-replies.json`：客户端 D100、委托锁定、结案和状态恢复。
- `world-bible.md`：可读设定总纲，不导入 SillyTavern。
- 固定世界书运行名称为 `forbidden-courier-worldbook`。
- `build.mjs` 会重写角色卡、世界书、Quick Reply 和 README。相关改动必须保持构建源与发行文件同步；`node build.mjs` 不是只读检查。

### `jinghai-manor`

- `gu-mizhen.character.json`：顾弥真主卡。
- `su-qibai-persona.md`：苏栖白固定玩家 Persona。
- `jinghai-manor-worldbook.json`：庄园共享世界书。
- `gu-mizhen-image-prompt.md`：单人立绘提示词。
- 没有构建器、Quick Reply 或测试套件，文件直接维护。

### `lanjin-case-0`

- `qin-zheng.character.json`：秦峥角色卡。
- `xie-zhaoning-persona.md`：谢昭宁 Persona。
- `lanjin-worldbook.json`：隐秘社会、能力阶段和首案阶段。
- `Qin Zheng.png`：带 `chara` 元数据的可导入 PNG 卡，分析时与 JSON 卡一致。
- `秦峥.png`：普通立绘。
- 没有同步脚本。修改角色卡时不能假定 JSON 和 PNG 会自动同步。

### `nive`

- `nive.character.json`：妮薇角色卡。
- `master-persona.md`：玩家 Persona 模板。
- `nive-shared-lorebook.json`：共享生活与关系条目。
- `nive-story-stages-lorebook.json`：阶段 0 至 6，同一时间只应启用一个阶段。
- `nive-dnd-lorebook.json`：轻量 D&D 舞台。
- `nive.md`：完整创作者设定。
- `nive-long-rp-setup.md`：实际安装与阶段操作说明。
- `Nive.png`：带 `chara` 元数据的 PNG 卡。分析时其 `system_prompt` 与当前 JSON 有轻微差异，不能把它当成 JSON 的可靠镜像。

### `rosamund-hale`

- 顶层是玩家发行文件：角色卡、`rosamund-complete-lorebook.json`、Quick Reply、OOC 文档和 README。
- `archive/creator/` 保存含剧透的创作者规格。
- `archive/development/sources/` 中六份拆分世界书是唯一开发源。
- `archive/development/build_complete_lorebook.py` 确定性生成 62 条完整世界书和 manifest。
- `archive/development/test_rosamund_package.py` 验证角色包、状态机和文档契约。
- 固定世界书运行名称为 `rosamund-complete-lorebook`，状态变量使用 `rh_` 前缀。
- 普通玩家不应导入拆分开发源，否则会重复世界书条目。

在 `role/rosamund-hale/` 下验证：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 archive/development/test_rosamund_package.py
PYTHONDONTWRITEBYTECODE=1 python3 archive/development/build_complete_lorebook.py --check
```

### `zheng-jin-infinite-flow`

- `zheng-jin.character.json`：Character Card V2。
- `zheng-jin-worldbook.json`：系统规则、前五个固定副本和动态副本规则。
- `zheng-jin-d100.quick-replies.json`：玩家公开 D100 和 NPC D100。
- `zheng-jin.card.png`：分析时内嵌卡与 JSON 一致。
- `zhengjin.zip`：发行归档；没有可重现归档的构建脚本。
- 修改 JSON、PNG 卡或 ZIP 时不能假定另外两份副本会自动同步。

### `zhou-heng-marvel-system`

- 顶层是五个玩家文件：角色卡、完整世界书、Quick Reply、Persona 和 README。
- `archive/creator/` 保存完整创作规格。
- `archive/development/sources/` 中七份拆分世界书是唯一开发源。
- `archive/development/build_zhou_heng_marvel_system_package.py` 生成 78 条完整世界书和 manifest。
- `archive/development/test_zhou_heng_marvel_system_package.py` 验证角色卡、骰子协议、内容边界和构建契约。
- 固定世界书运行名称为 `zhou-heng-marvel-system-worldbook`，Quick Reply 预设名为 `Zhou-Heng-Marvel-System`，状态变量使用 `zhms_` 前缀。
- 普通玩家不应导入拆分开发源。

在 `role/zhou-heng-marvel-system/` 下验证：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 archive/development/test_zhou_heng_marvel_system_package.py
PYTHONDONTWRITEBYTECODE=1 python3 archive/development/build_zhou_heng_marvel_system_package.py --check
```

## 文档区

| 路径 | 内容 |
| --- | --- |
| `docs/superpowers/plans/2026-08-26-zhou-heng-marvel-system.md` | 周衡角色包的历史实施计划；未勾选的 checkbox 不代表当前实现不存在 |
| `docs/worid-lora/civilization-domain-worldview.md` | “文明大域”可读世界观参考 |
| `docs/worid-lora/civilization-domain-worldview.json` | 同一世界观的结构化版本 |
| `docs/analysis/` | 仓库和第三方素材分析索引 |

`docs/worid-lora/` 的现有拼写就是 `worid-lora`。没有明确迁移任务时不要擅自改名，也不要假定 Markdown 和 JSON 之间存在自动同步工具。

## 第三方素材镜像

`sillytavernassets-main/` 约 3.26 GB，主体是下载内容：

- `cards/`：32 个分类、3506 个文件，包含 PNG 角色卡、普通图片、世界书、说明、压缩包、安装器和脚本。
- `presets/`：463 个文件，混合提示预设、正则、Quick Reply、世界书、角色卡、脚本、图片和压缩包。
- 该目录不是自制角色包开发源。默认不批量修改、格式化、执行或解压其内容。
- PNG 可能是带 `chara` 元数据的卡，也可能只是普通图片，不能只凭扩展名判断。
- 合集内至少有一个无法解析的 JSON，因此不适合运行“全仓所有 JSON 必须合法”式验证。
- 详细预设分析见 [`presets-catalog.md`](presets-catalog.md)。

## 技术栈与格式

- SillyTavern Character Card V2 JSON。
- World Info/Lorebook JSON。
- Quick Reply v2、STscript 和 SillyTavern 宏。
- Markdown Persona、设定、安装说明和创作者规格。
- 带 `chara` 元数据的 PNG 卡及普通立绘。
- Python 3 标准库构建器与 `unittest`，仅用于 Rosamund 和 Zhou Heng。
- Node.js ESM 构建器，仅用于 Forbidden Courier，无 npm 依赖。
- ZIP 等发行副本和第三方归档。

## 主要风险

- 运行时名称、变量前缀、注入 ID 和世界书条目 `comment` 可能被 STscript 精确检索，不能随意重命名。
- Rosamund 和 Zhou Heng 的完整世界书是生成物，直接修改会在下次构建时丢失。
- Forbidden Courier 的四个顶层文件由 `build.mjs` 生成，手改输出而不改构建源会造成漂移。
- Lanjin、Nive 和 Zheng Jin 同时存在 JSON、PNG 或 ZIP 副本，但没有自动同步工具。
- 仓库包含大量已跟踪二进制文件，避免无意义重导出、重新压缩或全仓格式化。
- 静态验证不能替代 SillyTavern 中的实际导入、世界书绑定、Quick Reply 和 STscript 交互测试。
