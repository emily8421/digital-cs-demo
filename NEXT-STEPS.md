# 下一步建议（NEXT-STEPS）

> 项目当前状态 + 下一步方向。**新对话打开本文件即可了解「做到哪了 / 下一步做什么」**。
> 项目专属（不参与模板下行同步）；更新时机：每完成一个阶段/里程碑后。

## 当前状态（2026-06-25）

- ✅ **P1（Demo）收官**（2026-06-21）：REQ-1~8/10/12
- ✅ **P2（优化扩展）收官**（2026-06-23）：REQ-9/11/13/14 + 话题级 REQ-10；55 tests passed
- ✅ **打磨完成**：文档一致性 + 2 bug（confirm 作者归属 / 多轮跳过）+ 质量/合规（入库脱敏 / except→logging）+ 复用（write_outbound 提公共）
- ✅ **模板同步 v1.7.0**（含 `check-derived-sync` 派生边界自检脚本；阶段双维度 §8.1）
- ✅ **交付物形态迁移**（#15）：project-rules §1 + 03 §3 补双维度/进入退出标准；全 docs MVP→Demo 校正
- ✅ **同步后清理**（#16）：README 版本同步 + 全 docs（含支撑文档）MVP→Demo 一致 + 提案归档合并到 `_archive/proposals/`
- ✅ **Demo 实演验证**（2026-06-25）：后端 + Docker 起好，全 REQ 闭环跑通（作答/留资/缺口转人/多轮/身份/非文字/小结/SLA），健康无断链（详见「Demo 验证记录」）
- ✅ **同步后整理**：docs 分区迁移（design/decisions/research/env）+ 环境约束（`docs/env/local-env.md` + `project-rules §2.5` + 04/05/09 骨架）+ README/project-rules 校准
- **当前交付物＝Demo**（可演示核心价值；非生产 MVP/产品，见 `docs/00-scenario.md` 交付物定位）
- ⏸️ 远期愿景（REQ-15 企微替代通道 / REQ-16 订单 / REQ-17 售后）待技术验证，未启动

## 下一步建议

### 🔵 短期（低成本，立即可做）

**B. 模板提案回流（§9 闭环）** ✅ 已完成（2026-06-25）
- phasing（模板落地 v1.7.0）+ sync-dryrun（v1.6.3）均已回流 ai-project-template，随 v1.7.0 同步并归档至 `_archive/proposals/`（历史 v1.5/v1.6 一并合并）。

**A. Demo 实演 + 环境确认**
- ✅ **Demo 实演已完成**（2026-06-25）：后端 + Docker 起好，`POST /api/v1/messages/simulate` + 管理侧 API 逐条验证全 REQ 闭环通过（见「Demo 验证记录」）。剩手机扫码 UI 演练（可选）。
- ⏳ **环境确认（local-env 9 项待人工拍板）**——建议值见下表，确认后写入 `docs/env/local-env.md`（顺手修 demo-script 两处小发现，一个文档 PR）。

  local-env 9 项建议值（2026-06-25 实跑实测，待人工确认）：

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

**B 已完成；A 的 Demo 实演也已完成（2026-06-25）**，剩 local-env 9 项确认即「彻底干净」；然后定方向：产品化（D，需外部条件）还是继续打磨（E/G）。

## 新对话恢复指引

- **分支**：`main`（与 `origin/main` 同步）
- **运行**：后端**可能仍在后台运行**（uvicorn :8000）；先 `curl localhost:8000/health` 验证——未跑则按 `docs/demo-script.md` §2 起（docker + uvicorn）。
- **扫码**：`http://<本机IP>:8000/ui/h5.html`（IP 用 `ipconfig` 查，忽略 `172.28` 虚拟网卡；防火墙放行 8000）
- **待人工确认**：`docs/env/local-env.md` 9 项（建议值见上「下一步建议 A」表）+ 04/05/09 环境章节「待确认」项
- **提案**：phasing/sync-dryrun 已回流模板并归档至 `_archive/proposals/`（B 完成）；`_proposals/` 仅留未处理提案
- **清理**：旧远程分支 `chore/sync-template-v1.6.8`（会话前遗留）可删：`git push origin --delete chore/sync-template-v1.6.8`
- **新对话第一步**：先读 `ai/index.md` 列出的规则（`global-rules.md` + `project-rules.md`），再看本文件

---

**追溯**：开发计划 `docs/08-dev-plan.md`；验证 `docs/09-verification.md`；交付物定位 `docs/00-scenario.md`；演示手册 `docs/demo-script.md`；环境 `docs/env/`。
