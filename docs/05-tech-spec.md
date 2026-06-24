# 05 技术方案

> AI 生成初稿，**人工确认**。技术栈 + 关键决策；版本「待确认」处为草稿，不杜撰精确版本号。按 global-rules §8 积累式演进。

## 1. 技术栈与版本

| 类别 | 选型 | 版本 | 阶段 | 备注 |
|---|---|---|---|---|
| 后端语言/框架 | Python + FastAPI | 待确认 | P1 | Python 是团队较熟语言；FastAPI 适合 Webhook + REST |
| 数据库 | PostgreSQL | 待确认 | P1 | 关系型承载会话/留资/转交/缺口/知识元数据 |
| 向量检索/RAG | **pgvector**（pgvector/pgvector:pg16，向量列 `vector(512)`） | pg16 | P1 | 据背景约束选定，免独立向量引擎 |
| LLM（对话生成） | **Demo 未启用**（中转站 GLM-5.2/DeepSeek 候选） | n/a | Demo | 作答＝检索 answer 原文直回（保「不编造」红线）；未来可在 RAG 限定内引入 LLM 润色/措辞；embedding 另见下行 |
| Embedding | **本地 BGE via Docker TEI**（bge-small-zh-v1.5，512 维） | — | P1 | Sprint-2 定；Python 3.14+Windows 进程内 torch 失败改 TEI（见 context-and-constraints §3） |
| 消息平台（客户侧） | 企业微信开放 API | n/a | 愿景·待验证 | 群内自动回复 Sprint-0 已核实不成立；**当前企业微信未认证→真实通道需先认证**（见背景约束） |
| 员工通知出站 | **飞书机器人**（custom robot webhook）— 代码已实现·**默认关闭** | — | P1 | webhook 代码有（`feishu.py`）；`FEISHU_WEBHOOK_URL` 空→只落 `Notification` 库不发（demo）；配 URL 即发 |
| 任务调度 | **外部 cron**（应用不内嵌） | — | P1 | 定时小结；应用只提供 `POST /summaries/daily` 接口，定时由部署层 cron/systemd/k8s 调用（Sprint-6 定，少组件、生产更稳） |
| 部署 | **本机原型**（Docker Desktop / 本地 Python）；公司 Linux 服务器＝后续 | 待确认 | P1 | 据背景约束：本机先跑通，公司服务器后续 |
| 测试 | pytest（待确认） | 待确认 | P1 | tests/ 目录 |

> 选型依据＝`docs/env/context-and-constraints.md`。已收敛：pgvector（pg16）/ 本机原型部署 / 飞书通知 / 对话经中转站（GLM-5.2/DeepSeek）/ **embedding＝本地 BGE via Docker TEI**（Sprint-2 定）。**待补**：各组件精确版本号。

## 2. 关键技术决策

- **同步 Webhook + 异步出站分离**：入站 Webhook 快速 ACK（避免平台超时重试），重处理（检索/LLM/通知）走任务化异步执行；保证回调不阻塞、消息不丢。
- **通道抽象优先**：定义统一「归一化消息」内部契约，企业微信/模拟器各自实现适配；业务逻辑只依赖契约，不感知平台（→ `design/channel-adapter.md`）。这是抵御 ⚠️ 平台风险的核心决策。
- **单轮 RAG 为主，编排驱动分支**：P1 主路径＝检索→作答；编排器在「未命中」时切到缺口/留资/转交分支，而非让 LLM 自由发挥，确保不编造。
- **留资/缺口结构化优先于自然语言解析**：手机号等用可校验模式抽取并脱敏存储；缺口问题原文留存供拍板人确认。
- **通知为消息、非系统**：员工/经营者提醒与小结都经出站通道发为普通消息，P1 不引入**功能**前端会话（与愿景一致）；P1/P2 收官后补**演示交互界面**（`/ui` PC 控制台 + `/ui/h5.html` 客户 H5 + `/ui/confirm.html` 知识确认，演示工具）不改此原则。
- **LLM 可控性**：作答限定在检索到的知识范围内（带来源/置信度），未命中不生成参数；为 P2 多轮与 P-愿景售后推理留可控接口。

## 3. Phase 技术约束（与 project-rules §1、§2 一致）

- **P1 允许**：Python/FastAPI、PostgreSQL、RAG、通道抽象+模拟器、定时任务、内部管理 API、Docker。
- **P1 禁止**：多轮状态机、售后推理、知识回写、非文字**内容**理解（类型识别+如实告知已 P1）、订单系统集成、企业微信客户群群内自动回复（Sprint-0 已核实不成立）、个人微信非官方自动化（永久）。
- **P2 解锁**：多轮引导、身份披露、知识回写、时效监控、转人工暂停的话题级精化；企业微信正式接入（若选定合规通道）。
- **愿景·待技术验证**：企业微信外部群能力（REQ-15）、订单系统集成（REQ-16）、售后规则推理（REQ-17）。

## 4. 编码约定

详见 `ai/project-rules.md` §5。该节当前为「待 03-09 审核后回填」占位草稿；本文不重复、不虚构。
待 project-rules §5 确认后，本节仅保留一行指针指向它，不在两处维护。

## 4. 运行环境与资源评估

> 本机 Demo 可行性见 `docs/env/local-env.md`（Win11/i7-12650H/32GB/RTX3050）；资源约束见 `docs/env/context-and-constraints.md`。
- **资源瓶颈**：Python 3.14+Windows 进程内 torch DLL 失败 → Docker TEI（见 `docs/env/context-and-constraints.md` §3）
- **降级/Mock**：TEI 不可用→编排跳过检索（`try/except + logging.warning`）；SQLite 内存库用于单测（不依赖 Docker）
- **服务器预案**：**待确认**（公司 Linux 服务器资源/部署方式；本机原型先行）

---

**追溯**：架构理由见 `docs/04-architecture.md` §3；数据落地见 `docs/06-db-design.md`；接口契约见 `docs/07-api-spec.md`。
