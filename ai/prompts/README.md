# Prompt Library

> Sync notice: This file is maintained by `ai-project-template` and may be overwritten when a derived project syncs template methodology.
> Do not edit it directly in derived projects; propose reusable changes in `_proposals/` and upstream them to the template repository.

本目录保存可复制给 AI 的 Prompt 模板。`INIT-PROMPT.md` 是轻量索引；完整 Prompt 按场景拆分在本目录下。

## 使用规则

1. 先阅读 `ai/index.md` 列出的规则文件。
2. 按 `INIT-PROMPT.md` 的场景索引选择一个 Prompt 文件。
3. 复制 Prompt 文件中的 `text` 代码块给 AI，并替换其中的项目名、路径、Sprint 编号或输入材料。
4. Prompt 不是需求本身；若输入不足，先补输入或使用 `ai/prompts/docs/01-review-inputs.md` 做入口判定。

## 分类

| 目录 | 用途 |
|---|---|
| `docs/` | 文档体系生成、输入评审、单文档修订、文档反向同步 |
| `dev/` | 单任务开发、Bug 修复、Sprint 验收 |
| `review/` | 项目审查与 docs checklist |
| `planning/` | Phase 升级评估 |
| `setup/` | 环境采集与新建派生项目 |
| `git/` | Commit message 辅助 |
| `maintainers/` | 模板维护、同步和提案汇总 |

> 若是第一次准备机器环境，先看 `template-docs/env-setup.md`，再运行 `scripts/check-prereqs.ps1`；环境准备脚本属于仓库脚本，不属于可复制给 AI 的 Prompt。
