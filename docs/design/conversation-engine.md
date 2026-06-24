# design-conversation-engine（对话编排）

> 子系统详细设计。本系统最复杂的子系统；P1 给单轮主路径与分支，P2/愿景分支留骨架。按 global-rules §8 积累式演进。

## 0. 定位与边界

- 职责：对一条归一化消息决定「怎么回」——走知识作答 / 留资 / 缺口转人 / 转人工，以及 P2 的多轮·暂停·身份·非文字分支。
- 依赖：知识库（检索/缺口）、路由与通知（转交/提醒）、会话与记录（状态）。
- 对应：REQ-2/3/4/5/6（P1）、REQ-9/10/11/12（P2）。指向：`docs/04-architecture.md` §2。

## 1. 完整框架（编排决策树）

```
收到 NormalizedMessage
 ├─ [P1/P2] handoff 暂停（会话级 P1 conversations.handoff_state，或话题级 P2
 │           dcs_topic_handoffs 该 sender）= handed_off → 暂停自动回复（REQ-10，仅记录）
 ├─ [P1] content_type != text → 非文字如实告知 + 提醒员工（REQ-12）
 ├─ [P2] 命中「是否AI」意图 → 身份披露（REQ-11）
 ├─ [P2] 有 collecting 询盘 → 多轮接续（匹配客户回复到当前项，REQ-9）
 ├─ [P2] 命中「定制询盘」意图 → 新建多轮引导（抽值预填 + 首轮，REQ-9）
 └─ [P1] 文本 → 知识检索（design-knowledge-base，REQ-2/3）
       ├─ 命中（confirmed）→ 作答回客户
       └─ 未命中 → 缺口分支：抽取留资（REQ-4）+ 客户侧请留资（REQ-6）
                   + 员工侧路由转交拍板人（REQ-5/8）
```

## 2. P1 细节 `[P1]` `[P1-已设计]`

- **主路径＝检索作答**：调 `knowledge.search`，命中 confirmed 条目则生成作答（限定在检索内容内，带来源/置信度，不编造），经出站回客户。
- **未命中＝缺口分支**（一等公民）：
  1. 写 `dcs_knowledge_gaps`(open)；
  2. 尝试抽取留资（手机号等可校验模式）→ 写 `dcs_leads`（脱敏）；
  3. 客户侧出站：请留资 + 「将请同事确认」；
  4. 经路由（`design-routing-notification`）转交拍板人/相关角色，写 `dcs_handoffs`。
- **留资识别**：单条消息内用可校验模式抽取联系方式；无联系方式不产生留资记录（REQ-4 可验证口径）。
- **非文字降级（P1 占位）**：P1 收到非文字消息按「记录 + 提醒人工查看」处理，**不声称理解**；完整非文字分支在 P2（REQ-12）。
- **可控性约束（两层）**：① **产品红线（永久）**——不编造：无知识依据不生成事实（产品参数/退换结论/进度，与愿景「不乱猜」一致）；② **Demo 实现（当前）**——作答＝知识库检索 answer 原文直回，不 LLM 改写（最简保红线）；③ **未来**——可在 RAG 检索内容限定内引入 LLM（润色/多轮措辞，不生成新事实）。
- **转人工后暂停（REQ-10，P1）**：会话置 `handed_off` 后，新入站客户消息不触发自动作答/缺口（仅记录、必要时提醒已接管员工）；经接口解除标记后才恢复。P1 为会话级。
- **非文字处理（REQ-12，P1）**：`content_type != text` 时，群内如实告知无法识别 + 提醒员工查看，不生成对内容的作答（内容理解永久非目标）。

## 3. P2 / 愿景骨架

### 3.1 多轮引导（REQ-9）`[P2]` `[P2-已实现]`

定制询盘（堆叠多要求）→ 拆项 → 多轮逐条确认 → 收集 → 可核价摘要转交。

