# _proposals/ —— 模板优化提案（派生项目起草区）

本目录起草对 `ai-project-template` 的去项目化优化提案，按 `CONTRIBUTING.md` §4（上行流程 B）回流到模板仓库。

## 结构约定

- **根目录**：未提交 / 待处理的提案（`TEMPLATE-UPGRADE-vX.Y.md` + 可选 `-patch.md`）。新发现的模板优化点起草于此。
- **`archive/`**：已合并并下行同步的提案，**保留作历史记录**（变更事实以「模板版本 vX.Y + git log」为准，提案本身不再驱动开发）。

## 区分依据

提案是否可归档：模板仓库已合并对应改动、并经 `scripts/sync-template.sh` 下行同步到本项目（见 `ai/global-rules.md` 首行「模板版本 vX.Y」）。

## 相关

- 反馈机制：`ai/global-rules.md` §9
- 回流流程：`CONTRIBUTING.md` §4
