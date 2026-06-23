# 08 开发计划

> AI 生成初稿，**人工确认**。按 Sprint 拆分，每个 Sprint 用 global-rules §3 格式（目标/输入文档/修改范围/验收标准/禁止事项）。
> 单 Sprint 限 1~3 文件/模块。按 global-rules §8 积累式演进：升阶段在对应 Phase 分组**原位追加**，**不删旧 Sprint**。
> **阶段归属**取自 `docs/03-prd.md` §3（唯一来源）与 `ai/project-rules.md` §1（当前阶段指针）。
> **P1（MVP）已于 2026-06-21 收官；当前阶段＝Phase2（优化扩展）。**

> ⚠️ Sprint-0 是全局前提（企业微信外部群能力验证），先行；未通过则 MVP 以模拟器通道推进，不阻塞核心价值（见 03 §3）。

---

## Phase1 / MVP —— ✅ 已收官（2026-06-21）

> **纳入功能**：REQ-1/2/3/4/5/6/7/8/10/12（+ REQ-15 作为 Sprint-0 技术验证项，结论＝客户群群内路径不成立，改走模拟器通道）。
> **收官判据**：03 §3 Demo 步骤 1–5（模拟器通道）走通；P1 全部 REQ 可验证口径通过（见 Sprint-1~7 各验收记录）。步骤 6（企微）因 Sprint-0 未通过而跳过。

### Sprint-0：企业微信外部群能力验证（技术验证项）

#### 目标
核实「企业微信客户群（含外部微信联系人）机器人/自动回复对外部用户消息的接收与应答」是否可行：开放范围、接口权限、频控、是否需企业认证。产出一份验证结论，决定 REQ-15 是否升 P1 并接入真实通道。

#### 输入文档
- `docs/vision/product-vision.md`（文首 ⚠️）、`docs/03-prd.md` §3、`docs/design-channel-adapter.md` §2

#### 修改范围
- 新增 `docs/sprint-0-wework-findings.md`（验证结论：能/不能/条件）；不改业务代码。

#### 验收标准
- 结论明确：能否接收外部用户消息、能否应答、所需权限/认证/频控；并给出「通过则接入、未通过则仅用模拟器」的决策建议。

#### 禁止事项
- 不在本 Sprint 写企业微信生产发送逻辑；不触碰个人微信自动化。

---

### Sprint-1：项目骨架 + 通道适配层 + 模拟器

#### 目标
搭后端骨架（FastAPI + PG），实现通道适配层与内置模拟器，落地 `dcs_messages`/`dcs_conversations`，跑通「投递一条文本 → 归一化 → 入库 → 可读回」。

#### 输入文档
- `docs/04-architecture.md`、`docs/05-tech-spec.md`、`docs/06-db-design.md`（messages/conversations）、`docs/07-api-spec.md` §3.1、`docs/design-channel-adapter.md`

#### 修改范围
- `backend/`（api/service/model/channels 骨架）、`docker/`（本地 PG+应用）、`scripts/`（初始化）

#### 验收标准
- `POST /api/v1/messages/simulate` 可投递文本并返回 message_id；`GET /api/v1/conversations/{id}` 可读回消息流（字段齐全）。REQ-1 可验证口径通过。

#### 禁止事项
- 不接 LLM/向量库；不写企业微信真实通道（待 Sprint-0 结论）；不超过 3 个模块。

#### 验收记录（2026-06-21）
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

### Sprint-2：知识库与检索（单轮问答 + 标准 FAQ）

#### 目标
实现知识库 RAG 检索与作答，落地 `dcs_knowledge_items`，预置愿景种子数据；接入对话编排主路径「命中→作答」。

#### 输入文档
- `docs/02-srs.md` REQ-2/3、`docs/06-db-design.md`（knowledge_items）、`docs/07-api-spec.md` §3.2、`docs/design-knowledge-base.md` §2、`docs/design-conversation-engine.md` §2

#### 修改范围
- `backend/service/knowledge/`、`backend/model/`（knowledge_items）、种子数据脚本

#### 验收标准
- `GET /api/v1/knowledge/search?q=` 命中返回带 score 的 confirmed 条目；未命中 `hit:false`。REQ-2/3 可验证口径通过。

#### 禁止事项
- 不做多轮；未命中不生成编造答案；向量库/LLM 选型须与 05 一致（新依赖先确认）。

