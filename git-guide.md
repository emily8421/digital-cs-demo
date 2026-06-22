# Git 使用说明

本项目（及所有派生自 `ai-project-template` 的项目）的 git 工作流。模板变更治理见 `CONTRIBUTING.md`。

## 1. 账号体系

- **主账号 `emily8421`**：模板仓库 `emily8421/ai-project-template` 与各派生项目（如 `emily8421/LUMEN-DEMO`）都在此账号下。日常推送用它。
- **次账号 `emilymmhere`**：备用 / 历史账号。
- 多账号切换用 gh：

  ```
  gh auth login             # 添加账号（网页或 token）
  gh auth status            # 查看已登录账号与活跃账号
  gh auth switch -u <账号>  # 切换活跃账号
  ```

- **提交身份**：commit 作者按 `git config user.name/user.email`（本项目为 `mmemily <maixh2012@gmail.com>`）。只要该邮箱在 GitHub 账号上验证过，提交会自动归属该账号——换账号不必改 git 身份。

> ⚠️ `emilymmhere` 用的是 classic PAT（`ghp_`），权限在创建时固定，`gh auth refresh` 无法给它追加权限（如 `delete_repo`）。需要高危权限时用网页流程重登或新建带相应权限的 PAT。`emily8421` 是网页 OAuth 登录（`gho_`），可随时 refresh 追加 scope。

## 2. 起新项目（复制模板 + 入 git）

**手动**：

```
git init -b main
gh repo create emily8421/<项目名> --private --source=. --remote=origin
git add -A && git commit -m "init: <项目名>"
git push -u origin main
```

**自动**：`bash scripts/new-project.sh <项目名>` 一步完成「取模板 + git init + 建库 + 首提交 + 推送」。默认从 GitHub `main` 派生（事实来源）；加 `--local` 改走本地模板（需自行确保最新）。详见脚本头部。

> 手动与脚本**等价、派生时任选**——脚本只是把上面的手动步骤自动化。要一条命令就用脚本，要细控或脚本不在手边就手动 clone（两者都从 GitHub `main` 取，正确性一致）。

## 3. 日常提交规范

- **一功能 = 一任务 = 一提交**（见 `ai/global-rules.md` §1.2），禁止一次提交整个系统。
- Commit message 用「完成 XX」式，避免「修改 / update / test」等模糊词；跨模块改动拆成多条（见 `INIT-PROMPT.md` §6）。
- 任何模块开发前先有设计说明再写代码（`global-rules.md` §1.3）。

### 3.1 代码修改完成后的标准流程

完成一次任务后，按以下顺序收尾：

```powershell
git status
git diff
# 运行项目对应验证命令，例如：bash scripts/check-template.sh / npm test / pytest
git add <文件路径>
git commit -m "类型: 简短说明"
git push -u origin <当前分支名>   # 首次推送该分支
gh pr create --fill              # 模板仓库必须走 PR
```

后续同一分支已有 upstream 时，推送可简化为：

```powershell
git push
```

PR 合并后，同步本地 `main` 并清理已合并分支：

```powershell
git switch main
git pull
git branch -d <已合并分支名>
```

常用提交类型：

- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 更新文档
- `chore:` 调整脚本、流程或治理文件
- `refactor:` 重构但不改变行为
- `test:` 增加或修正测试

## 4. 模板变更流程

见 `CONTRIBUTING.md`：模板仓库一律**分支 → PR → 评审 → 合并**，`main` 受分支保护、禁止直推。

派生项目里日常开发是否也走 PR 由项目自行决定；模板仓库强制走 PR。

## 5. 下行同步（模板 → 项目）

派生项目同步模板方法论更新时，优先使用 `scripts/sync-template.sh`，不要手动逐文件复制。该流程是**模板 → 派生项目**的下行获取，不会把派生项目内容提交回模板。

### 5.1 标准操作流程

在派生项目根目录执行：

```powershell
git status
git switch -c chore/sync-template-vX.Y
bash scripts/sync-template.sh --dry-run
```

确认 `--dry-run` 输出只涉及 README「方法论同步」清单中的模板方法论文件，且不会覆盖项目专属内容后，再执行：

```powershell
bash scripts/sync-template.sh --commit
bash scripts/check-template.sh
git status --short --branch
```

如果项目要求走 PR，继续执行：

```powershell
git push -u origin chore/sync-template-vX.Y
gh pr create --fill
```

### 5.2 两条核心命令

```
bash scripts/sync-template.sh --dry-run    # 先看差异
bash scripts/sync-template.sh --commit     # 覆盖并提交 sync template vX.Y
```

### 5.3 注意事项

- 执行前工作区应干净；若 `git status` 显示未提交改动，先提交 / 暂存 / 放弃这些改动，不要混入同步提交。
- `--dry-run` 只预览差异，不修改工作区、不 stage。
- `--commit` 会覆盖同步清单中的文件并自动提交；提交信息通常由脚本生成。
- `README.md` 是项目件，`ai/project-rules.md` 是项目专属规则，默认不应被同步覆盖。
- 同步文件清单见 README「方法论同步」，具体以 `scripts/sync-template.sh` 中的 `SYNC_FILES` 为准。
- 同步后若自检失败，先修复同步造成的不自洽，再 push / PR。
- 老派生项目若执行 `--dry-run` 后出现 staged 改动，说明本地 `scripts/sync-template.sh` 过旧；先恢复工作区，手动用模板最新版覆盖该脚本，再重新执行 `--dry-run`。

## 6. 常见踩坑

| 现象 | 原因 / 处理 |
|---|---|
| push 报 403 / 权限不足 | 活跃账号不对：`gh auth switch -u <目标账号>`；或目标仓库不在该账号下 |
| `gh repo delete` 报 needs delete_repo | classic PAT 无此权限；网页删除，或重登带 `delete_repo` 的 token |
| 提交不归属账号 | commit 邮箱未在该账号验证：GitHub Settings → Emails 添加验证 |
| 两个账号 credential 串 | `git config --global --get credential.helper` 看 GCM；多账号优先用 gh 管理的 credential helper |
| `git push origin main` 被拒（模板仓库） | 预期行为：`main` 受分支保护，改走分支 + PR |

## 7. 命令速查

```
gh auth status                            # 账号总览
gh repo create <acct>/<name> --private    # 建私有仓库
gh pr create / gh pr merge --squash       # 提 / 合 PR
git switch -c <分支>                      # 建并切分支
git push -u origin <分支>                 # 推分支并设上游
bash scripts/new-project.sh <name>        # 一键起新项目
bash scripts/sync-template.sh --dry-run   # 同步预览
```
