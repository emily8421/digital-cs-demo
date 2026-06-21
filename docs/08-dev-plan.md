# 08 开发计划

> AI 生成初稿，**人工确认**。按 Sprint 拆分，每个 Sprint 用 global-rules §3 格式（目标/输入文档/修改范围/验收标准/禁止事项）。
> 当前阶段＝Phase1（MVP）。单 Sprint 限 1~3 文件/模块。按 global-rules §8 积累式演进：升阶段在原位追加，不删旧 Sprint。

> ⚠️ Sprint-0 是全局前提（企业微信外部群能力验证），先行；未通过则 MVP 以模拟器通道推进，不阻塞核心价值（见 03 §3）。

---

## Sprint-0：企业微信外部群能力验证（技术验证项）

### 目标
核实「企业微信客户群（含外部微信联系人）机器人/自动回复对外部用户消息的接收与应答」是否可行：开放范围、接口权限、频控、是否需企业认证。产出一份验证结论，决定 REQ-15 是否升 P1 并接入真实通道。

### 输入文档
- `docs/vision/product-vision.md`（文首 ⚠️）、`docs/03-prd.md` §3、`docs/design-channel-adapter.md` §2

### 修改范围
- 新增 `docs/sprint-0-wework-findings.md`（验证结论：能/不能/条件）；不改业务代码。

### 验收标准
- 结论明确：能否接收外部用户消息、能否应答、所需权限/认证/频控；并给出「通过则接入、未通过则仅用模拟器」的决策建议。

### 禁止事项
- 不在本 Sprint 写企业微信生产发送逻辑；不触碰个人微信自动化。

---

## Sprint-1：项目骨架 + 通道适配层 + 模拟器

### 目标
搭后端骨架（FastAPI + PG），实现通道适配层与内置模拟器，落地 `dcs_messages`/`dcs_conversations`，跑通「投递一条文本 → 归一化 → 入库 → 可读回」。

### 输入文档
- `docs/04-architecture.md`、`docs/05-tech-spec.md`、`docs/06-db-design.md`（messages/conversations）、`docs/07-api-spec.md` §3.1、`docs/design-channel-adapter.md`

### 修改范围
- `backend/`（api/service/model/channels 骨架）、`docker/`（本地 PG+应用）、`scripts/`（初始化）

### 验收标准
- `POST /api/v1/messages/simulate` 可投递文本并返回 message_id；`GET /api/v1/conversations/{id}` 可读回消息流（字段齐全）。REQ-1 可验证口径通过。

### 禁止事项
- 不接 LLM/向量库；不写企业微信真实通道（待 Sprint-0 结论）；不超过 3 个模块。

### 验收记录（2026-06-21）
- 已实现：通道适配层（`simulator`）+ `NormalizedMessage` 契约 + `dcs_messages`/`dcs_conversations` + `POST /api/v1/messages/simulate` + `GET /api/v1/conversations(/{id})`。
- 自动化测试：`pytest -q` → **3 passed**（SQLite 内存库；覆盖 投递→归一化→入库→读回、同群聚合、非文字归一化）。
- 真实 PG 端到端（补验，已通过）：`docker compose up db`（PG:16，宿主端口 15432）+ `uvicorn app.main:app`。
  - `POST /api/v1/messages/simulate`（text）→ `200 {message_id, conversation_id}`；
  - 同群再投 `image`（非文字）→ 归一化入库，`conversation_id` 与上一条相同（同群聚合生效）；
  - `GET /api/v1/conversations/{id}` → 读回消息流，字段齐全（`direction/channel/content_type/content_text/raw_payload/received_at`，非文字 `content_text` 为空且保留 `raw_payload`）。
  - 中文 UTF-8 存储无误（`repr` 校验码点正确；先前控制台乱码仅 Windows GBK 显示问题，非存储问题）。
- 依赖备注：Python 3.14 下驱动用 **psycopg3**（`psycopg[binary]`）替代 psycopg2-binary（后者无 3.14 预编译包）。
- **REQ-1 可验证口径：通过。** Sprint-1 验收完成。

---

## Sprint-2：知识库与检索（单轮问答 + 标准 FAQ）

### 目标
实现知识库 RAG 检索与作答，落地 `dcs_knowledge_items`，预置愿景种子数据；接入对话编排主路径「命中→作答」。

### 输入文档
- `docs/02-srs.md` REQ-2/3、`docs/06-db-design.md`（knowledge_items）、`docs/07-api-spec.md` §3.2、`docs/design-knowledge-base.md` §2、`docs/design-conversation-engine.md` §2

### 修改范围
- `backend/service/knowledge/`、`backend/model/`（knowledge_items）、种子数据脚本

### 验收标准
- `GET /api/v1/knowledge/search?q=` 命中返回带 score 的 confirmed 条目；未命中 `hit:false`。REQ-2/3 可验证口径通过。

### 禁止事项
- 不做多轮；未命中不生成编造答案；向量库/LLM 选型须与 05 一致（新依赖先确认）。

