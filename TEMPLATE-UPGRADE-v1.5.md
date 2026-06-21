# TEMPLATE-UPGRADE-v1.5：模板易用性——演示决策前置 + 反馈机制可见性

> **模板优化提案（去项目化）**。按 `CONTRIBUTING.md` §4「上行流程 B」：本文件在派生项目起草 → 到【ai-project-template】仓库开 PR 落成实际改动 → 合并下行同步后**从派生项目删除**（改由「模板版本 vX.Y + git log」作变更事实来源）。
>
> - 起草项目：`digital-cs-demo`。
> - 提议版本：模板 **v1.4 → v1.5**（`global-rules.md` 改动，触发版本号；本次含两处 global-rules 改动，合并一次递增）。

## 1. 动机（两点）

### 1.1 演示决策缺口
Demo / 原型项目核心目的是**可演示**。当前 `project-rules.md §3` 只显式决策「持久化 / 对外接口」，**未决策演示形态 / 前端** → `frontend/` 启用被归为「按需」（`global-rules §5`），创建时易遗漏。
**实例**：`digital-cs-demo` P1 全后端、无演示 UI，演示靠 Swagger / 脚本，对非技术受众不直观，需 P1 收官后**事后补** `demo-ui`（本可前置的决策被推迟）。愿景含界面交互词（「页面 / 界面 / 点击 / 手机」）时更易矛盾、埋返工。

### 1.2 反馈机制不可见
「发现模板可优化 → 写 `TEMPLATE-UPGRADE-*.md` 提案」的标准流程**只在 `CONTRIBUTING.md` §4**（治理文档）。但 AI 进派生项目时按 `ai/index.md` **只读 `global-rules.md` + `project-rules.md`（必读规则层）**，不主动读 `CONTRIBUTING` → 发现可通用优化时**不知标准做法**，很可能直接改派生项目里的 `global-rules.md`（正是 §4 明确禁止的版本漂移）。**机制存在但不可见，等于没机制。**

## 2. 拟改（去项目化，落在模板通用层）

### 2.1 `ai/project-rules.md` §3 模板骨架
新增「演示形态」**必填裁剪项**，与「持久化 / 对外接口」并列：
- 选项：**消息通道内交互**（无自建前端，如 IM 机器人）/ **独立 Web 页面** / **移动端** / **CLI** / **不需演示**；
- 该项决定 `frontend/` 是否启用、`docs/04-05` 是否体现前端架构；
- §0「由 AI 填草稿、需人工确认」段同步加此项。

### 2.2 `INIT-PROMPT.md`
- **§0**：生成 `03 §3` 时，据 `project-rules §3` 演示决策推导 `frontend` 启用与否；**解析愿景文档**，若含界面交互词且 §3 标「无前端」，**警告并提示复核**。
- **§1**：读取清单显式含「`project-rules §3` 演示形态」。

### 2.3 `ai/global-rules.md` §5 目录标准
- `frontend/` 启用条件从「按需」改为「**按 `project-rules §3` 演示决策**」；
- 补「演示形态」维度说明：消息通道内交互 → `frontend` 通常不启用；Web / 移动端 → 启用。

### 2.4 `ai/global-rules.md` 新增「模板优化反馈」指示（对应动机 1.2）
在 AI 必读规则层（global-rules，建议新增一节或并入总则）加**一条**，把治理流程提升到工作可见层：
> **模板优化反馈**：本仓库派生自 `ai-project-template`，`ai/global-rules.md` 是模板复用件、**不得在本仓直接改**（会版本漂移、无法审计）。发现可通用优化时，写 `TEMPLATE-UPGRADE-*.md` 提案（去项目化：动机 / 拟改 / 版本 / 影响），按 `CONTRIBUTING.md` §4 到【ai-project-template】仓库开 PR 落实；合并后下行同步、删除提案文档。

一行规则 + 一个指针 → AI 在规则层即知反馈机制，不再直接改派生 `global-rules`。

### 2.5（可选）`_examples/`
补一个「消息通道内交互、`frontend` 不启用」的样例，与现有 `md-notes-frontend`（纯前端）对照，明示两种形态的裁剪差异。

## 3. 版本号
`global-rules.md` 两处内容变更（§5 目录标准 + 新增「模板优化反馈」）→ 递增 **v1.4 → v1.5**（按 `CONTRIBUTING.md` §7，仅 global-rules 内容变更触发版本号；一次递增覆盖本提案全部 global-rules 改动；其余文件改动随 v1.5 登记到 README 版本记录）。

## 4. 影响面
- **新项目**：创建时 `project-rules §3` 多一项演示决策（AI 填草稿 + 人工确认）；`INIT-PROMPT §0/§1` 据此推导前端；`global-rules` 反馈指示让 AI 知「别在派生改模板、写 TEMPLATE-UPGRADE」。
- **现有派生项目**：不受影响（除非主动同步 v1.5）；同步后获得新决策位 + 反馈指示。
- **向后兼容**：不改变既有 `docs/` 骨架编号 / 结构，只**新增决策维度 + 一条规则**。

## 5. 落地流程（CONTRIBUTING.md §4）
1. 本提案在 `digital-cs-demo` 起草（本文件）。
2. 到【ai-project-template】仓库开分支 `feat/template-v1.5-demo-and-feedback`，落实 §2 的实际改动（**落成真实文件改动，不是把提案丢进模板**）。
3. 走 PR 评审、合并（`global-rules.md` 递增 v1.5 + README 版本记录登记）。
4. 下行同步回 `digital-cs-demo`（及其他派生项目）：`bash scripts/sync-template.sh --commit`。
5. **删除本提案文档**（`TEMPLATE-UPGRADE-v1.5.md`），改由「模板版本 v1.5 + git log」作为变更事实来源。

---

> 参考：`CONTRIBUTING.md` §4 示例——LUMEN 的 `TEMPLATE-UPGRADE-v1.4.md` 即按此回流（起草 → PR 合入模板 → 同步后从 LUMEN 移除）。
