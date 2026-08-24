# Code Review 质量审查报告 · st / role/rosamund-hale

> THUNDERSOFT · CONFIDENTIAL
> 兜底 Markdown 模板, 用于 Gerrit / GitLab MR / GitHub PR 评论区粘贴。HTML 是主交付物。

## §1 执行摘要

| Field      | Value           |
| ---------- | --------------- |
| Repository | st        |
| Module     | role/rosamund-hale      |
| Branch     | main      |
| Commit     | `d7f54ba + local changes`    |
| 审查时间   | 2026-08-24 16:31   |
| Reviewer   | OpenCode Code Review    |
| 扫描模式   | 本地改动 + 未跟踪完整目录   |
| 应用规则   | Common 9维度 113+项, SillyTavern 1.18 STscript/World Info 官方语义, Rosamund package invariants |

**综合评分: 8.5 / 10  →  B 级  →  CL 评分 0**

| Critical | Major | Minor | Q/Praise |
| -------- | ----- | ----- | -------- |
| 0 | 10 | 3 | 0 |

> **评审边界**: 本报告只覆盖 **编码规范 / 设计规范 / 历史 Bug Root Cause 逻辑检查**; 不覆盖架构设计 / Bug Fix / 功能验收。

## §2 各维度详细评分

| 维度 | 权重 | 得分 | 🔴 Critical | 🟡 Major | 🟢 Minor | 💡 Q/P | 备注 |
| ---- | ---- | ---- | ----------- | -------- | -------- | ------ | ---- |
| 维度1·空安全与边界防护 | 20% | 10.0/10 | 0 | 0 | 0 | 0 |  |
| 维度2·线程安全与同步机制 | 14% | — | 0 | 0 | 0 | 0 | N/A |
| 维度3·资源与内存管理 | 20% | 9.0/10 | 0 | 1 | 0 | 0 |  |
| 维度4·代码逻辑与语法规范 | 14% | 5.7/10 | 0 | 4 | 1 | 0 |  |
| 维度5·性能与体验优化 | 8% | 9.7/10 | 0 | 0 | 1 | 0 |  |
| 维度6·兼容性、安全与工程规范 | 8% | 6.0/10 | 0 | 4 | 0 | 0 |  |
| 维度7·代码风格与命名规范 | 8% | 9.7/10 | 0 | 0 | 1 | 0 |  |
| 维度8·IPC 通信安全 | 6% | — | 0 | 0 | 0 | 0 | N/A |
| 维度9·序列化与数据格式 | 6% | 9.0/10 | 0 | 1 | 0 | 0 |  |

## §3 问题汇总表

