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

> 上述两提案均在派生项目同步至模板 v1.7.0 时归档（commit 见 git log）。

## 备注：与历史 `_proposals/archive/` 的关系

本项目早期使用 `_proposals/archive/` 存放已归档提案（v1.5、v1.6 等）。
模板标准化后，规范归档位置改为顶层 `_archive/proposals/`（见 `ai/global-rules.md` §9）。
历史 `_proposals/archive/` 中的提案可择机合并到本目录统一管理；合并前二者并存，不互相覆盖。
