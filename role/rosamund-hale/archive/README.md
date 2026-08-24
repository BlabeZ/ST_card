# 归档目录

这里保存发行包运行时不需要的创作与开发资料。普通玩家无需导入本目录中的任何文件。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `creator/rosamund-hale.md` | 含角色身份、事故与主线答案的完整创作者设定 |
| `development/sources/` | 生成完整世界书的六份拆分开发源 |
| `development/build_complete_lorebook.py` | 确定性生成完整世界书和哈希清单的构建器 |
| `development/test_rosamund_package.py` | 角色包结构、状态机和文档契约测试 |
| `development/rosamund-package-manifest.json` | 包版本、源文件及三个安装文件的 SHA-256 清单 |
| `reviews/` | 历史内部评审报告 |

## 开发命令

在角色包根目录运行：

```bash
python3 archive/development/build_complete_lorebook.py
python3 archive/development/test_rosamund_package.py
python3 archive/development/build_complete_lorebook.py --check
```

构建结果仍输出到角色包根目录的 `rosamund-complete-lorebook.json`。完整安装只使用根目录中的角色卡、完整世界书和 Quick Reply。
