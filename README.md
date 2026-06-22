# DigitalCustomerService_Demo（数字客服 · 演示）

> 派生自 [ai-project-template](https://github.com/emily8421/ai-project-template) v1.4。

数字客服 MVP——**群里消息有人接、该跟的已分给该跟的人、经营者收到「今天关注什么」的小结**。
后端编排闭环 + 演示 UI，本机原型（真实通道企业微信 Sprint-0 已核实不成立，待替代方案）。

## 核心能力（P1 已完成）

客户消息进来 → 检索作答 / 未命中请留资+转拍板人 → 经营者收小结：

| REQ | 能力 |
|---|---|
| REQ-1 | 消息接入 + 归一化 + 内置模拟器通道 |
| REQ-2/3 | 知识库 RAG 检索作答（pgvector + BGE via TEI） |
| REQ-4/5/8 | 留资识别（脱敏）+ 转交通知（飞书 webhook）+ 角色路由 |
| REQ-6 | 知识缺口 → 请留资 + 转拍板人 |
| REQ-7 | 定时小结 / 日报 |
| REQ-10/12 | 转人工后 AI 暂停（会话级）+ 非文字如实告知 |

编排决策树：`暂停(handoff_state) → 非文字(告知) → 文本(检索作答/缺口转人)`。演示 UI（`/ui`）可视化全部能力。

## 技术栈

Python + FastAPI · PostgreSQL + pgvector · BGE embedding（Docker TEI，进程内 torch 在 Python 3.14+Windows 不可用，改容器化）· 飞书 webhook（员工通知）· 模拟器通道（客户侧）。

## 快速开始

```bash
docker compose -f docker/docker-compose.yml up -d   # pgvector + TEI
.venv/Scripts/python scripts/seed_knowledge.py       # 知识种子（首次拉模型）
.venv/Scripts/python scripts/seed_staff_routing.py   # staff/routing 种子
.venv/Scripts/python -m uvicorn app.main:app --app-dir backend
```

- **演示 UI**：http://127.0.0.1:8000/ui（聊天窗 + 控制台）
- **API 文档**：http://127.0.0.1:8000/docs（Swagger）
- **一键 Demo**：`.venv/Scripts/python scripts/demo.py`（走通 03 §3 步骤 1-5）

测试（不依赖 Docker，SQLite 内存库）：`pytest -q`（27 passed）。
后端细节见 `backend/README.md`。

## 文档体系

- `docs/00-09` + `docs/design-*.md`：需求 / 架构 / 技术方案 / DB / API / 开发计划 / 验证 + 子系统设计
- `docs/vision/product-vision.md`：产品愿景叙事（工程文档输入）
- `docs/context-and-constraints.md`：背景与选型依据
- `ai/`：AI 行为规范（`global-rules.md` 通用 + `project-rules.md` 项目专属，入口 `ai/index.md`）
- AI 工具入口：`CLAUDE.md` / `AGENTS.md` / `.cursor/`

## 模板关系

派生自 [ai-project-template](https://github.com/emily8421/ai-project-template) v1.4：
- 方法论同步（模板 ⇄ 项目）：见 `CONTRIBUTING.md`、`git-guide.md`、`scripts/sync-template.sh`
- 模板优化提案：`TEMPLATE-UPGRADE-v1.5.md`（`feat/template-upgrade-v1.5` 分支，待回流模板仓库）

## 进度

- ✅ **P1（MVP）完成**（Sprint-1~7，10 REQ 可验证口径通过，27 测试，Demo 1-5 走通）
- ⬜ P2（多轮引导 / 身份披露 / 知识回写 / 时效监控）—— 待升阶段
- ⬜ 愿景（企微替代通道 / 订单进度 / 售后推理）—— 待技术验证

开发计划详见 `docs/08-dev-plan.md`。