#### 验收记录（2026-06-21）
- 已实现：`dcs_knowledge_items`（pgvector `vector(512)`）+ `KnowledgeItem` ORM + 检索（pgvector cosine）+ `select_hits` 阈值/排序纯逻辑 + `GET /api/v1/knowledge/search` + 灯带/驱动 FAQ 种子 7 条。
- **embedding 落地变更（重要）**：原拟「本地 BGE 进程内（sentence-transformers）」，但 Python 3.14 + Windows 下 torch/onnxruntime 原生 DLL（`c10.dll`/pybind）加载失败（`WinError 1114`），改用 **Docker TEI（text-embeddings-inference）服务**、宿主以 httpx 调用；向量库仍 pgvector（05 不变）。详见 `docs/context-and-constraints.md` §3/§4/§5.2。
- 自动化测试：`pytest -q` → **8 passed**（Sprint-1 的 3 + Sprint-2 的 `select_hits` 逻辑 5），SQLite 内存库，不依赖 Docker/torch。
- 真实端到端（TEI bge-small-zh + pgvector + uvicorn）：`search` 命中返回带 score 的 confirmed 条目，无关问题 `hit:false`。
- **阈值标定（数据驱动）**：扫描种子相似度分布——相关问法 top-1 ∈ [0.50, 0.86]、无关问法 ≤ 0.46；据此把默认阈值从初稿 0.7 调到 **0.5**（cosine 相似度，可配置 `config.knowledge_score_threshold`），随真实语料增长需复核。
- **REQ-2/3 可验证口径：通过。** Sprint-2 验收完成（编排「命中→作答」接入留 Sprint-4）。

---

### Sprint-3：留资 + 转交通知 + 角色路由

#### 目标
实现留资识别记录、角色路由、口语化员工提醒；落地 `dcs_leads`/`dcs_handoffs`/`dcs_staff`/`dcs_routing_rules`/`dcs_notifications`。

#### 输入文档
- `docs/02-srs.md` REQ-4/5/8、`docs/06-db-design.md`（leads/handoffs/staff/routing_rules/notifications）、`docs/07-api-spec.md` §3.3、`docs/design-routing-notification.md` §2

#### 修改范围
- `backend/service/leads/`、`backend/service/routing/`、`backend/model/`

#### 验收标准
- 投递含手机号消息→产生脱敏留资记录；触发转交→按路由送达目标角色并附摘要。REQ-4/5/8 可验证口径通过。

#### 禁止事项
- 转人工暂停的会话级判定留到 Sprint-5（已提至 P1）；Sprint-3 只做转交记录与通知，不做暂停判定。不做前端；联系方式须脱敏存储。

#### 验收记录（2026-06-21）
- 已实现：5 表 ORM（`dcs_leads`/`dcs_staff`/`dcs_routing_rules`/`dcs_handoffs`/`dcs_notifications`）；留资识别（`detector` 手机号正则 + 脱敏，接入 `handle_inbound`）；路由（`scenario→target_role→在岗 staff`）；口语化通知（`build_handoff_body`）；`POST /api/v1/handoffs`；飞书 webhook 出站（`FEISHU_WEBHOOK_URL` 可配）；staff/routing 种子脚本。
- 边界（合规）：联系方式**只脱敏不加密**（`contact_value_enc` 建 bytea 留 NULL，加密需密钥管理待后续）；飞书**默认只落库**（webhook 未配则不发送，本机原型）；不做转人工暂停（Sprint-5）；不做编排完整分支（Sprint-4）。
- 自动化测试：`pytest -q` → **19 passed**（Sprint-1/2 的 8 + 留资 3 / 路由 5 / handoffs 3）。
- 真实端到端：投递含手机号消息 → 产生脱敏留资（`139****5678`）；`POST /handoffs` 路由 `presale→sales/小雯`、`unknown_question→owner/陈总`，通知落 `dcs_notifications`(kind=handoff, channel=feishu)，body 口语化含摘要+客户标识+脱敏联系方式。
- **REQ-4/5/8 可验证口径：通过。** 转人工暂停留 Sprint-5，编排闭环（检索作答/缺口转人串联）留 Sprint-4。

---

### Sprint-4：知识缺口检测 + 编排闭环串联

#### 目标
实现缺口检测→请留资+转拍板人；把「检索作答 / 缺口转人 / 留资」编排成端到端闭环；落地 `dcs_knowledge_gaps`。

