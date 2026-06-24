# 下一步建议（NEXT-STEPS）

> 项目当前状态 + 下一步方向。**新对话打开本文件即可了解「做到哪了 / 下一步做什么」**。
> 项目专属（不参与模板下行同步）；更新时机：每完成一个阶段/里程碑后。

## 当前状态（2026-06-24）

- ✅ **P1（MVP）收官**（2026-06-21）：REQ-1~8/10/12
- ✅ **P2（优化扩展）收官**（2026-06-23）：REQ-9/11/13/14 + 话题级 REQ-10；55 tests passed
- ✅ **打磨完成**：文档一致性 + 2 bug（confirm 作者归属 / 多轮跳过）+ 质量/合规（入库脱敏 / except→logging）+ 复用（write_outbound 提公共）
- ✅ **模板同步 v1.6.9**（含 `check-derived-sync` 派生边界自检脚本）
- ✅ **同步后整理**：docs 分区迁移（design/decisions/research/env）+ 环境约束（`docs/env/local-env.md` + `project-rules §2.5` + 04/05/09 骨架）+ README/project-rules 校准
- **当前交付物＝Demo**（可演示核心价值；非生产 MVP/产品，见 `docs/00-scenario.md` 交付物定位）
- ⏸️ 远期愿景（REQ-15 企微替代通道 / REQ-16 订单 / REQ-17 售后）待技术验证，未启动

## 下一步建议

### 🔵 短期（低成本，立即可做）

**B. 模板提案回流（§9 闭环）** — 推荐
- `_proposals/TEMPLATE-UPGRADE-phasing-v1.6.9.md`（阶段双维度：功能范围 + 交付物形态 Demo/MVP/产品）
- `_proposals/TEMPLATE-UPGRADE-sync-dryrun-direction.md`（sync dry-run 差异方向）
- → 到 `ai-project-template` 开 PR，合并后本项目归档提案到 `_proposals/archive/`

**A. Demo 实演 + 环境确认**
- 扫码跑 `docs/demo-script.md` 全流程（验证打磨 + 整理后无断链、话术准）
- 补 `docs/env/local-env.md` 人工确认项（联网 / 安装依赖 / 公司服务器 / 资源申请口径，见 `ai/project-rules.md` §2.5）

### 🟡 中期（Demo → MVP，需外部条件 + 方向决策）

**D. 愿景前置验证（产品化三件）** — 若目标「能上线」
- **真实通道**：DEC-1 微信客服 1:1 Spike（需企微认证，见 `docs/decisions/open-decisions.md`）
- **飞书启用**：配 `FEISHU_WEBHOOK_URL`（代码就绪 `feishu.py`，差配置；默认只落库不发）
- **LLM 接入**：中转站 GLM-5.2/DeepSeek，RAG 限定内润色（守「不编造」产品红线，见 `docs/design/conversation-engine.md` §2）

**E. 检索质量**（打磨留优化）：category 预筛 / 混合检索（解决 IP67 边界召回，阈值 0.5 margin 薄）

### 🔴 长期（产品 / 愿景）

- **F. REQ-16/17**（订单进度 / 售后推理）—— 依赖外部订单系统 / 高风险 AI，待技术验证
- **G. 代码留优化**：SLA 口径（每条未答，非只最后 inbound）、多轮并发锁、真实 PG 端到端测试覆盖（SQLite 检索 0 覆盖）、OrchestrationResult 工厂 / 转交三件套抽取（打磨批次 4 跳过）

## 推荐路径

**先 B（模板提案回流）+ A（Demo 演练）**——做完这两项，项目（Demo + 方法论）彻底干净；再定方向：产品化（D，需外部条件）还是继续打磨（E/G）。

## 新对话恢复指引

- **分支**：`main`（与 `origin/main` 同步）
- **运行**：后端需重启（上次 uvicorn 进程已停）；启动见 `docs/demo-script.md` §2（`docker compose up -d` + uvicorn，绑 `0.0.0.0:8000`）
- **扫码**：`http://<本机IP>:8000/ui/h5.html`（IP 用 `ipconfig` 查，忽略 `172.28` 虚拟网卡；防火墙放行 8000）
- **待人工确认**：`docs/env/local-env.md`（联网/依赖/服务器）+ 04/05/09 环境章节「待确认」项
- **提案**：`_proposals/` 两提案待回流（见 B）
- **新对话第一步**：先读 `ai/index.md` 列出的规则（`global-rules.md` + `project-rules.md`），再看本文件

---

**追溯**：开发计划 `docs/08-dev-plan.md`；验证 `docs/09-verification.md`；交付物定位 `docs/00-scenario.md`；演示手册 `docs/demo-script.md`；环境 `docs/env/`。
