# 下一步建议（NEXT-STEPS）

> 项目当前状态 + 下一步方向。**新对话打开本文件即可了解「做到哪了 / 下一步做什么」**。
> 项目专属（不参与模板下行同步）；更新时机：每完成一个阶段/里程碑后。

## 当前状态（2026-06-28）

- ✅ **P1（Demo）收官**（2026-06-21）：REQ-1~8/10/12
- ✅ **P2（优化扩展）收官**（2026-06-23）：REQ-9/11/13/14 + 话题级 REQ-10；55 tests passed
- ✅ **打磨完成**：文档一致性 + 2 bug（confirm 作者归属 / 多轮跳过）+ 质量/合规（入库脱敏 / except→logging）+ 复用（write_outbound 提公共）
- ✅ **模板同步 v1.7.0**（含 `check-derived-sync` 派生边界自检脚本；阶段双维度 §8.1）
- ✅ **交付物形态迁移**（#15）：project-rules §1 + 03 §3 补双维度/进入退出标准；全 docs MVP→Demo 校正
- ✅ **同步后清理**（#16）：README 版本同步 + 全 docs（含支撑文档）MVP→Demo 一致 + 提案归档合并到 `_archive/proposals/`
- ✅ **Demo 实演验证**（2026-06-25）：后端 + Docker 起好，全 REQ 闭环跑通（作答/留资/缺口转人/多轮/身份/非文字/小结/SLA），健康无断链（详见「Demo 验证记录」）
- ✅ **同步后整理**：docs 分区迁移（design/decisions/research/env）+ 环境约束（`docs/env/local-env.md` + `project-rules §2.5` + 04/05/09 骨架）+ README/project-rules 校准
- ✅ **环境确认完成**（2026-06-26）：local-env 9 项 + 服务器资源预案写入实测值（`docs/env/local-env.md`）；同步 `project-rules.md` §2.5 三项；修正 demo-script §4.3 缺口造例（换冷门问句，避免被历史回写条目命中）
- ✅ **文档体系诊断 + 横切一致性提案**（2026-06-26）：诊断 sprint-0 回写遗漏 / wxautox4 定性二分裂 / STR-01 孤岛三症状（根因＝缺「横切约束变更回梳」环节）；起草 `_proposals/TEMPLATE-UPGRADE-cross-cutting-consistency.md` 补充提案（PR#20）；STR-01 保命入库（PR#21）
- ✅ **模板同步 v1.9.0**（#24，2026-06-27）：v1.7.0→v1.9.0；新增 `ai/document-lifecycle-rules.md`（v1.8.0 横切一致性/变更传播/外部文档接入）+ Prompt Library 拆分（v1.9.0，INIT-PROMPT 改索引）；cross-cutting-consistency 提案已被 v1.8.0 采纳并归档至 `_archive/proposals/`
- ✅ **模板同步 v1.18.1**（#29，2026-06-28）：v1.9.0→v1.18.1；新增 `docs/_scaffold/` 规范镜像 + `template-docs/` 新手文档 + `16-docs-system-audit` 提示词 + `check-prereqs`/`bootstrap-dev-env` 脚本；15-cleanup 审计确认 docs 结构 / env / project-rules 全合规，仅刷新版本号
- ✅ **同步后整理**（#25，2026-06-27）：`demo-script.md` 移出 docs/ 根 + 5 处链接更新 + README 版本号/版块校准 + 05 §4 编号修复 + project-rules 引用更新；业务代码零改动
- **当前交付物＝Demo**（可演示核心价值；非生产 MVP/产品，见 `docs/00-scenario.md` 交付物定位）
- ⏸️ 远期愿景（REQ-15 企微替代通道 / REQ-16 订单 / REQ-17 售后）待技术验证，未启动

## 下一步建议

### 🔵 短期（低成本，立即可做）

**B. 模板提案回流（§9 闭环）** ✅ 已完成（2026-06-25）
- phasing（模板落地 v1.7.0）+ sync-dryrun（v1.6.3）均已回流 ai-project-template，随 v1.7.0 同步并归档至 `_archive/proposals/`（历史 v1.5/v1.6 一并合并）。