| # | 严重 | 规则 | 维度 | 检查项 | 位置 | 修复建议 |
|---|------|------|------|--------|------|----------|
| 1 | Major | `6.3` | 维度六·兼容性、安全与工程规范 | 尚未提供用户要求的单一整合世界书 | `role/rosamund-hale/README.md:5-47` | 生成一份包含 62 条外部条目的规范整合世界书，并明确卡内嵌入 Lore 在完整安装时是否跳过。 |
| 2 | Major | `9.1` | 维度九·序列化与数据格式 | 直接合并会发生 entries 键与 uid 冲突 | `role/rosamund-hale/rosamund-city-lorebook.json:2-4` | 整合文件必须由确定性构建或校验流程产生，不能手工拼接 JSON 对象。 |
| 3 | Major | `6.3` | 维度六·兼容性、安全与工程规范 | Quick Reply 硬编码旧核心案件世界书名称 | `role/rosamund-hale/rosamund-quick-replies.json:205-206` | 确定整合书唯一名称后，同时更新 Quick Reply、角色卡、规则、README 和 OOC 文档，并在初始化时做已知条目预检。 |
| 4 | Major | `3.15` | 维度三·资源与内存管理 | 结案历史注入无上限增长 | `role/rosamund-hale/rosamund-quick-replies.json:225` | 为长期沙盒设置明确容量和淘汰策略，并用 /tokens 或 /len 实际校验摘要尺寸。 |
| 5 | Major | `4.17` | 维度四·代码逻辑与语法规范 | 长案件缺少持久化的活动案件状态账本 | `role/rosamund-hale/rosamund-quick-replies.json:149,225` | 把活动状态作为有界、可重建的唯一账本，并显式传给案件板和结算生成。 |
| 6 | Major | `4.24` | 维度四·代码逻辑与语法规范 | 关键状态更新不是事务式或可恢复的 | `role/rosamund-hale/rosamund-quick-replies.json:187,206,225,339,358` | 让关键流程幂等并可恢复，避免出现变量是新档案但模型仍收到旧注入的 split-brain 状态。 |
| 7 | Major | `6.2` | 维度六·兼容性、安全与工程规范 | 缺少旧聊天迁移、导出和注入重建流程 | `role/rosamund-hale/README.md:204-210` | 版本升级和长会话换档前必须能检测孤儿变量、旧格式数组和缺失注入。 |
| 8 | Major | `4.13` | 维度四·代码逻辑与语法规范 | 核心案件使用模糊查找但未核对返回身份 | `role/rosamund-hale/rosamund-quick-replies.json:206` | 避免错误档案被静默标记为另一个案件，是整合书版本预检的一部分。 |
| 9 | Major | `4.17` | 维度四·代码逻辑与语法规范 | 动态标题与核心案件共用完成状态命名空间 | `role/rosamund-hale/rosamund-quick-replies.json:206,225` | 控制键和显示文本必须分离，核心完成状态应使用精确键查询。 |
| 10 | Major | `6.3` | 维度六·兼容性、安全与工程规范 | 尚未完成真实 SillyTavern 导入和按钮烟测 | `role/rosamund-hale/README.md:204-221` | 这是发布前必须完成的运行时验收；静态检查不能证明 STscript 在真实 UI 中按预期执行。 |
| 11 | Minor | `4.24` | 维度四·代码逻辑与语法规范 | 剧情阶段存在两个独立权威来源 | `role/rosamund-hale/rosamund-quick-replies.json:299-301` | 同一个状态应只有一个权威来源，或拥有自动一致性校验。 |
| 12 | Minor | `7.9` | 维度七·代码风格与命名规范 | 案件目录和阶段映射多处重复且无生成校验 | `role/rosamund-hale/rosamund-quick-replies.json:205-206` | 整合世界书时同时建立可复现构建与校验，避免两个发布文件组合不兼容。 |
| 13 | Minor | `5.1` | 维度五·性能与体验优化 | 19 个 Quick Reply 全部常驻显示 | `role/rosamund-hale/rosamund-quick-replies.json:9-370` | 属于可选体验优化，不影响当前静态正确性。 |

## §4 改进路线图

### Critical · 必修 (合入前)
- 无

预估工时: **0.0 h**

### Major · 强烈建议
- `role/rosamund-hale/README.md:5-47` — 尚未提供用户要求的单一整合世界书 (规则 `6.3`)
- `role/rosamund-hale/rosamund-city-lorebook.json:2-4` — 直接合并会发生 entries 键与 uid 冲突 (规则 `9.1`)
- `role/rosamund-hale/rosamund-quick-replies.json:205-206` — Quick Reply 硬编码旧核心案件世界书名称 (规则 `6.3`)
- `role/rosamund-hale/rosamund-quick-replies.json:225` — 结案历史注入无上限增长 (规则 `3.15`)
- `role/rosamund-hale/rosamund-quick-replies.json:149,225` — 长案件缺少持久化的活动案件状态账本 (规则 `4.17`)
- `role/rosamund-hale/rosamund-quick-replies.json:187,206,225,339,358` — 关键状态更新不是事务式或可恢复的 (规则 `4.24`)
- `role/rosamund-hale/README.md:204-210` — 缺少旧聊天迁移、导出和注入重建流程 (规则 `6.2`)
- `role/rosamund-hale/rosamund-quick-replies.json:206` — 核心案件使用模糊查找但未核对返回身份 (规则 `4.13`)
- `role/rosamund-hale/rosamund-quick-replies.json:206,225` — 动态标题与核心案件共用完成状态命名空间 (规则 `4.17`)
- `role/rosamund-hale/README.md:204-221` — 尚未完成真实 SillyTavern 导入和按钮烟测 (规则 `6.3`)

预估工时: **5.0 h**

### Minor · 可协商
- `role/rosamund-hale/rosamund-quick-replies.json:299-301` — 剧情阶段存在两个独立权威来源 (规则 `4.24`)
- `role/rosamund-hale/rosamund-quick-replies.json:205-206` — 案件目录和阶段映射多处重复且无生成校验 (规则 `7.9`)
- `role/rosamund-hale/rosamund-quick-replies.json:9-370` — 19 个 Quick Reply 全部常驻显示 (规则 `5.1`)

预估工时: **0.8 h**

---

*CONFIDENTIAL · Thundersoft · Code Review Skill · 生成时间 2026-08-24 16:31*
