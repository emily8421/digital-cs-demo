# 派生项目模板同步运行记录：digital-cs-demo v1.30.4 → ai-project-template v1.54.2

> 本记录覆盖阶段 2（方法论同步）+ 阶段 3-A（项目自有版本机制启用）+ 阶段 3-B（文档体系审计 + 本报告）。

## 基本信息

- 项目：digital-cs-demo（数字客服 Demo，代号 `dcs`）
- 同步日期：2026-07-18
- 同步前模板版本：v1.30.4（旧单版本语义：VERSION = 继承模板版本）
- 目标模板版本：v1.54.2（跨约 24 个模板版本）
- 项目自身版本（`VERSION`）：v1.30.4 → **v0.1.0**（阶段 3-A 启用项目自有版本）
- 继承版本记录（`TEMPLATE-BASE.md`）：存在；Lineage type：ordinary derived project；当前同步到：v1.54.2；Project version at sync time：v0.1.0
- 同步分支：`chore/sync-template-v1.54.2`（阶段 2）/ `chore/enable-version-mechanism`（阶段 3-A）
- 实际同步提交（非 PR merge commit）：`8d0f1fc sync template v1.54.2 from ai-project-template`（squash 合并 main 为 `5f9030e`，PR #35）
- 版本机制启用提交：`8a27206 feat(governance): 启用项目自有版本机制 v0.1.0`（squash 合并 main 为 `37b64aa`，PR #36）
- 操作入口：`/run sync-methodology`（阶段 2）+ `/run post-sync-cleanup`（阶段 3-A）
- AI 工具 / CLI：Claude Code

## 执行命令

- dry-run：`bash scripts/sync-template.sh --dry-run --preserve-project-version`（§5.2 旧项目首次同步路径，Bash 入口）
- commit：`bash scripts/sync-template.sh --commit --preserve-project-version`
- 版本保留标志：`--preserve-project-version`（普通派生项目；VERSION/CHANGELOG 留在 template-sync.json，靠标志防覆盖）
- check-derived-sync：`powershell -ExecutionPolicy Bypass -File scripts/check-derived-sync.ps1`（对同步提交 `8d0f1fc` EXIT 0，119 文件全在清单）
- post-sync-cleanup：版本机制启用（VERSION + TEMPLATE-BASE + CHANGELOG 顶部重构 + project-rules §2.8 + project-check.yml）
- docs-system-audit（同步后审计）：**轻量执行**（结构完整性 + 抽查；全量 8 维度审计作为后续独立任务）
- 项目验证：本地模拟 project-check.yml 版本一致性逻辑 + git diff --check + CI project-check pass 7s

### 命令真实性记录

| 步骤 | 实际命令 / 动作 | 退出结果 | 是否完整执行 | 是否等价替代 | 是否生成独立报告 | 备注 |
|---|---|---|---|---|---|---|
| dry-run 预览 | `bash scripts/sync-template.sh --dry-run --preserve-project-version` | EXIT=0，119 文件（118 方法论 + TEMPLATE-BASE.md 首次生成） | 是 | 否 | 不适用 | 工具 120s 超时（Windows CRLF 冗长），改 600s+log 重跑确认 |
| commit / 同步 | `bash scripts/sync-template.sh --commit --preserve-project-version` | EXIT=0，commit `8d0f1fc` | 是 | 否 | 不适用 | VERSION 保留 v1.30.4 |
| check-derived-sync | `check-derived-sync.ps1`（对 `8d0f1fc`） | EXIT=0，边界通过；版本机制段 ⚠️ 未启用 | 是 | 否 | 不适用 | 版本机制未启用提示驱动阶段 3-A |
| post-sync-cleanup | 版本机制启用 5 文件（commit `8a27206`） | 双信号 ✓，CI pass 7s | 完整执行 | 否 | 否 | 仿 LUMEN-DEMO#82 |
| docs-system-audit | 结构 + 抽查 | docs/00-09 齐 + 元信息齐 + 分区齐 | **轻量执行** | 否 | 本报告 §文档体系审计摘要 | 全量审计留后续 |
| 项目验证 | project-check CI + 本地一致性模拟 | CI pass 7s | 是 | 否 | 不适用 | 首次 CI 运行 |