#### 输入文档
- `docs/02-srs.md` REQ-6、`docs/06-db-design.md`（knowledge_gaps）、`docs/design-conversation-engine.md` §2、`docs/design-knowledge-base.md` §2

#### 修改范围
- `backend/service/conversation/`（编排）、`backend/model/`（knowledge_gaps）

#### 验收标准
- 投递未覆盖问题→客户侧收到「请留资/将请同事确认」、员工侧收到缺口通知、缺口入库(open)。03 §3 Demo 步骤 1–3 可走通。

#### 禁止事项
- 不做多轮/身份披露/非文字完整分支；任何分支不允许无依据生成参数/结论。

#### 验收记录（2026-06-21）
- 已实现：`KnowledgeGap` ORM（`dcs_knowledge_gaps`，status open/resolved，`resolved_knowledge_id` 留 P2 回写）；编排引擎 `service/conversation`（`act_on_search` 命中作答/未命中缺口+转交·纯编排可测；`orchestrate` 检索+编排）；`handle_inbound` 接入编排（try/except：无 TEI/pgvector 时跳过，不阻塞入库）；客户侧出站＝写 `dcs_messages`(outbound)（原型，不经 OutboundChannel）；`SimulateData` 返回编排结果（hit/reply_text/gap_id/handoff_id）。
- 自动化测试：`pytest -q` → **21 passed**（+编排 `act_on_search` 命中/未命中 2）。
- 真实端到端：命中问题（5050/2835）→ 作答 outbound（回标准答案）；未覆盖问题（公司地址）→ 客户侧「请留资」+ `dcs_knowledge_gaps`(open) + 转交 owner/陈总 + 通知。
- **REQ-6 可验证口径：通过。** MVP 主路径闭环完成（Sprint-2 检索 + Sprint-3 留资/转交 + Sprint-4 串联）；03 §3 Demo 步骤 1-3 可走通。
- 检索边界（待调）：灯带规格类问题（如「海里使用」）可能在阈值 0.5 下误命中同类规格条目（召回偏宽），属检索质量持续调优（Sprint-2 范畴），**编排逻辑不受影响**（缺口分支已用低相似度问题验证）。

---

### Sprint-5：转人工暂停 + 非文字消息处理（编排边界）

#### 目标
实现两条由 P2 提至 P1 的编排边界：会话级「转人工后 AI 暂停」(REQ-10) 与「非文字消息如实告知 + 提醒」(REQ-12)。

#### 输入文档
- `docs/02-srs.md` REQ-10/12、`docs/design-conversation-engine.md` §2、`docs/design-channel-adapter.md` §2、`docs/06-db-design.md`（dcs_conversations.handoff_state）

#### 修改范围
- `backend/service/conversation/`（编排：暂停判定 + 非文字分支）、`backend/model/`（handoff_state 读写）

#### 验收标准
- 会话置 `handed_off` 后投递新客户消息 → 不产生客户侧自动回复；解除标记后恢复（REQ-10）。
- 投递 voice 消息 → 群内如实告知 + 员工提醒，不生成内容作答（REQ-12）。

#### 禁止事项
- 不做话题（thread）级暂停（后续）；不做非文字内容理解（永久）；不超过 3 个模块。

#### 验收记录（2026-06-21）
- 已实现：编排边界——`handle_inbound` 加 `handoff_state` 检查（`handed_off` 暂停所有自动编排，仅记录，REQ-10）+ 非文字分支 `act_on_non_text`（如实告知 + 转交 owner 提醒，不生成内容作答、不写 gap，REQ-12）；`POST /api/v1/conversations/{id}/handoff-state`（置/解除暂停标记）；`build_non_text_reply`（按类型：语音/图片/视频）。
- 边界：暂停为**会话级**（话题级留后续）；非文字仅识别类型 + 如实告知（**内容理解永久非目标**）。
- 自动化测试：`pytest -q` → **24 passed**（+暂停/非文字 3）。
- 真实端到端：投 voice → 如实告知 + 员工提醒（notif）；置 `handed_off` → 投消息无自动回复（reply/notif 均 None）；解除 `auto` → 恢复。
- **REQ-10/12 可验证口径：通过。**

---

### Sprint-6：定时小结 / 日报

#### 目标
实现定时小结：聚合消息量/类型、需跟进清单（含已分给谁），生成经营者小结；支持手动触发测试。

#### 输入文档
- `docs/02-srs.md` REQ-7、`docs/07-api-spec.md` §3.4、`docs/design-routing-notification.md` §2