**A. Demo 实演 + 环境确认** ✅ 已完成（2026-06-26）
- ✅ **Demo 实演已完成**（2026-06-25）：后端 + Docker 起好，`POST /api/v1/messages/simulate` + 管理侧 API 逐条验证全 REQ 闭环通过（见「Demo 验证记录」）。剩手机扫码 UI 演练（可选）。
- ✅ **环境确认已完成**（2026-06-26）：local-env 9 项 + 服务器资源预案写入实测值（`docs/env/local-env.md`）；同步 `project-rules.md` §2.5 三项；修正 demo-script §4.3 缺口造例（换冷门问句，避免被历史回写条目命中）。**短期已彻底干净。**

  local-env 9 项建议值（2026-06-25 实跑实测，已确认写入 `docs/env/local-env.md`）：

  | 项 | 建议值 | 依据 |
  |---|---|---|
  | 最大内存 | ≤ 1 GB | 实测 PG 31M + TEI 161M + uvicorn ~150M |
  | 最大显存 | 0（Demo 不用 GPU） | TEI 用 cpu-1.6 镜像，纯 CPU 推理 |
  | 最大磁盘 | ≤ 3 GB | 镜像 2.1G（pgvector 621M+pg 642M+TEI 914M）+ PG 数据 + BGE 模型 |
  | 联网外部 API | Demo 不联网 | 作答＝本地检索；LLM/飞书/真实通道属 MVP |
  | 装新依赖/镜像 | 允许（已装齐） | Docker + .venv 就绪；新依赖须先确认（§2.2） |
  | 公司服务器 | Demo 不需要 | 本机先行；服务器属 MVP/部署（05 §1） |
  | 公司/隐私数据 | 不涉及 | 全虚构演示数据；留资脱敏已实现 |
  | 本机必须跑通 | 后端 + Docker(PG pgvector+TEI) + 模拟器；8 类 REQ（已验证） | 本次实跑 |
  | 可 Mock/远程 | TEI 不可用→编排跳过检索；单测用 SQLite 内存库 | orchestrator 现状 |

**C. 文档体系一致性修复** ✅ 已完成（2026-06-27）
- 全链路回溯审计 + 三症状回梳（横切事实 SSOT 引用同步）：
  - 症状一（REQ-15 措辞）：`01:72` / `03:34` / `vision:19` / `vision:240`「先验后接/待验证」→「已核实不成立」（权威源 sprint-0-findings）
  - 症状二（wxautox4）：`project-rules:48/66` / `03:95` / `05:34` / `04:100`「永久禁止」→「商用永久禁止 + 非商用验证例外（DEC-7）」
  - 症状三（STR-01）：加 §8 锚定 + 命名冲突澄清，迁 `docs/vision/` → `docs/decisions/`
- 全链路审计结论：链路主干强健（无悬空 ID、可行性有降级、交付物形态一致），三症状为唯一实质待修项，未发现 C 之外的重大断裂。
- **审计新发现（C 之外·小缺口·非阻塞·择机）**：
  - 检索相似度阈值「待确认」未给默认值（`knowledge-base`/`05 §1`；demo-script §6 已记 0.5 margin 薄）→ 并入 E 检索质量
  - SLA scan（REQ-14）依赖部署层 cron，Demo 本机是否配 cron 未在任何文档说明（手动触发可行）→ demo-script/08 补一句
  - 08-dev-plan 未逐 Sprint 核对 Sprint→REQ→验收（本次基于 grep+09+06/07 交叉推断）→ 单独逐 Sprint 核对

### 🟡 中期（Demo → MVP，需外部条件 + 方向决策）

**D. 愿景前置验证（产品化三件）** — 若目标「能上线」
- **真实通道**：DEC-1 微信客服 1:1 Spike（需企微认证，见 `docs/decisions/open-decisions.md`）
- **飞书启用**：配 `FEISHU_WEBHOOK_URL`（代码就绪 `feishu.py`，差配置；默认只落库不发）
- **LLM 接入**：中转站 GLM-5.2/DeepSeek，RAG 限定内润色（守「不编造」产品红线，见 `docs/design/conversation-engine.md` §2）

