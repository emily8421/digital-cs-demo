# 派生项目模板同步运行记录：v1.21.0

## 基本信息

- 项目：DigitalCustomerService_Demo
- 同步日期：2026-06-30
- 同步前模板版本：v1.18.1
- 目标模板版本：v1.21.0
- 同步分支：docs/16-audit-backlog
- 操作入口：自然语言“模板有新的变更，需要同步最新版后再执行文档审计”
- AI 工具 / CLI：Codex CLI

## 执行命令

- dry-run：`scripts/sync-template.ps1 --dry-run` 尝试失败（Git Bash/MSYS `Win32 error 5`）；随后使用 `git fetch --no-tags --depth=1 https://github.com/emily8421/ai-project-template.git main` 与 PowerShell 只读比对预览。
- commit：未执行脚本 `--commit`；因本机 Git Bash 环境阻断，改用 `git restore --source=FETCH_HEAD -- <template-sync files>` + `docs/00-09` → `ai/doc-standards/00-09` 等价同步。
- check-derived-sync：`scripts/check-derived-sync.ps1` 尝试失败（同一 Git Bash/MSYS 问题）；已用内容一致性脚本核对同步文件与 `FETCH_HEAD`。
- post-sync-cleanup：本轮执行同步后整理 + `16-docs-system-audit` 回梳。

## 同步结果

- 是否成功：成功（等价同步；未用官方脚本自动提交）。
- 新增 / 修改的方法论文件：`VERSION`、`CHANGELOG.md`、`ai/session-rules.md`、`ai/commands/*`、`ai/doc-standards/*`、`template-docs/derived-sync-report-template.md` 等 v1.21.0 同步清单文件。
- 项目专属文件是否被误改：未发现模板同步误覆盖 `docs/00-09`；项目文档改动属于后续审计回梳。
- 是否新增 / 刷新 `ai/doc-standards/00-09`：是。
- 是否残留旧 `docs/_scaffold/`：已于同步后整理阶段清理；旧路径仅作为模板文档中的兼容说明保留。

## 遇到的问题

- Git / gh / Git Bash / PowerShell / 网络问题：PowerShell 启动 Git Bash 报 `couldn't create signal pipe, Win32 error 5`；一次 `git fetch` 曾出现 SSL EOF，中途重试后成功。
- 同步脚本问题：脚本依赖 Git Bash，当前本机环境无法直接运行；已按 `git-guide.md` 的边界规则做等价同步和一致性核对。
- Prompt / 快捷命令理解问题：v1.21.0 新增 `ai/commands/` 后，应优先通过 `/run sync-methodology`、`/run docs-system-audit` 路由。
- 文档说明不清：派生项目 README / NEXT-STEPS / 旧提案仍有 v1.18.1 和 `docs/_scaffold` 表述，已在同步后整理中回梳为 `ai/doc-standards` 主路径。
- 派生项目专属冲突：同步前已有未提交审计改动，已保存到 `stash@{0}`；新增输入文件已从 stash 恢复。

## 可优化点归纳

| 问题 | 是否项目专属 | 是否建议回流模板 | 建议提案 |
|---|---|---|---|
| PowerShell 入口在 Git Bash/MSYS Win32 error 5 时只能失败，缺少原生 PowerShell fallback | 否 | 是 | 可起草 `TEMPLATE-UPGRADE-sync-powershell-fallback.md` |
| `docs/_scaffold` 旧路径在派生项目中曾被跟踪，v1.20+ 未给出派生清理策略 | 否 | 可评估 | 可补 post-sync-cleanup 提醒“旧路径是否删除需人工确认” |

## 已生成的回流提案

- 暂未新增；本轮先更新既有 `_proposals/TEMPLATE-UPGRADE-docs-system-audit-prompt.md` 和 `_proposals/TEMPLATE-UPGRADE-docs-spec-sync.md` 的状态 / 路径说明。

## 后续动作

- 是否需要 `/run post-sync-cleanup`：已执行最小整理。
- 是否需要 `/run docs-system-audit`：已执行并回梳结构缺口。
- 是否需要人工清理旧目录：已确认并删除 `docs/_scaffold/`。
- 是否需要同步回模板仓库：如要解决 Git Bash fallback 或旧路径清理策略，可另起去项目化提案。

