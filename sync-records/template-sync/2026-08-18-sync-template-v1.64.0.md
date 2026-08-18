# 派生项目模板同步运行记录：digital-cs-demo → v1.64.0

## 基本信息

- 项目：digital-cs-demo（普通派生项目，主派生 / 提案回流源）
- 同步日期：2026-08-18
- 同步前模板版本：v1.61.4（2026-08-13，PR #39）
- 目标模板版本：v1.64.0
- 项目自身版本（`VERSION`）：v0.1.0（保留不变）
- 继承版本记录（`TEMPLATE-BASE.md`）：存在；Lineage type: ordinary derived project；本次同步到 v1.64.0
- 同步分支：`chore/sync-template-v1.64.0`
- 实际同步提交：`8e53226`（bootstrap）+ `510c2b6`（sync template v1.64.0 from ai-project-template，44 文件 +1418/-139）
- 操作入口：`/run sync-methodology`（模板仓发起模式，registry 路由）
- AI 工具 / CLI：Claude Code（GLM）

## 执行命令

- dry-run：`powershell -ExecutionPolicy Bypass -File scripts/sync-template.ps1 --dry-run`（首次 EXIT=1 提示 bootstrap；bootstrap 后 EXIT=0，无误触）
- bootstrap：`git checkout FETCH_HEAD -- scripts/sync-template.sh` → commit `8e53226`（+6 行）
- commit：`powershell -ExecutionPolicy Bypass -File scripts/sync-template.ps1 --commit --preserve-project-version`（EXIT=0）
- 版本保留标志：`--preserve-project-version`（普通派生）
- check-derived-sync：`powershell -ExecutionPolicy Bypass -File scripts/check-derived-sync.ps1` → ✅ 通过
- post-sync-cleanup：轻量执行（同仓 2026-08-13 轮已做过 CHANGELOG-PLAIN ownership 收口；本轮无新增 project-rules 骨架项、docs/env 已存在、无旧 scaffold 残留，无需整理动作）
- docs-system-audit（同步后审计）：轻量执行（同步范围与 zhiyan 完全同构——同 44 文件模板资产；项目 docs 分区无迁移需求）
- 项目验证建议：CI project-check + 人工抽查 `template-docs/beginner-guide.md` 三层地图可读性

### 命令真实性记录

| 步骤 | 实际命令 / 动作 | 退出结果 | 是否完整执行 | 是否等价替代 | 是否生成独立报告 | 备注 |
|---|---|---|---|---|---|---|
| 预检 A（身份安全） | git status / log / stash / VERSION / TEMPLATE-BASE | pass（工作区干净、无 stash） | 完整 | 否 | 否 | — |
| 预检 B（同步能力） | test -f 精确查询 4 项 | 全 pass | 完整 | 否 | 否 | — |
| fetch + 目标版本 | git fetch --depth=1 → git show FETCH_HEAD:VERSION | v1.64.0 | 完整 | 否 | 否 | — |
| dry-run | sync-template.ps1 --dry-run → sync.log | 首次 EXIT=1（bootstrap），后 EXIT=0 | 完整 | 否 | 否 | log 已清理 |
| dry-run 误触检查 | grep 项目专属文件模式 | 无误触 | 完整 | 否 | 否 | — |
| sync commit | sync-template.ps1 --commit --preserve-project-version | EXIT=0，44 文件 | 完整 | 否 | 否 | — |
| 边界验证 | check-derived-sync.ps1 | ✅ 通过 | 完整 | 否 | 否 | — |

## 同步内容摘要（v1.61.4 → v1.64.0）

与 zhiyan 同轮同步内容一致（同源模板提交）：Web UI 知识核心层（ui-knowledge 4 文件）、OO 建模 overlay 与图表镜像（v1.63.0）、形态裁剪 + 根目录三层地图 + pitfall 存量触发（v1.64.0）、extract-diagrams.mjs、capability-packages 重构、upstream/CHANGELOG*。

## 提案回流收口决策矩阵

| 本地提案 | 模板 issue 或 PR | 远端状态 | 关闭原因或处理结果 | 本地动作建议 |
|---|---|---|---|---|
| `_proposals/` 仅 README.md | 无 | — | — | 无归档动作（历史回流提案已于 2026-08-13 轮归档 3 份） |

## 项目验证建议

1. CI：PR 合并前 project-check workflow 绿（若被账号计费拦截，按 zhiyan/agent-system 同模式处理——转 public 或修计费）。
2. 人工抽查：`docs/README.md` 新分区说明与项目 docs 结构无冲突。
3. 项目业务验证：本轮无业务代码改动，无需跑业务测试。

## 可回流优化点（本次无模板回流提案）

- 无：三仓（agent-system-template / zhiyan / digital-cs-demo）连续命中同一「private 仓 Actions 计费拦截」环境问题，属账号计费状态而非模板方法论缺陷；处置（转 public）已记录在 registry，不形成提案。

## 后续动作

- PR 合并 → main 对齐 → 删分支 → 模板仓 registry 更新（digital-cs-demo 行 → v1.64.0 / Last sync 2026-08-18）。
