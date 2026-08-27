# 归档目录

这里保存发行包运行时不需要的创作与开发资料。普通玩家无需导入本目录中的任何文件；完整安装只使用角色包根目录中的五个玩家文件。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `creator/zhou-heng-marvel-system.md` | 周衡、系统、任务、MCU 与漫画连续性的完整创作规格 |
| `development/sources/` | 生成完整世界书的七份拆分开发源 |
| `development/build_zhou_heng_marvel_system_package.py` | 确定性生成世界书与哈希清单的构建器 |
| `development/test_zhou_heng_marvel_system_package.py` | 角色卡、Persona、骰子协议、内容边界、发行文档和构建契约测试 |
| `development/zhou-heng-marvel-system-package-manifest.json` | 包版本、五个安装文件、七份源文件及 SHA-256 清单 |

`development/sources/` 是开发输入，不是可分别安装的七本扩展世界书。构建器会统一正规化字段、重排 UID，并强制任务档案和故事阶段保持禁用。直接导入拆分源会重复注入常驻规则，并可能让未来阶段或隐藏任务信息在错误时间出现。

## 开发命令

在角色包根目录运行：

```bash
python3 archive/development/build_zhou_heng_marvel_system_package.py
python3 archive/development/test_zhou_heng_marvel_system_package.py
python3 archive/development/build_zhou_heng_marvel_system_package.py --check
```

构建结果输出到根目录的 `zhou-heng-marvel-system-worldbook.json`；清单输出到本目录的 `development/zhou-heng-marvel-system-package-manifest.json`。
