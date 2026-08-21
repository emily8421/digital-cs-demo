# 派生项目模板同步运行记录：digital-cs-demo → v1.67.0

## 基本信息

- 项目：digital-cs-demo（普通派生项目，主派生 / 提案回流源）
- 同步日期：2026-08-22
- 同步前模板版本：v1.64.0（2026-08-18，PR #40）
- 目标模板版本：v1.67.0
- 项目自身版本（`VERSION`）：v0.1.0（保留不变）
- 继承版本记录（`TEMPLATE-BASE.md`）：存在；Lineage type: ordinary derived project；本次同步到 v1.67.0
- 同步分支：`chore/sync-template-v1.67.0`
- 实际同步提交：`6193e47`（bootstrap .sh）+ `1c63196`（bootstrap .ps1）+ `e6afae0`（sync template v1.67.0 from ai-project-template，145 文件）+ `699d820`（post-sync-cleanup 清理 24 件残留）
- 操作入口：`/run sync-methodology`（模板仓发起模式，registry 路由）
- AI 工具 / CLI：Claude Code（deepseek-v4-flash）

## 执行命令

- dry-run：`powershell -ExecutionPolicy Bypass -File scripts/sync-template.ps1 --dry-run`（首次 EXIT=1 提示 bootstrap；bootstrap 后 EXIT=0，无误触）
- bootstrap：`git checkout FETCH_HEAD -- scripts/sync-template.sh` → commit `6193e47`；`scripts/sync-template.ps1` 亦落后 → commit `1c63196`
- commit：`powershell -ExecutionPolicy Bypass -File scripts/sync-template.ps1 --commit --preserve-project-version`（EXIT=0，145 文件）
- 版本保留标志：`--preserve-project-version`（普通派生）
- check-derived-sync：`powershell -ExecutionPolicy Bypass -File scripts/check-derived-sync.ps1 e6afae0` → ✅ 通过（145 文件全合规）
- post-sync-cleanup：完整执行三项残留审计——4a 脚本残留 5 件（check-template.sh/.ps1、sync-all-derived.sh、e2e-sync-check.sh、new-project.sh）、4b template-docs 模板仓/领域专用文档 4 件（e2e-regression-checklist、e2e-report-template、rd-data-chain、domain-derived-scenarios-template）、4c template-docs 根下旧路径残留 15 件（迁往 profiles//templates/ 的新件已在）；全部删除（commit `699d820`），引用核查无破坏（check-derived-sync 中仅为文本提示）
- docs-system-audit（同步后审计）：轻量执行（docs/ 结构合规——根仅 README + 00-09 + 标准子目录；docs/env/local-env.md 存在；workflow 仅 project-check.yml；无 template-check.yml 残留）
- 项目验证建议：CI project-check + 人工抽查 `docs/README.md` 分区与 docs 结构一致性

### 命令真实性记录

| 步骤 | 实际命令 / 动作 | 退出结果 | 是否完整执行 | 是否等价替代 | 是否生成独立报告 | 备注 |
|---|---|---|---|---|---|---|
| 预检 A（身份安全） | git status / log / stash / VERSION / TEMPLATE-BASE | pass（工作区干净、无 stash） | 完整 | 否 | 否 | — |
| 预检 B（同步能力） | test -f 精确查询 5 项 | 全 pass | 完整 | 否 | 否 | — |
| fetch + 目标版本 | git fetch --depth=1 → git show FETCH_HEAD:VERSION | v1.67.0 | 完整 | 否 | 否 | — |
| dry-run | sync-template.ps1 --dry-run → sync.log | 首次 EXIT=1（bootstrap），后 EXIT=0 | 完整 | 否 | 否 | log 已清理 |
| dry-run 误触检查 | grep 项目专属文件模式 | 无误触 | 完整 | 否 | 否 | — |
| sync commit | sync-template.ps1 --commit --preserve-project-version | EXIT=0，145 文件 | 完整 | 否 | 否 | — |
| 边界验证 | check-derived-sync.ps1 e6afae0 | ✅ 通过 | 完整 | 否 | 否 | — |
| post-sync-cleanup | 三项残留审计 + 删除 | 24 件删除（699d820） | 完整执行 | 否 | 否 | 迁移计划经用户确认 |
| docs-system-audit | docs 结构 / env / workflow 只读核查 | 合规 | 轻量执行 | 否 | 否 | 深度审计留后续 |

## 同步内容摘要（v1.64.0 → v1.67.0）

跨版本携带 v1.65.0（脚本边界：模板仓专用脚本移出同步清单）+ v1.66.0（template-docs 重组为 profiles//templates//maintainer/ 三区；project/ 与 _governance/ 容器未下行至派生）+ v1.67.0（workspace project-container 实施，含治理归拢 _governance/）。本轮同步 145 文件：ai 规则 / ai/commands / ai/prompts / ai/doc-standards 全量刷新、template-docs 新三区结构、scripts（check-derived-sync.*、check-github-context、collect-env、check-prereqs、check-runtime、bootstrap-dev-env、check-markdown-clean）、SOP / INIT-PROMPT / CONTRIBUTING / git-guide、docs/README + docs/inputs/README、upstream/CHANGELOG* 镜像、TEMPLATE-BASE.md 继承记录。

## 提案回流收口决策矩阵

| 本地提案 | 模板 issue 或 PR | 远端状态 | 关闭原因或处理结果 | 本地动作建议 |
|---|---|---|---|---|
| `_proposals/` 仅 README.md | 无 | — | — | 无归档动作（历史回流提案已归档；本轮无新提案） |

## 项目验证建议

1. CI：PR 合并前 project-check workflow 绿。
2. 人工抽查：`docs/README.md` 分区说明与项目 docs 结构无冲突；`template-docs/` 新三区（profiles//templates/）可读性。
3. 项目业务验证：本轮无业务代码改动，无需跑业务测试。

## 待确认 / 后续动作

- 根 `CHANGELOG-PLAIN.md` 顶部仍为模板内容（v1.56.13，与 VERSION v0.1.0 不一致）：v1.67.0 起同步保留不覆盖；需改写为项目自有大白话 changelog（内容决策，未在本轮处理）。
- PR 合并 → main 对齐 → 删分支 → 模板仓 registry 更新（digital-cs-demo 行 → v1.67.0 / Last sync 2026-08-22）。