#### 修改范围
- `backend/service/summary/`、调度配置（待确认 APScheduler/cron）

#### 验收标准
- 手动触发 `POST /api/v1/summaries/daily` 返回含「总量/需跟进清单/分配对象」的小结文案；定时按配置触发。REQ-7 可验证口径通过；03 §3 Demo 步骤 4 可走通。

#### 禁止事项
- 小结口径为「该关注什么」非系统报表腔；不引入前端。

#### 验收记录（2026-06-21）
- 已实现：`service/summary/generator.generate_daily_summary`（聚合 `inbound messages` 量/类型 + `open handoffs` 跟进清单含目标 staff → 口语化小结 → 落 `dcs_notifications`(kind=summary) 发 owner）；`POST /api/v1/summaries/daily`（手动触发）。
- **调度选型收敛**：**外部 cron**（应用不内嵌 APScheduler）——接口提供能力，定时由部署层 cron/systemd/k8s 调用；少组件、生产更稳（进程重启不丢调度）。已同步 `docs/05-tech-spec.md`。
- 自动化测试：`pytest -q` → **26 passed**（+小结聚合 2）。
- 真实端到端：`POST /summaries/daily` →「今天共 8 条客户消息（文字6、语音2）…3 条需跟进：售前(小雯)、待确认问题(陈总)…均已通知对应同事」；`dcs_notifications` 落 kind=summary。
- **REQ-7 可验证口径：通过。** 03 §3 Demo 步骤 4 可走通。

---

### Sprint-7：端到端串联 + 企业微信接入（视 Sprint-0 结论）

#### 目标
端到端串联 P1 全流程；若 Sprint-0 验证通过，接入企业微信真实通道并重放 Demo；否则固化模拟器演示路径。

#### 输入文档
- `docs/03-prd.md` §3（Demo 脚本）、`docs/design-channel-adapter.md` §2、Sprint-0 结论

#### 修改范围
- `backend/channels/wework/`（仅当通过）、集成测试 `tests/`

#### 验收标准
- 03 §3 Demo 步骤 1–6 在所选通道走通；P1 全部 REQ 可验证口径通过。

#### 禁止事项
- 未通过验证不向真实外部用户发送；不做 P2 功能。

#### 验收记录（2026-06-21）
- 已实现：端到端 Demo 集成测试 `tests/test_demo_flow.py`（monkeypatch fake 检索，SQLite 串联 03 §3 Demo 步骤 1-5：作答→缺口转交→留资→小结→非文字→暂停）；真实环境 Demo 脚本 `scripts/demo.py`（固化模拟器演示路径）。
- **企业微信**：Sprint-0 已核实客户群群内自动回复路径**不成立**（见 `docs/sprint-0-wework-findings.md`），Sprint-7 **不接企微**，固化模拟器 Demo；真实通道（微信客服/智能机器人入外部群）待人工选定替代方案，属愿景。
- 自动化测试：`pytest -q` → **27 passed**（+Demo 串联 1）；各环节真实端到端已在 Sprint-2~6 验证（检索/留资转交/编排闭环/暂停非文字/小结）。
- **03 §3 Demo 步骤 1-5 走通**（模拟器通道）；步骤 6（企微）跳过。
- **P1 全部 REQ 可验证口径通过**：REQ-1/2/3/4/5/6/7/8/10/12。**🎯 P1（MVP）收官。**

---

### 演示辅助 UI（P1 收官后补）

> P1 收官后补的**演示工具**（非 P1 功能、非 Sprint 范围）。PR #8/#9/#10。

- `frontend/index.html`：聊天窗 + 演示控制台，调后端 API；`backend/app/main.py` 挂载 `/ui`（StaticFiles，同源免 CORS）。
- 功能：客户消息→AI 作答/请留资；非文字如实告知；转交/小结飞书卡片；聊天历史持久化、可重放；一键重放 Demo（03 §3 步骤 1-5）。
- 定位：**演示辅助 UI**（非功能前端/员工后台）；P1 功能交互仍走消息通道（见 03 §4、04、05）。
- 启动：`docker compose up -d` + `uvicorn` → 浏览器开 http://127.0.0.1:8000/ui

---

## Phase2 / 优化扩展 —— 🚧 进行中

