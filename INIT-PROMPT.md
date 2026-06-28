# 常用 Prompt 模板索引

> Sync notice: This file is maintained by `ai-project-template` and may be overwritten when a derived project syncs template methodology.
> Do not edit it directly in derived projects; propose reusable changes in `_proposals/` and upstream them to the template repository.

本文件是 Prompt Library 的轻量索引。完整可复制 Prompt 已拆分到 `ai/prompts/`；使用时先按场景打开对应文件，再复制其中的 `text` 代码块给 AI。

## 使用方式总览

1. **先判断入口**：输入材料不确定、只有愿景或小工具描述时，先用 `ai/prompts/docs/01-review-inputs.md` 做生成前评审；评审通过后用 `ai/prompts/docs/00-generate-or-complete-docs.md` 生成 / 补齐文档体系。
2. **再按任务阶段选择**：开发用 `ai/prompts/dev/02-run-task.md`，审查用 `ai/prompts/review/03-project-review.md` / `ai/prompts/review/10-docs-checklist.md`，局部文档变更用 `ai/prompts/docs/04-edit-single-doc.md`，修 Bug 用 `ai/prompts/dev/05-fix-bug.md`。
3. **收尾时使用辅助 Prompt**：提交前可用 `ai/prompts/git/06-commit-message.md`，代码与文档不一致用 `ai/prompts/docs/07-sync-docs-from-code.md`，阶段升级用 `ai/prompts/planning/08-phase-upgrade.md`，Sprint 完成用 `ai/prompts/dev/09-sprint-summary.md`。
4. **模板同步与维护**：新建派生项目用 `ai/prompts/setup/14-new-project.md`，采集本机环境用 `ai/prompts/setup/13-collect-env.md`；派生项目同步模板方法论用 `ai/prompts/maintainers/12-sync-template.md`；同步后整理项目专属内容用 `ai/prompts/maintainers/15-post-sync-cleanup.md`；模板仓库处理 `_proposals/` 时用 `ai/prompts/maintainers/11-template-proposal-summary.md`。

| 当前场景 | Prompt 文件 | 主要目的 |
|---|---|---|
| 需要多入口生成 / 补齐完整 docs | `ai/prompts/docs/00-generate-or-complete-docs.md` | 从愿景、需求、PRD、任务或现有系统输入生成 / 补齐文档体系 |
| 输入材料不确定、要先评审 | `ai/prompts/docs/01-review-inputs.md` | 判断入口模式、文档剖面、生成准备度和缺口 |
| 要实现某个 Sprint / 切换 AI 工具续接 | `ai/prompts/dev/02-run-task.md` | 限定范围执行单任务，避免跨范围改动 |
| 要审查项目或实现是否合规 | `ai/prompts/review/03-project-review.md` | 按需求、架构、技术、DB/API、边界和追溯维度审查 |
| 单独修订一份 docs 文档 | `ai/prompts/docs/04-edit-single-doc.md` | 在规则约束下做局部文档更新 |
| 修复 Bug | `ai/prompts/dev/05-fix-bug.md` | 先定位和提出最小方案，再改代码 |
| 需要生成提交信息 | `ai/prompts/git/06-commit-message.md` | 根据实际改动给出清晰 commit message |
| 代码实现与 docs 不一致 | `ai/prompts/docs/07-sync-docs-from-code.md` | 先把事实差异同步回文档 |
| 准备进入下一 Phase | `ai/prompts/planning/08-phase-upgrade.md` | 评估当前完成度并草拟 Phase 边界更新 |
| Sprint 做完要验收 | `ai/prompts/dev/09-sprint-summary.md` | 对照验收标准总结是否完成 |
| 生成 03-09 后人工验收 | `ai/prompts/review/10-docs-checklist.md` | 在编码前拦住文档空洞、越界和自相矛盾 |
| 模板仓库汇总派生项目提案 | `ai/prompts/maintainers/11-template-proposal-summary.md` | 读取 `_proposals/` 并形成模板优化计划 |
| 派生项目同步模板方法论 | `ai/prompts/maintainers/12-sync-template.md` | 按 SOP 执行 `sync-template.sh` 下行同步并创建 PR |
| 需要采集本机资源约束 | `ai/prompts/setup/13-collect-env.md` | 自动生成 `docs/env/local-env.md` 并补人工确认项 |
| 需要从模板新建派生项目 | `ai/prompts/setup/14-new-project.md` | 调用 `scripts/new-project.sh` 创建项目并完成初始化入口 |
| 同步后整理派生项目 | `ai/prompts/maintainers/15-post-sync-cleanup.md` | 审计 docs 分区、README、project-rules 与运行环境约束，先出迁移计划再执行 |
| 项目成型后回溯审计全链路 | `ai/prompts/review/16-docs-system-audit.md` | 用 document-lifecycle-rules 回溯审视 PLM 链路合理性、可行性与一致性，先出报告不改文件 |

> 原则：Prompt 不是需求本身。AI 只能基于 `docs/`、`ai/document-lifecycle-rules.md`、`ai/project-rules.md` 与人工确认的信息工作；如果输入不足，先补输入，不要让 AI 猜。生成或修改任何项目事实文档前，必须按文档生命周期规则声明上游输入、约束来源、允许修改范围和下游影响。
