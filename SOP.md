# SOP 索引

> Sync notice: This file is maintained by `ai-project-template` and may be overwritten when a derived project syncs template methodology.
> Do not edit it directly in derived projects; propose reusable changes in `_proposals/` and upstream them to the template repository.

本文件是 `ai-project-template` 的标准操作流程导航。它只回答“当前场景应该看哪里”，不重复完整命令。

## 使用原则

- 操作步骤权威来源：`git-guide.md`。
- 可复制给 AI 执行的 Prompt：`INIT-PROMPT.md` 索引与 `ai/prompts/`。
- 模板治理规则：`CONTRIBUTING.md`。
- 项目快速入口：`README.md`；完整版本记录：`CHANGELOG.md`。

## 场景索引

| 场景 | 权威操作文档 | 可复制 Prompt | 备注 |
|---|---|---|---|
| 新建派生项目 | `git-guide.md` §2 | `ai/prompts/setup/14-new-project.md` | 推荐 `scripts/new-project.sh` 从 GitHub `main` 派生；不要手工复制模板目录 |
| 新项目初始化 docs | `README.md` 快速开始 | `ai/prompts/docs/01-review-inputs.md` / `ai/prompts/docs/00-generate-or-complete-docs.md` | 输入不确定先评审，再生成 / 补齐文档体系 |
| 采集本机环境 | `docs/env/README.md` | `ai/prompts/setup/13-collect-env.md` | 生成 `docs/env/local-env.md`，人工补齐确认项 |
| 执行单个 Sprint / 任务 | `ai/global-rules.md` §3、`docs/08-dev-plan.md` | `ai/prompts/dev/02-run-task.md` | 一个任务只做一个功能，避免跨范围改动 |
| 项目 / 实现审查 | `ai/global-rules.md` §4 | `ai/prompts/review/03-project-review.md` / `ai/prompts/review/10-docs-checklist.md` | 前者用于通用审查；后者用于 docs/03-09 生成后验收 |
| 单文档修订 | `ai/global-rules.md` §8 | `ai/prompts/docs/04-edit-single-doc.md` | 只改目标文档，不顺手扩需求 |
| Bug 修复 | `docs/08-dev-plan.md`、对应任务说明 | `ai/prompts/dev/05-fix-bug.md` | 先定位原因，再做最小修复 |
| 文档反向同步 | `ai/global-rules.md` §1 / §8 | `ai/prompts/docs/07-sync-docs-from-code.md` | 代码事实与 docs 不一致时，先补文档事实 |
| Phase 升级评估 | `docs/03-prd.md`、`ai/project-rules.md` §1 | `ai/prompts/planning/08-phase-upgrade.md` | 评估当前完成度，再草拟下一 Phase 边界 |
| Sprint 验收总结 | `docs/08-dev-plan.md`、`docs/09-verification.md` | `ai/prompts/dev/09-sprint-summary.md` | 对照验收标准总结是否完成 |
| 派生项目同步模板 | `git-guide.md` §5 | `ai/prompts/maintainers/12-sync-template.md` | 先按是否低于 v1.6.8 / 是否缺少 `sync-template.ps1` 判定同步路径；旧项目先用 Bash 入口 bootstrap；根 `README.md` 不参与下行同步；同步后只做派生边界检查，不跑模板自检 |
| 同步后项目整理 | `docs/README.md`、`ai/project-rules.md`、`docs/env/local-env.md` | `ai/prompts/maintainers/15-post-sync-cleanup.md` | 同步方法论后，审计 docs 分区、README、project-rules 与环境约束；先出迁移计划，确认后再执行 |
| 模板优化提案汇总 | `CONTRIBUTING.md` §4、`_proposals/README.md` | `ai/prompts/maintainers/11-template-proposal-summary.md` | 先提案，后改模板；完成后归档到 `_archive/proposals/` |
| 直接修改模板 | `CONTRIBUTING.md` §3 / §7 | `ai/prompts/maintainers/11-template-proposal-summary.md` | 必须判断版本影响并更新 `VERSION` / README 版本记录 |
| 生成提交信息 | `git-guide.md` §3 | `ai/prompts/git/06-commit-message.md` | 基于实际 diff 生成清晰 commit message |

## 常见选择

- “我要开一个新项目” → 先看 `git-guide.md` §2，或复制 `ai/prompts/setup/14-new-project.md`。
- “我要把已有项目同步到最新模板” → 先看 `git-guide.md` §5，复制 `ai/prompts/maintainers/12-sync-template.md`；同步后用 `scripts/check-derived-sync.ps1` 检查边界，再用 `ai/prompts/maintainers/15-post-sync-cleanup.md` 整理项目专属内容。
- “我要让 AI 生成文档体系” → 输入不确定先用 `ai/prompts/docs/01-review-inputs.md`；评审通过后用 `ai/prompts/docs/00-generate-or-complete-docs.md`。
- “我要改模板本身” → 先看 `CONTRIBUTING.md`，先写 `TEMPLATE-UPGRADE-*.md` 提案。