> **纳入功能**：REQ-9（多轮引导）、REQ-11（身份披露）、REQ-13（知识回写）、REQ-14（时效监控）。
> REQ-10（转人工暂停）、REQ-12（非文字处理）已在 P1（Sprint-5）实现；本期 P2 仅做 **REQ-10 话题（thread）级精化**（Sprint-12）——会话内某话题 handed_off 只暂停该话题，其他话题不暂停。
> **Sprint-8~13**：状态待实现，验收记录在各 Sprint 启动后于原位追加。

### Sprint-8：多轮引导（定制询盘状态机，REQ-9）

#### 目标
定制询盘堆叠多要求时，拆项 → 多轮状态机逐条确认 → 收集后整理为可核价摘要转交。

#### 输入文档
- `docs/02-srs.md` REQ-9、`docs/design-conversation-engine.md` §3（P2 多轮骨架）、`docs/06-db-design.md`（conversations 多轮状态字段）

#### 修改范围
- `backend/service/conversation/`（多轮状态机）、`backend/model/`（状态字段）

#### 验收标准
- 投递定制询盘（多要求）→ 系统拆项逐条确认 → 收集后摘要转交。REQ-9 可验证口径通过。

#### 禁止事项
- 不做身份披露/回写/时效；状态机不过度复杂（覆盖典型定制询盘即可）。

#### 验收记录（2026-06-23）
- 已实现：`Inquiry` ORM（`dcs_inquiries`，**新表**而非 conversations 扩展——询盘级生命周期：status/items_pending/items_collected(jsonb)/current_item/summary）+ `service/conversation/inquiry.py`（`detect_custom_inquiry` 触发词识别+维度抽取/默认、`build_summary`、`start_inquiry`/`act_on_inquiry_reply` 状态机逐项确认→摘要转交）+ `orchestrator.handle_inbound` 文本分支接入（collecting 优先 → 新询盘识别 → 检索兜底）。
- 设计决策：状态落**新表 `dcs_inquiries`**（询盘级，不污染 conversations）；意图识别**纯规则**（定制触发词+维度关键词，大小写不敏感，不引 LLM，守可控性）；客户未陈述规格时用默认核心维度（颜色/数量/Logo/交期）；转交走 `presale` 路由（售前核价）。**抽值预填（2026-06-23 优化）**：颜色/数量/Logo/交期 用正则抽客户陈述值预填 collected，系统只追问未陈述维度（陈述规格不重复问）；后续项提示去前缀重复。
- 自动化测试：`pytest -q` → **33 passed**（P1 的 27 + `test_inquiry` 纯逻辑 6：触发词识别+维度抽取/默认/不误判、摘要模板）。SQLite 内存库，不依赖 TEI/pgvector。
- 真实端到端（uvicorn + docker db/embeddings）：投递「我要定制灯带」→ 系统逐项问【颜色/数量/Logo/交期】→ 客户逐项答（蓝色/100米/要logo/7天交货）→ 收集完生成摘要「颜色=蓝色 / 数量=100米 / Logo=要logo / 交期=7天交货」转交 → `dcs_inquiries=completed` + `handoff #7`(presale)。
- **REQ-9 可验证口径：通过。** Sprint-8 验收完成（身份披露/回写/时效留 Sprint-9~11）。

---

### Sprint-9：AI 身份披露（REQ-11）

#### 目标
被问「是不是 AI/机器人」时，按既定口径自然承认身份，不喧宾夺主。

#### 输入文档
- `docs/02-srs.md` REQ-11、`docs/design-conversation-engine.md` §3（P2 身份骨架）

#### 修改范围
- `backend/service/conversation/`（身份意图识别 + 既定话术）

#### 验收标准
- 投递「你是机器人吗」→ 系统按既定话术承认身份。REQ-11 可验证口径通过。

#### 禁止事项
- 被动披露（不主动）；不做多轮；话术不喧宾夺主。

#### 验收记录（2026-06-23）
- 已实现：`service/conversation/identity.py`（`detect_identity_question` 规则识别身份询问、`build_identity_reply` 既定话术、`act_on_identity` 写 outbound）+ `orchestrator.handle_inbound` 文本分支**最前**接入（身份披露优先于多轮/检索）。
- 设计决策：意图识别**纯规则**（身份询问关键词，大小写不敏感，不引 LLM）；既定话术承认身份+角色+回归服务（「我是小辰，汇辰灯饰的 AI 客服助理…有什么可以帮您的？」）；**被动披露**（被问才答，不主动）、单轮、不触多轮/缺口/转交。
- 自动化测试：`pytest -q` → **38 passed**（+ `test_identity` 4：明确身份问句触发、普通问题不误判、话术含身份+角色+服务）。
- 真实端到端（uvicorn + docker）：投「你是机器人吗」→ 既定话术承认身份（hit=false）；投「5050和2835区别」→ 照常检索作答（hit=true，身份不误判普通问题）。
- **REQ-11 可验证口径：通过。** Sprint-9 验收完成（知识回写/时效/话题暂停留 Sprint-10~12）。

