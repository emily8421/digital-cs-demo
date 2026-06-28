# MAINTAINERS

> Sync notice: This file is maintained by `ai-project-template` and may be overwritten when a derived project syncs template methodology.
> Do not edit it directly in derived projects; propose reusable changes in `_proposals/` and upstream them to the template repository.


本文件面向 `ai-project-template` 模板维护者。普通派生项目使用者优先看 `README.md`、`template-docs/beginner-guide.md`、`template-docs/env-setup.md`、`template-docs/ai-cli-setup.md`、`template-docs/smoke-test.md`、`template-docs/smoke-test-report-template.md`、`SOP.md` 和 `INIT-PROMPT.md`。

## 维护原则

- 模板方法论只在本仓库修改；派生项目发现通用优化时，先在 `_proposals/` 起草，再回流模板仓库。
- 所有模板改动走「提案 → 分支 → PR → 评审 → 合并 → 归档」，不得直推 `main`。
- 模板维护时必须先切维护分支，再开始第一次提交；不得先在本地 `main` 提交后再补建分支。
- 任何影响下游同步判断的合并都必须递增根目录 `VERSION`，并更新 `CHANGELOG.md`。
- 根 `README.md` 保持用户入口轻量；维护细节放本文件，完整版本记录放 `CHANGELOG.md`。

## 发布 Checklist

1. 先确认当前不在 `main` 直接改动；模板维护必须发生在维护分支上。
2. 创建或更新 `TEMPLATE-UPGRADE-*.md` 提案，并在完成后归档到 `_archive/proposals/`。
3. 判断版本影响，更新根目录 `VERSION`。
4. 更新 `CHANGELOG.md`，确保包含当前 `VERSION`。
5. 若新增 / 删除下行同步方法论文件，更新 `template-sync.json`；若改动 `docs/00-09` 撰写规范，确认 `check-template.sh` 的 `_scaffold` 镜像自检（`require_scaffold_mirror`）通过。
6. 若改变用户入口，保持 `README.md` 的 5 分钟路径可读，不塞入维护者细节。
7. 运行：`git diff --check`。
8. 运行：`powershell -ExecutionPolicy Bypass -File scripts/check-template.ps1`。
9. push 分支并创建 PR，等待 GitHub Actions `Template Check` 通过后再合并。

## 提案组织建议

- 若模板修改来自 `_proposals/` 中现有提案，优先沿用原提案并在 PR 中处理完成后归档。
- 若模板修改来自人工在当前会话中陆续提出的建议，应在本轮维护分支里同步维护一份 `TEMPLATE-UPGRADE-*.md` 作为记录。
- 同一轮目标、同一条 PR、同一版本窗口内的多条新增建议，优先合并进同一份提案，而不是机械地“一条建议一份提案”。
- 只有当建议明显属于不同主题、不同版本节奏或不同 PR 时，才拆成多份提案。
- 提案应在修改过程中持续补充，不要全部改完后再统一回忆补写。

## 下行同步清单

`template-sync.json` 是下行同步清单的事实来源，`scripts/sync-template.sh` 会优先读取它。

维护规则：

- 只放跨项目复用的方法论文件。
- 不放项目专属内容，例如 `ai/project-rules.md`、根 `README.md`、`docs/` 业务文档或业务代码。
- 同步 Markdown 文件必须在顶部包含 `Sync notice`，说明派生项目同步时可能被覆盖，不建议直接修改。
- 派生项目根 `README.md` 是项目专属文档，不参与模板下行同步；它由 `scripts/new-project.sh` 初始化生成，后续由项目自行维护。
- 新增方法论入口、脚本、规则文件时，必须同时更新 `template-sync.json` 和自检断言。
- 新增新手环境准备脚本或安装说明时，必须同时检查 `README.md`、`template-docs/` 下对应文档与 `SOP.md` 的入口是否一致。
- 删除同步文件时，必须确认派生项目旧版本同步脚本不会因此失败。
- `scripts/check-template.sh` / `scripts/check-template.ps1` 只用于模板仓库完整性自检；派生项目同步验收使用 `scripts/check-derived-sync.sh` / `scripts/check-derived-sync.ps1`。
- `NEXT-STEPS.md` 之类的本地续接便签不属于模板方法论文档；应保持本地临时性，并通过 `.gitignore` 排除，不进入同步清单和正式提交。

## 自检与 CI

- 本地自检入口：`powershell -ExecutionPolicy Bypass -File scripts/check-template.ps1`。
- Bash 入口：`bash scripts/check-template.sh`。
- 派生项目同步边界检查入口：`powershell -ExecutionPolicy Bypass -File scripts/check-derived-sync.ps1` 或 `bash scripts/check-derived-sync.sh`。
- CI：`.github/workflows/template-check.yml` 在 PR 和 `main` push 上运行空白检查与模板自检。
- `check-template.sh` 含 `_scaffold` 规范镜像自检（`require_scaffold_mirror`）：在临时派生项目验证下行同步会生成 `docs/_scaffold/00-09`、项目事实 `docs/00-09` 不被覆盖、且 `check-derived-sync` 接受该同步提交。
- 自检可以包含结构性断言，不应过度绑定长文案；新增文案检查时优先选择稳定关键词。
- Windows 下若 PowerShell 无法拉起 Git Bash，`scripts/check-template.ps1` 可以退回到原生结构检查；但 `scripts/check-derived-sync.ps1` 与 `scripts/sync-template.ps1` 仍要求 Git Bash 正常工作。不要继续为这类系统问题堆更多 fallback，优先修本机环境。

## README 边界

`README.md` 只回答三件事：

1. 如何最快启动一个项目。
2. 该去哪个文件继续。
3. 当前模板版本和最近变化。

以下内容不要塞回 README：

- 完整版本历史。
- 发布 checklist。
- 同步清单维护细节。
- 模板治理流程长说明。

## 文档分区维护

`docs/README.md` 是派生项目内文档分区规则。维护该文件时遵守：

- `docs/` 根目录只放 `00-09` 核心文档和 `README.md`。
- 输入类源文档放 `docs/vision/`；尚未归类的原始输入包放 `docs/inputs/`。
- 子系统详细设计放 `docs/design/`。
- 决策记录放 `docs/decisions/`。
- 调研 / 实验 / 运行环境 / 会议记录分别放对应子目录。
- 历史归档放 `docs/archive/`。
- `docs/_scaffold/`（v1.18.0+）是模板 `00-09` 撰写规范的只读镜像，随模板同步刷新，不作为项目事实、不直接驱动开发。
- AI 需要新增文档时，必须先判断文档类型；不确定则先提议路径并等待人工确认。