- **意图识别 + 拆项（规则，不引 LLM）**：文本含定制类关键词（定制/定做/我要做…）→ 识别为定制询盘；**抽值预填**——颜色/数量/Logo/交期 用正则抽客户陈述的值预填 `collected`，系统只追问未陈述维度（`pending`），不重复问；未陈述规格时用默认核心维度（颜色/数量/Logo/交期）。纯规则，守 §2 可控性约束（不 LLM 生成）。
- **状态落新表 `dcs_inquiries`**（询盘级生命周期，不污染 conversations）：`status`(collecting/completed/abandoned)、`items_pending`/`items_collected`(jsonb)、`summary`(text)、`conversation_id`(FK)。见 `06-db-design.md`。
- **状态机**：新询盘 → 建 inquiry(collecting) + 出站确认第 1 项；客户回复 → 匹配当前 pending 项 → 移入 collected → 确认下一项；全部 collected → 生成可核价摘要 → 转交（handoff `scenario=custom_inquiry` + 通知跟单）→ inquiry=completed。
- **编排接入点**（`handle_inbound` 文本分支，多轮优先）：文本时先查 conv 的 collecting inquiry → 有则接续（匹配回复到 pending）；无则 `detect_custom_inquiry` → 命中则建 inquiry + 首轮；否则原 `orchestrate`（检索/缺口）。即正在多轮的会话优先接续，检索兜底。
- **未应答兜底**：客户发「跳过/没有了/就这些」→ 结束收集转已收集项；回复不匹配当前项 → 重申当前问题（不强行匹配）；超时留 Sprint-11 SLA。
- **可核价摘要模板**：「定制询盘：尺寸=X / 颜色=Y / 数量=Z / …（跳过项标注）」→ 转交跟单核价。

### 3.2 身份披露（REQ-11）`[P2]` `[P2-已实现]`

被问「是不是AI/机器人」时，按既定口径自然承认身份，不喧宾夺主。

- **意图识别（规则，不引 LLM）**：文本命中身份询问模式（你是机器人/真人/AI、是不是…、你是程序/自动回复…）→ 触发。纯规则，守 §2 可控性约束。
- **既定话术**：「我是小辰，汇辰灯饰的 AI 客服助理 🤖 能帮您查产品参数、记需求转同事跟进。有什么可以帮您的？」——承认身份 + 角色 + 回归服务，不躲闪、不喧宾夺主。
- **编排接入点**（`handle_inbound` 文本分支**最前**，身份优先于多轮/检索）：文本时先判身份询问 → 命中则披露（写 outbound 话术，单轮）；否则走多轮/定制/检索。
- **边界**：**被动披露**（只在被问时承认，不主动）；单轮（问→答，不拉多轮）；不触发缺口/转交。

### 3.3 转人工暂停话题级（REQ-10）`[P2]` `[P2-已实现]`

P1 会话级暂停 → 话题（thread）级精化：会话内某话题 handed_off 只暂停该话题，其他话题正常。

- **话题口径**：话题 = 客户（`sender_external_id`）——群内多客户交叉（愿景尾注 5）各成一线；每客户一个话题。键策略可调。
- **数据**：新表 `dcs_topic_handoffs`(conversation_id, topic_key, handoff_state)，记某话题暂停状态；P1 会话级 `conversations.handoff_state` 保留（整会话暂停＝话题级特例）。
- **编排接入**（`handle_inbound`）：会话级 `handed_off`(P1) **或** 话题级 (conv.id, sender) `handed_off`(P2) → 该消息暂停（仅记录）；两级任一即暂停。
- **接口**：`POST /api/v1/conversations/{id}/topic-handoff` `{topic_key, handoff_state}` 置/解除某话题暂停。
- **边界**：话题级非文字处理不做（非文字仍走会话级 §2）；P1 会话级向后兼容。

### 3.4 售后规则引导（REQ-17）`[愿景]` `[骨架·高风险AI]`
高风险 AI 推理（质保边界判定/安抚话术），待技术验证后才细化，不进当前阶段。

## 4. 风险

- 多轮状态机、售后推理是复杂度高/风险高的部分，刻意推迟；P1 用「检索 + 缺口转人」覆盖愿景大多数单轮场景，保证可控。

---

**追溯**：REQ-2/3/4/5/6/9/10/11/12/17；联动见 `design/knowledge-base.md`、`design/routing-notification.md`、`design/channel-adapter.md`。