## A13 完成判据矩阵

| A13 步骤 | 证据 | 状态 | 若非完成，原因 | 下一步 |
|---|---|---|---|---|
| 标准闭环计划 | 按 12-sync-template SOP 分阶段（评估→同步→版本机制→审计→报告） | 完成 | — | — |
| dry-run 预览 | 119 文件清单 EXIT=0，无项目专属触及 | 完成 | — | — |
| commit + 边界验证 | `8d0f1fc` + check-derived-sync EXIT 0 | 完成 | — | — |
| post-sync-cleanup | 版本机制启用 5 文件，双信号 ✓，CI pass | 完整执行 | — | — |
| docs-system-audit | 结构完整性 + 抽查 | **轻量执行** | 全量 8 维度审计留独立任务 | 需要时跑 `/run docs-system-audit` 全量 |
| 提案回流收口 | 未扫描 `_proposals/` | **部分完成** | 本轮未做提案回流扫描 | 单独扫 `_proposals/` + 模板 issue |
| 同步报告留痕 | 本文件 | 完成 | — | — |

> 依模板规则：存在「轻量执行」「部分完成」项，本次标记为「**同步主链 + 版本机制启用完成，A13 闭环尚有剩余项（全量 docs-audit + 提案回流收口）**」。

## 同步结果

- 是否成功：是（PR #35 merged `5f9030e`）
- 新增 / 修改的方法论文件：118 个（ai/、template-docs/、scripts/、AGENTS/CLAUDE/.cursor、SOP、INIT-PROMPT、CONTRIBUTING、git-guide、docs/README 等）+ 首次生成 TEMPLATE-BASE.md
- `VERSION` / `CHANGELOG.md` 是否保持项目自身版本：阶段 2 保留 v1.30.4（--preserve-project-version）；阶段 3-A 切到项目自有 v0.1.0
- `TEMPLATE-BASE.md` 是否新增继承模板版本：是（v1.54.2，2026-07-18，Project version at sync time v0.1.0）
- 项目专属文件是否被误改：否（check-derived-sync EXIT 0，未触及根 README / project-rules / docs 00-09 / 业务代码）
- 是否新增 / 刷新 `ai/doc-standards/00-09`：是（规范镜像随同步刷新）
- 是否残留旧 `docs/_scaffold/`：否

## 同步后整理摘要

- 是否执行 `/run post-sync-cleanup`：是（阶段 3-A，聚焦版本机制启用）
- README / `ai/project-rules.md` / docs 分区是否需整理：
  - `ai/project-rules.md`：新增 §2.8 项目版本管理（项目专属，不参与同步，手动补）
  - 根 README / docs 分区：轻量审计未见需迁移项（docs/ 结构良好，00-09 + design/env/decisions/inputs/vision/archive 分区齐）
- 已处理项：版本机制双信号启用（project-check.yml + project-rules §2.8）、VERSION 切项目自有 v0.1.0、CHANGELOG 顶部重构（项目版本段 + 历史模板同步记录分隔符）
- 待确认项：无阻塞
- 建议回写 / 后续迁移任务：见「后续动作」

## 文档体系审计摘要（轻量执行）

- 是否执行 `/run docs-system-audit` 同步后审计模式：**轻量执行**（结构完整性 + 追溯抽查；非完整 8 维度审计）
- 规范基线缺口：
  - **P2 待核**：`docs/09-verification.md` 的 `TC-` 计数为 0（可能用自定义命名或缺 TC-ID 追溯矩阵）—— 需全量审计对照 `ai/doc-standards/09-verification.md` 核实，不强制逐字重写
- 可接受兼容差异：docs/00-09 为旧版生成（v1.30.x 时期），章节编号风格 / 结构与最新 doc-standards 示例不必逐字对齐（按语义等价 + 最小补齐）
- 项目事实风险：轻量审计未见（全量审计需逐份对照 04/05/06/07 检查架构视图 / COMP-MOD-Flow ID / ADR / 字段契约 / endpoint matrix 等）
- 回梳计划摘要：本轮不回梳；全量 docs-system-audit 作为独立任务，按需触发

## 项目验证建议