---

### Sprint-10：知识回写 + 确认页面（REQ-13）

#### 目标
拍板人答复缺口后 → 生成 pending 条目 → 征询确认 → 经确认页面 confirm → confirmed；落地知识确认轻量页面（前端）。

#### 输入文档
- `docs/02-srs.md` REQ-13、`docs/design-knowledge-base.md` §3（P2 回写骨架）、`docs/07-api-spec.md` §3.5（POST /knowledge/{id}/confirm）

#### 修改范围
- `backend/service/knowledge/`（回写 pending→confirmed）、`backend/app/api/`（confirm 接口）、`frontend/`（知识确认页面）

#### 验收标准
- 缺口补答 → pending → 确认页面确认 → confirmed 入库。REQ-13 可验证口径通过。

#### 禁止事项
- 回写必须经拍板人确认（不自动固化）；不做多轮。

#### 验收记录（2026-06-23）
- 已实现：`service/knowledge/writeback.py`（`answer_gap` 补答→pending+embedding+关联gap、`confirm_knowledge` pending→confirmed+gap resolved、`list_open_gaps`/`list_pending`）+ `api/knowledge.py` 4 接口（GET /gaps、POST /gaps/{id}/answer、GET /pending、POST /{id}/confirm）+ `frontend/confirm.html` 知识确认页面（两区：缺口补答 + 待确认，挂 /ui/confirm.html）+ schemas。
- 设计决策：保留 **pending 中间态**（展示「确认才回写」）；补答即生成 embedding（确认后可检索命中）；回填 `gap.resolved_knowledge_id` + `gap.status=resolved`；归属 `source_staff_id` 记确认人。
- 自动化测试：`pytest -q` → **43 passed**（+ `test_writeback` 5：补答→pending+关联、confirm→confirmed+gap resolved、缺口不存在/非pending 返回 None、列表；SQLite + fake embedder）。
- 真实端到端（uvicorn + docker TEI）：造缺口（未命中「今天天气怎么样」→ gap #6）→ 补答（pending #8）→ 确认（confirmed + gap #6 resolved）→ 检索「天气」命中新条目（answer=补答内容）。确认页面 `/ui/confirm.html` 可视化操作。
- **REQ-13 可验证口径：通过。** Sprint-10 验收完成（时效/话题暂停留 Sprint-11~12）。

---

### Sprint-11：响应时效 SLA 监控（REQ-14）

#### 目标
扫描「客户消息 → 首次应答」间隔，对 > 阈值（愿景口径 30 分钟）未回复者提示。

#### 输入文档
- `docs/02-srs.md` REQ-14、`docs/design-routing-notification.md` §3（P2 时效骨架）

#### 修改范围
- `backend/service/`（时效扫描，候选 sla/ 或复用 summary 调度）、调度配置

#### 验收标准
- 模拟超时未回复消息 → 触发时效提示。REQ-14 可验证口径通过。

#### 禁止事项
- 不做售后/订单；超时口径待调参。

#### 验收记录（2026-06-23）
- 已实现：`service/sla/scanner.py`（`scan_sla` 扫超时未答 + 生成口语化提示 + 写 Notification kind=sla）、`api/sla.py`（POST /sla/scan 手动触发/外部 cron）、`config.sla_threshold_minutes`（默认 30）、models Notification CHECK 加 sla。
- 设计决策：计时口径＝每会话最后 inbound，同会话无更晚 outbound + 距今 > 阈值 → 超时未答；提示发经营者（owner，复用 summary）；调度＝外部 cron（复用 summary 模式，不内嵌）；SQLite naive datetime 兼容（received_at aware 化）。
- 自动化测试：`pytest -q` → **47 passed**（+ `test_sla` 4：超时未答→overdue、已答→不计、阈值内→不计、提示+Notification 落库；SQLite）。
- 真实端到端（uvicorn + docker PG）：插超时未答消息（demo_sla_overdue，60 分钟前 inbound 无 outbound）→ POST /sla/scan(threshold 30) → 命中 3 条超时（含 demo_sla_overdue 62 分钟）+ Notification #50(kind=sla) + 口语化提示。
- **PG 迁移备注**：notifications 表 CHECK 需含 sla；models 已改（新部署 create_all 自动），**已有 PG 库需手动 ALTER**（演示前已执行：DROP/ADD CONSTRAINT 含 sla）。
- **REQ-14 可验证口径：通过。** Sprint-11 验收完成（话题级暂停留 Sprint-12，端到端留 Sprint-13）。