**E. 检索质量**（打磨留优化）：category 预筛 / 混合检索（解决 IP67 边界召回，阈值 0.5 margin 薄）

### 🔴 长期（产品 / 愿景）

- **F. REQ-16/17**（订单进度 / 售后推理）—— 依赖外部订单系统 / 高风险 AI，待技术验证
- **G. 代码留优化**：SLA 口径（每条未答，非只最后 inbound）、多轮并发锁、真实 PG 端到端测试覆盖（SQLite 检索 0 覆盖）、OrchestrationResult 工厂 / 转交三件套抽取（打磨批次 4 跳过）

## Demo 验证记录（2026-06-25）

- 后端起法：`docker compose -f docker/docker-compose.yml up -d` + `.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000`；`curl localhost:8000/health` → `{"status":"ok"}`。
- 入口 API：`POST /api/v1/messages/simulate`（body: `external_group_id`/`sender_external_id`/`content_type`/`content_text`）；管理侧 `POST /api/v1/summaries/daily`、`POST /api/v1/sla/scan`、`GET /api/v1/knowledge/gaps`。
- 全 REQ 闭环通过：知识问答(2/3)、留资(4)、缺口转人(6)、多轮(9 颜色→数量→Logo)、身份(11)、非文字(12)、经营者小结(7)、SLA(14)。
- 两处小发现（待修 demo-script）：① §4.3 用「今天天气怎么样」造缺口，现被 KB「灯饰客服不查天气」消歧条目 **hit**，应换冷门问题（已用「能帮我写一首关于月亮的诗吗」验证缺口路径正常：gap_id+handoff_id+notif 全生成）；② Windows 控制台中文 GBK 乱码（§6 已知，仅显示，存储 UTF-8 正确）。

## 推荐路径

**B、A、模板同步 v1.9.0→v1.18.1、同步后整理、C 文档体系一致性修复均已完成（2026-06-28）**，短期「彻底干净」。下一步两条线：① 处理审计小缺口（检索阈值/SLA cron/08 核对）+ 沉淀审计提示词提案；② 定方向：产品化（D，需外部条件）还是继续打磨（E/G）。

## 新对话恢复指引

- **分支**：`main`（与 `origin/main` 同步）
- **运行**：后端**可能仍在后台运行**（uvicorn :8000）；先 `curl localhost:8000/health` 验证——未跑则按 `demo-script.md` §2 起（docker + uvicorn）。
- **扫码**：`http://<本机IP>:8000/ui/h5.html`（IP 用 `ipconfig` 查，忽略 `172.28` 虚拟网卡；防火墙放行 8000）
- **环境确认**：`docs/env/local-env.md` 9 项已确认（2026-06-26）；剩 04/05/09 环境章节零散「待确认」项（属中期整理，非阻塞）
- **提案**：phasing/sync-dryrun/cross-cutting-consistency 均已回流模板并归档至 `_archive/proposals/`（cross-cutting-consistency 被模板 v1.8.0 采纳，落地于 `ai/document-lifecycle-rules.md`）；`_proposals/` 现仅留收件箱说明
- **STR-01**：外部策略文档已锚定（§8 锚定 + 命名冲突澄清）并迁移至 `docs/decisions/`（按 §8.4 策略决策类）；PR#21 入库，C 回梳补锚定/分区
- **清理**：旧分支 `chore/sync-template-v1.6.8`、`demo_verify*.txt` 已清（2026-06-26）
- **新对话第一步**：先读 `ai/index.md` 列出的规则（`global-rules.md` + `project-rules.md`），再看本文件

---

**追溯**：开发计划 `docs/08-dev-plan.md`；验证 `docs/09-verification.md`；交付物定位 `docs/00-scenario.md`；演示手册 `demo-script.md`；环境 `docs/env/`。