- 建议运行的测试 / lint / 文档检查 / 人工验收：
  - project-check.yml CI 已在 PR/push 到 main 自动运行（whitespace + 版本一致性 + sync 边界）
  - 后续版本 bump 时确保 VERSION ↔ CHANGELOG 顶部一致（CI 强制）
- 已执行验证与结果：project-check CI pass 7s（PR #36）；本地版本一致性模拟全过；git diff --check whitespace OK
- 未验证项与原因：项目业务测试 / lint 未运行（本轮聚焦同步 + 版本机制，非业务开发）

## 遇到的问题

- Git / gh / 网络：
  - **受限网络**：本机访问 GitHub git 协议（fetch/push）需走 clash 代理 7897；`gh` 不读 `git http.proxy`，命令需带 `HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897`
  - **dry-run 工具超时**：`sync-template.sh --dry-run` 在 Windows 下因 119 文件逐个 CRLF 警告 + diff-stat 撑出数百行，命中工具 120s 默认超时（非脚本失败，fetch + 文件清单已完整输出）；改用 600s 超时 + log 重定向 + grep 过滤后正常
  - **gh repo view TLS timeout**：预检时一次 GraphQL 调用超时（代理瞬时抖动，非权限问题，重试 / 后续命令均成功）
- 同步脚本问题：
  - **check-derived-sync 对 squash 合并提交误报**：HEAD 为 PR squash merge commit `5f9030e`（subject 带 `(#35)` 后缀）不匹配脚本严格正则 `^sync template v... from ai-project-template$`，报「提交信息不像模板同步提交」；脚本自身提示 HEAD 是 merge commit 时改传实际 sync commit。实际同步内容（119 文件）已对 sync commit `8d0f1fc` EXIT 0 验证，非真实缺陷
- 文档说明不清：无
- 派生项目专属冲突：无

## 可优化点归纳

| 问题 | 是否项目专属 | 是否建议回流模板 | 建议提案 |
|---|---|---|---|
| Windows 下 sync dry-run/commit 输出冗长（CRLF 警告 × 119 文件）致工具超时 | 否（环境） | 是 | `TEMPLATE-UPGRADE-sync-windows-output-noise`：脚本侧抑制 diff 阶段 CRLF 警告，或 git-guide §5.7 / 12-sync-template 提示「Windows 用长超时 + log 重定向」 |
| check-derived-sync 正则不容忍 squash merge `(#N)` 后缀 | 否 | 是 | `TEMPLATE-UPGRADE-check-derived-sync-squash-suffix`：正则放宽为允许可选 ` (#N)` 后缀，避免对合并到 main 的 squash sync commit 误报 |
| check-derived-sync 输出 119 文件列两遍（清单 + 逐文件确认） | 否 | 是（次要） | 成功时只保留计数 + 尾部摘要，失败再展开 |
| dry-run 审查 checklist（项目专属触及 / 版本机制处理 / 变化规模）未沉淀到 prompt | 否 | 是 | 写入 `12-sync-template.md` 或 git-guide §5 |

## 已生成的回流提案

- 本轮未起草正式 `_proposals/TEMPLATE-UPGRADE-*.md`（候选见上表，待单独评估是否回流）

## 提案回流收口

- 本轮未扫描 `_proposals/`（部分完成）。digital-cs-demo 历史回流提案（如 docs-spec-sync / template #36 v1.18.0 _scaffold）需单独核对模板 issue 状态 + 归档。建议作为独立 follow-up。

## 后续动作

- 是否需要 `/run post-sync-cleanup`：已完成版本机制启用；其余整理项（README/docs 分区）轻量审计未见必需
- 是否需要 `/run docs-system-audit`：**全量审计建议作为独立任务**（本轮轻量执行）
- 是否需要按审计结果回梳 `docs/00-09` / `docs/design` / `docs/env`：视全量审计结论；09 的 TC 追溯待核
- 是否需要补项目验证入口：CI 已就位（project-check.yml）；业务测试入口视项目需要
- 是否需要人工清理旧目录：无需（无 _scaffold 残留）
- 是否需要同步回模板仓库：本轮候选回流点见「可优化点归纳」，待评估起草提案
- 分支清理：`chore/sync-template-v1.54.2` + `chore/enable-version-mechanism` 已合并，可删（本地 + 远端）
