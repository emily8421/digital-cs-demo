# TEMPLATE-UPGRADE-sync-dryrun-direction：sync-template.sh dry-run 差异方向对齐「同步语义」

> **模板优化提案（去项目化）**。按 `CONTRIBUTING.md` §4：派生项目起草 → 模板仓库 PR 落实 → 合并下行同步后归档到 `_proposals/archive/`。
>
> - 起草项目：`digital-cs-demo`。
> - **是否触发版本号：否**（仅 `scripts/sync-template.sh` 改动，不改 `ai/global-rules.md`，按 CONTRIBUTING §7 不递增；故本提案用主题命名而非 `vX.Y`）。
> - 背景：v1.5 已修 dry-run「名不副实」（v1.4 的 dry-run 会 checkout+stage 改写工作区）；本提案修的是 v1.5 dry-run **残留**的「差异方向易误读」。

## 1. 动机

v1.5 `sync-template.sh` dry-run 用 `git diff --stat "$REF" -- "$f"` 显示差异，方向是 **FETCH_HEAD(模板) → worktree(本地)**：

- `+` = 本地有、模板没有（同步后会**丢失**）
- `-` = 模板有、本地没有（同步后会**新增**）

但 dry-run 的语义是「预览同步（用模板覆盖本地）后的变化」，直觉方向应是 **本地(现在) → 模板(同步后)**：`+` = 同步后新增、`-` = 同步后删除。

两者相反，导致 **deletions 多时被误读成「同步会删很多」**，实际却是「模板更全、同步会新增很多」。

**实例（digital-cs-demo，2026-06-22）**：本项目从 v1.4 同步到 v1.5 时，dry-run 显示 `INIT-PROMPT.md 11+/237-`、`git-guide.md 2+/74-` 等大量 deletions。AI 与用户都解读成「模板瘦身重构、同步会删内容」，实际方向相反——模板的这些文件**更大更全**，同步是**扩充**（本项目 INIT-PROMPT 229→455 行等）。最终靠逐文件 `wc -l` 对比才纠正，绕了一大圈。这是「机制可用但易误读」的典型可通用优化点。

## 2. 拟改（去项目化，落在 `scripts/sync-template.sh`）

让 dry-run 的 `+/-` 对齐「同步语义」（`+` = 同步后新增，`-` = 同步后删除）。两种实现，择一：

### 方案 A（推荐）：反转 diff 方向（`-R`）
把 dry-run 的 diff 统计从 `git diff --stat "$REF" -- "$f"` 改为：
```diff
-      git diff --stat "$REF" -- "$f"
+      git diff --stat -R "$REF" -- "$f"
```
`-R` 反转 `+/-`，使输出符合「本地 → 模板（同步后）」方向。改动最小（一个 flag）。

### 方案 B：保留方向 + 加语义标注
不改命令，在 dry-run 输出说明里加一行明确方向：
```
差异方向：模板 → 本地。+ = 本地独有（同步后丢失），- = 模板独有（同步后新增）
```
更保守，但读者仍需脑内换算。

> `git diff --quiet "$REF" -- "$f"`（判断 `=` / `Δ`）只看有无差异，不受方向影响，无需改。

## 3. 版本号

不递增（仅脚本改动，按 CONTRIBUTING §7）。落地后在 CONTRIBUTING §8「变更记录」登记一行（如「sync dry-run 差异方向对齐同步语义」）。

## 4. 影响面

- **所有派生项目**：`sync-template.sh --dry-run` 输出更直观，`+/-` 不再需脑内换算方向。
- **向后兼容**：dry-run 行为不变（仍只读预览、不改工作区不 stage），仅 `+/-` 标签语义对齐同步直觉。

## 5. 落地流程（CONTRIBUTING §4）

1. 本提案在 `digital-cs-demo` `_proposals/` 起草（本文件）。
2. 到 ai-project-template 开分支 `fix/sync-dryrun-direction`，按方案 A（或 B）改 `scripts/sync-template.sh`（改动仅一行）。
3. PR 评审合并（不触发版本号）。
4. 下行同步回派生项目 → 本提案移入 `_proposals/archive/`。

---

> 相关：v1.5 `global-rules.md` §9（模板优化反馈机制）；`CONTRIBUTING.md` §4（上行流程 B）。本提案是该机制的首次实战产出。