---

### Sprint-12：转人工暂停话题级精化（REQ-10）

#### 目标
P1 会话级暂停 → 话题（thread）级精化：会话内某话题 handed_off 只暂停该话题，其他话题不暂停。

#### 输入文档
- `docs/02-srs.md` REQ-10、`docs/design-conversation-engine.md` §2、`docs/06-db-design.md`（conversations.topic_key）

#### 修改范围
- `backend/service/conversation/`（话题级暂停判定）、`backend/model/`（topic_key 读写）

#### 验收标准
- 会话内某话题置 handed_off → 该话题新消息不自动回复、其他话题正常。REQ-10 话题级口径通过。

#### 禁止事项
- 不做话题级非文字处理；话题识别口径待定（键策略）。

#### 验收记录（2026-06-23）
- 已实现：`models.TopicHandoff`（dcs_topic_handoffs，conversation_id+topic_key+handoff_state，UNIQUE）、`engine.topic_handed_off`（话题级判定）、`orchestrator.handle_inbound` 两级暂停（会话级 OR 话题级 handed_off → 暂停）、`api POST /conversations/{id}/topic-handoff`（置/解除某话题暂停）。
- 设计决策：话题＝`sender_external_id`（群内多客户各成一线，愿景尾注 5；键策略可调）；新表 `dcs_topic_handoffs`（一会话一话题一行）；P1 会话级 `handoff_state` 保留（整会话暂停＝话题级特例，向后兼容）；两级任一 handed_off 即暂停。
- 自动化测试：`pytest -q` → **51 passed**（+ `test_topic_handoff` 4：默认不暂停、该话题暂停/其他正常、auto 不暂停、会话隔离；SQLite）。
- 真实端到端（uvicorn + docker）：cust_A 造会话作答 → 置 cust_A 话题 handed_off → cust_A 再发**无回复**（reply_text None）→ cust_B 同会话发**正常作答**（hit true）。话题级精化生效（某话题暂停不影响其他）。
- **REQ-10 话题级口径：通过。** Sprint-12 验收完成（P2 全部功能 REQ 9/11/13/14 + 话题级 10 完成；剩 Sprint-13 端到端）。

---

### Sprint-13：P2 端到端 + 演示

#### 目标
串联 P2 全流程（多轮/身份/回写/时效/话题暂停）+ demo-ui 扩展（知识确认页面、多轮演示）。

#### 输入文档
- `docs/03-prd.md` §3、各 `docs/design-*.md`、Sprint-8~12

#### 修改范围
- `tests/`（P2 集成）、`frontend/`（demo 扩展）

#### 验收标准
- P2 全部 REQ（9/11/13/14 + 话题级 10）可验证口径通过；demo 走通 P2 流程。

#### 禁止事项
- 不做愿景/企微；不引入 P3 功能。

---

## 远期愿景 · 待技术验证

> REQ-15（企业微信外部群接入，Sprint-0 已核实群内路径不成立，待替代通道如微信客服）、REQ-16（订单进度转人工）、REQ-17（售后规则智能引导）。
> 对应 Sprint 待 Phase2 收官、升阶段后在本文**原位追加**到此分组下。

### 通道验证路线（非功能 · 对比研究）

> 真实数据的 I/O 载体验证，**非商用、不进功能范围**。完整路线与对比矩阵见 `docs/channel-validation-plan.md`；决定见 `docs/open-decisions.md` DEC-7。
> - **Step 一（模拟器）**：＝ Sprint-1，验证整体架构（先行、不阻塞）。
> - **Step 二（真实微信号 wxautox4 式）/ Step 三（合规：会话存档采集 + 飞书通知 + 微信客服回复）**：MVP 架构跑通后，作为**两个并行 Spike**，用真实数据做对比。具体 Sprint 待 MVP 完成后在此**原位追加**。