### 验收记录（2026-06-21）
- 已实现：`dcs_knowledge_items`（pgvector `vector(512)`）+ `KnowledgeItem` ORM + 检索（pgvector cosine）+ `select_hits` 阈值/排序纯逻辑 + `GET /api/v1/knowledge/search` + 灯带/驱动 FAQ 种子 7 条。
- **embedding 落地变更（重要）**：原拟「本地 BGE 进程内（sentence-transformers）」，但 Python 3.14 + Windows 下 torch/onnxruntime 原生 DLL（`c10.dll`/pybind）加载失败（`WinError 1114`），改用 **Docker TEI（text-embeddings-inference）服务**、宿主以 httpx 调用；向量库仍 pgvector（05 不变）。详见 `docs/context-and-constraints.md` §3/§4/§5.2。
- 自动化测试：`pytest -q` → **8 passed**（Sprint-1 的 3 + Sprint-2 的 `select_hits` 逻辑 5），SQLite 内存库，不依赖 Docker/torch。
- 真实端到端（TEI bge-small-zh + pgvector + uvicorn）：`search` 命中返回带 score 的 confirmed 条目，无关问题 `hit:false`。
- **阈值标定（数据驱动）**：扫描种子相似度分布——相关问法 top-1 ∈ [0.50, 0.86]、无关问法 ≤ 0.46；据此把默认阈值从初稿 0.7 调到 **0.5**（cosine 相似度，可配置 `config.knowledge_score_threshold`），随真实语料增长需复核。
- **REQ-2/3 可验证口径：通过。** Sprint-2 验收完成（编排「命中→作答」接入留 Sprint-4）。

---

## Sprint-3：留资 + 转交通知 + 角色路由

### 目标
实现留资识别记录、角色路由、口语化员工提醒；落地 `dcs_leads`/`dcs_handoffs`/`dcs_staff`/`dcs_routing_rules`/`dcs_notifications`。

### 输入文档
- `docs/02-srs.md` REQ-4/5/8、`docs/06-db-design.md`（leads/handoffs/staff/routing_rules/notifications）、`docs/07-api-spec.md` §3.3、`docs/design-routing-notification.md` §2

### 修改范围
- `backend/service/leads/`、`backend/service/routing/`、`backend/model/`

### 验收标准
- 投递含手机号消息→产生脱敏留资记录；触发转交→按路由送达目标角色并附摘要。REQ-4/5/8 可验证口径通过。

### 禁止事项
- 转人工暂停的会话级判定留到 Sprint-5（已提至 P1）；Sprint-3 只做转交记录与通知，不做暂停判定。不做前端；联系方式须脱敏存储。

### 验收记录（2026-06-21）
- 已实现：5 表 ORM（`dcs_leads`/`dcs_staff`/`dcs_routing_rules`/`dcs_handoffs`/`dcs_notifications`）；留资识别（`detector` 手机号正则 + 脱敏，接入 `handle_inbound`）；路由（`scenario→target_role→在岗 staff`）；口语化通知（`build_handoff_body`）；`POST /api/v1/handoffs`；飞书 webhook 出站（`FEISHU_WEBHOOK_URL` 可配）；staff/routing 种子脚本。
- 边界（合规）：联系方式**只脱敏不加密**（`contact_value_enc` 建 bytea 留 NULL，加密需密钥管理待后续）；飞书**默认只落库**（webhook 未配则不发送，本机原型）；不做转人工暂停（Sprint-5）；不做编排完整分支（Sprint-4）。
- 自动化测试：`pytest -q` → **19 passed**（Sprint-1/2 的 8 + 留资 3 / 路由 5 / handoffs 3）。
- 真实端到端：投递含手机号消息 → 产生脱敏留资（`139****5678`）；`POST /handoffs` 路由 `presale→sales/小雯`、`unknown_question→owner/陈总`，通知落 `dcs_notifications`(kind=handoff, channel=feishu)，body 口语化含摘要+客户标识+脱敏联系方式。
- **REQ-4/5/8 可验证口径：通过。** 转人工暂停留 Sprint-5，编排闭环（检索作答/缺口转人串联）留 Sprint-4。

---

## Sprint-4：知识缺口检测 + 编排闭环串联

### 目标
实现缺口检测→请留资+转拍板人；把「检索作答 / 缺口转人 / 留资」编排成端到端闭环；落地 `dcs_knowledge_gaps`。

### 输入文档
- `docs/02-srs.md` REQ-6、`docs/06-db-design.md`（knowledge_gaps）、`docs/design-conversation-engine.md` §2、`docs/design-knowledge-base.md` §2

### 修改范围
- `backend/service/conversation/`（编排）、`backend/model/`（knowledge_gaps）

### 验收标准
- 投递未覆盖问题→客户侧收到「请留资/将请同事确认」、员工侧收到缺口通知、缺口入库(open)。03 §3 Demo 步骤 1–3 可走通。

### 禁止事项
- 不做多轮/身份披露/非文字完整分支；任何分支不允许无依据生成参数/结论。

