# 已处理模板优化提案归档

本目录保存已经处理完成、但仍需保留审计记录的模板优化提案。

## 归档原则

- `_proposals/` 是待处理 / 汇总中的提案收件箱。
- `_archive/proposals/` 是已处理提案的历史记录。
- 提案归档后，模板变更事实仍以根目录 `VERSION`、README 版本记录和 Git 历史为准。
- 归档内容不得作为当前待办事项重复执行；若要再次调整，应创建新的 `TEMPLATE-UPGRADE-*.md` 提案。

## 归档触发

派生项目同步模板方法论后，凡已被模板仓库采纳、并经下行同步到本项目的提案，
按 `ai/global-rules.md` §9 与 SOP 同步流程移入本目录归档。

## 本目录已归档提案

| 本项目提案 | 对应模板落地版本 | 模板仓库归档文件（同名/同主题） | 说明 |
|---|---|---|---|
| `TEMPLATE-UPGRADE-phasing-v1.6.9.md` | v1.7.0 | `TEMPLATE-UPGRADE-v1.7.0-phasing-deliverable.md` | 阶段双维度（功能范围 + 交付物形态）+ vision→文档生成约束；原提议 v1.6.8→v1.6.9，实际落地 v1.7.0 |
| `TEMPLATE-UPGRADE-sync-dryrun-direction.md` | v1.6.3 | `TEMPLATE-UPGRADE-v1.6.3-sync-dry-run-direction.md` | 修正下行同步 dry-run 差异方向，使 `+/-` 对齐同步语义（本地→模板）；不触发版本号 |
| `TEMPLATE-UPGRADE-v1.5.md`（+ `-patch`） | v1.5 | `TEMPLATE-UPGRADE-v1.5.md` | v1.5 模板优化（历史，早期回流） |
| `TEMPLATE-UPGRADE-v1.6.md`（+ `-patch`） | v1.6 | `TEMPLATE-UPGRADE-v1.6.md` | v1.6 模板优化（历史，早期回流） |
| `TEMPLATE-UPGRADE-cross-cutting-consistency.md` | v1.8.0 | lifecycle 规则主题（`ai/document-lifecycle-rules.md`） | 文档横切一致性：横切事实单一权威源 SSOT + 引用同步、变更分局部/横切两类、外部文档接入锚定、横切变更后强制一致性验证；4 点全部并入 `ai/document-lifecycle-rules.md` §7（横切事实与权威源）/ §8（外部文档接入规则）/ §9（变更传播规则） |
| `TEMPLATE-UPGRADE-docs-spec-sync.md` | v1.20.0+（`ai/doc-standards/00-09` 规范镜像主路径） | —（模板演进吸收，无同名归档） | 00-09 撰写规范与项目事实分离：模板 docs/00-09 撰写规范镜像至 ai/doc-standards/00-09；docs/_scaffold 方案被替代（git-guide §5.6） |
| `TEMPLATE-UPGRADE-docs-system-audit-prompt.md` | v1.28.0（`ai/prompts/review/16-docs-system-audit.md`） | —（模板演进吸收，无同名归档） | 文档体系同步后审计提示词：对照规范基线回溯审计整条 PLM 链路 |
| `TEMPLATE-UPGRADE-sync-powershell-fallback.md` | v1.57.1 已含（`scripts/sync-template.ps1` 原生 fallback） | —（模板演进吸收，无同名归档） | Git Bash/MSYS 启动失败时 PowerShell 原生 fallback 完成 dry-run / commit / 边界检查 |
> phasing / sync-dryrun 在派生项目同步至模板 v1.7.0 时归档；v1.5 / v1.6 为早期回流的历史提案，已从 `_proposals/archive/` 合并到本目录统一管理（commit 见 git log）。cross-cutting-consistency 在派生项目同步至模板 v1.9.0 时归档（落地版本 v1.8.0）。

## 历史归档位置说明

本项目早期曾用 `_proposals/archive/` 存放已归档提案。模板标准化后，规范归档位置改为
顶层 `_archive/proposals/`（见 `ai/global-rules.md` §9）。历史提案（v1.5、v1.6）
已全部合并到本目录，`_proposals/` 仅保留待处理提案收件箱。