### 验收记录（2026-06-21）
- 已实现：`KnowledgeGap` ORM（`dcs_knowledge_gaps`，status open/resolved，`resolved_knowledge_id` 留 P2 回写）；编排引擎 `service/conversation`（`act_on_search` 命中作答/未命中缺口+转交·纯编排可测；`orchestrate` 检索+编排）；`handle_inbound` 接入编排（try/except：无 TEI/pgvector 时跳过，不阻塞入库）；客户侧出站＝写 `dcs_messages`(outbound)（原型，不经 OutboundChannel）；`SimulateData` 返回编排结果（hit/reply_text/gap_id/handoff_id）。
- 自动化测试：`pytest -q` → **21 passed**（+编排 `act_on_search` 命中/未命中 2）。
- 真实端到端：命中问题（5050/2835）→ 作答 outbound（回标准答案）；未覆盖问题（公司地址）→ 客户侧「请留资」+ `dcs_knowledge_gaps`(open) + 转交 owner/陈总 + 通知。
- **REQ-6 可验证口径：通过。** MVP 主路径闭环完成（Sprint-2 检索 + Sprint-3 留资/转交 + Sprint-4 串联）；03 §3 Demo 步骤 1-3 可走通。
- 检索边界（待调）：灯带规格类问题（如「海里使用」）可能在阈值 0.5 下误命中同类规格条目（召回偏宽），属检索质量持续调优（Sprint-2 范畴），**编排逻辑不受影响**（缺口分支已用低相似度问题验证）。

---

## Sprint-5：转人工暂停 + 非文字消息处理（编排边界）

### 目标
实现两条由 P2 提至 P1 的编排边界：会话级「转人工后 AI 暂停」(REQ-10) 与「非文字消息如实告知 + 提醒」(REQ-12)。

### 输入文档
- `docs/02-srs.md` REQ-10/12、`docs/design-conversation-engine.md` §2、`docs/design-channel-adapter.md` §2、`docs/06-db-design.md`（dcs_conversations.handoff_state）

### 修改范围
- `backend/service/conversation/`（编排：暂停判定 + 非文字分支）、`backend/model/`（handoff_state 读写）

### 验收标准
- 会话置 `handed_off` 后投递新客户消息 → 不产生客户侧自动回复；解除标记后恢复（REQ-10）。
- 投递 voice 消息 → 群内如实告知 + 员工提醒，不生成内容作答（REQ-12）。

### 禁止事项
- 不做话题（thread）级暂停（后续）；不做非文字内容理解（永久）；不超过 3 个模块。

---

## Sprint-6：定时小结 / 日报

### 目标
实现定时小结：聚合消息量/类型、需跟进清单（含已分给谁），生成经营者小结；支持手动触发测试。

### 输入文档
- `docs/02-srs.md` REQ-7、`docs/07-api-spec.md` §3.4、`docs/design-routing-notification.md` §2

### 修改范围
- `backend/service/summary/`、调度配置（待确认 APScheduler/cron）

### 验收标准
- 手动触发 `POST /api/v1/summaries/daily` 返回含「总量/需跟进清单/分配对象」的小结文案；定时按配置触发。REQ-7 可验证口径通过；03 §3 Demo 步骤 4 可走通。

### 禁止事项
- 小结口径为「该关注什么」非系统报表腔；不引入前端。

---

## Sprint-7：端到端串联 + 企业微信接入（视 Sprint-0 结论）

### 目标
端到端串联 P1 全流程；若 Sprint-0 验证通过，接入企业微信真实通道并重放 Demo；否则固化模拟器演示路径。

### 输入文档
- `docs/03-prd.md` §3（Demo 脚本）、`docs/design-channel-adapter.md` §2、Sprint-0 结论

### 修改范围
- `backend/channels/wework/`（仅当通过）、集成测试 `tests/`

### 验收标准
- 03 §3 Demo 步骤 1–6 在所选通道走通；P1 全部 REQ 可验证口径通过。

### 禁止事项
- 未通过验证不向真实外部用户发送；不做 P2 功能。

---

> P2（多轮引导/身份披露/知识回写/时效监控）与愿景（订单进度/售后推理）的 Sprint，待 P1 完成升阶段后在本文**原位追加**，不删旧内容。
> （转人工暂停 REQ-10、非文字处理 REQ-12 已提至 P1，见 Sprint-5。）

---

## 通道验证路线（非 P1 功能 · 对比研究）

> 真实数据的 I/O 载体验证，**非商用、不进 P1 功能范围**。完整路线与对比矩阵见 `docs/channel-validation-plan.md`；决定见 `docs/open-decisions.md` DEC-7。
> - **Step 一（模拟器）**：＝ Sprint-1，验证整体架构（先行、不阻塞）。
> - **Step 二（真实微信号 wxautox4 式）/ Step 三（合规：会话存档采集 + 飞书通知 + 微信客服回复）**：MVP 架构跑通后，作为**两个并行 Spike**，用真实数据做对比。具体 Sprint 待 MVP 完成后在此**原位追加**。
