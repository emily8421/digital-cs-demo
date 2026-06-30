# 07 API设计

> **文档定位**：定义 REST / Webhook / 内部通道契约的统一约定、接口清单、请求响应、错误码和权限边界。
> **上游输入**：`docs/02-srs.md`、`docs/03-prd.md`、`docs/04-architecture.md`、`docs/05-tech-spec.md`。
> **下游输出**：约束 API 层、演示 UI、集成测试和验收用例。
> AI 生成初稿，**人工确认**。完整接口清单 + 阶段标签/状态；**P1 接口写请求/响应示例，P2/愿景接口留骨架**。按 global-rules §8 积累式演进。
> 风格：REST + Webhook 回调；统一响应格式。版本前缀 `/api/v1`（Webhook 回调路径例外）。

## 0. 文档元信息

| 项 | 内容 |
|---|---|
| 保留 / 省略决策 | 保留 |
| 接口形态 | REST + 内部通道适配契约 |
| 覆盖 REQ / 模块 | REQ-1~REQ-14；REQ-15/16/17 仅保留愿景骨架 |
| 当前状态 | 已确认（P1+P2 Demo 收官；愿景待技术验证） |
| 最后更新 | 2026-06-29 |

## 1. 统一约定

- **统一响应格式**（管理 API）：
  ```json
  { "code": 0, "message": "ok", "data": { } }
  ```
  `code=0` 成功；非 0 见错误码。Webhook 回调按平台要求返回（如 200 + `"success"`）。
- **错误码体系**（节选）：
  | code | 含义 |
  |---|---|
  | 0 | 成功 |
  | 1000 | 参数错误 |
  | 1001 | 未授权 |
  | 2001 | 知识未命中（业务语义，非错误，用于编排） |
  | 5000 | 内部错误 |
- **鉴权**：管理 API 用 Token（待确认方案，候选固定 Token / OAuth）；Webhook 用平台签名校验（企业微信，待验证）。→ 待确认。
- **通道无关**：所有业务接口不感知企业微信/模拟器差异；通道差异收敛在 `/webhooks/*` 与 `/messages/simulate`。

## 2. 接口清单

| 方法 | 路径 | 用途 | 对应 REQ | 阶段 | 状态 |
|---|---|---|---|---|---|
| POST | `/webhooks/wework/message` | 企业微信消息回调（入站） | REQ-1/15 | 愿景·待验证 | 骨架·待验证 |
| POST | `/api/v1/messages/simulate` | 模拟器投递一条入站消息 | REQ-1 | P1 | P1-已实现 |
| GET | `/api/v1/conversations` | 会话列表 | REQ-1 | P1 | P1-已实现 |
| GET | `/api/v1/conversations/{id}` | 会话详情（含消息流） | REQ-1 | P1 | P1-已实现 |
| POST | `/api/v1/conversations/{id}/handoff-state` | 置/解除**会话级**转人工暂停 | REQ-10 | P1 | P1-已实现 |
| POST | `/api/v1/conversations/{id}/topic-handoff` | 置/解除**话题级**转人工暂停 | REQ-10 | P2 | P2-已实现 |
| GET | `/api/v1/knowledge/search?q=` | 知识检索 | REQ-2/3 | P1 | P1-已实现 |
| GET | `/api/v1/knowledge/gaps` | 列 open 缺口（供拍板人补答） | REQ-13 | P2 | P2-已实现 |
| POST | `/api/v1/knowledge/gaps/{id}/answer` | 拍板人补答 → 创建 pending | REQ-13 | P2 | P2-已实现 |
| GET | `/api/v1/knowledge/pending` | 列 pending（供确认） | REQ-13 | P2 | P2-已实现 |
| POST | `/api/v1/knowledge/{id}/confirm` | 确认 pending → confirmed + 回填 gap | REQ-13 | P2 | P2-已实现 |
| POST | `/api/v1/handoffs` | 人工转交（建记录 + 路由 + 通知） | REQ-5/8 | P1 | P1-已实现 |
| POST | `/api/v1/summaries/daily` | 触发定时小结（手动/调度） | REQ-7 | P1 | P1-已实现 |
| POST | `/api/v1/sla/scan` | 扫描超时未答 + 提示经营者 | REQ-14 | P2 | P2-已实现 |
| GET | `/api/v1/orders/{id}/progress` | 订单进度（售中） | REQ-16 | 愿景·待验证 | 骨架·依赖外部系统 |

> 注：知识/留资/员工/路由规则的 CRUD 经种子脚本（`scripts/seed_*.py`）与编排内部调用，未开 REST 接口（需时再议）。

## 3. 请求 / 响应示例（P1）

### 3.1 POST `/api/v1/messages/simulate`（模拟器入站） `[P1]`
请求：
```json
{
  "external_group_id": "sim_group_001",
  "sender_external_id": "cust_laozhou",
  "content_type": "text",
  "content_text": "5050灯带和2835防水等级有啥区别，能做IP67吗？",
  "received_at": "2026-06-20T02:00:00+08:00"
}
```
响应（编排后异步产生回包；接口本身仅 ACK）：
```json
{ "code": 0, "message": "ok", "data": { "message_id": 1001, "conversation_id": 57 } }
```
编排副作用（出站，经通道）：客户侧作答（命中知识库）或请留资（缺口）。

### 3.2 GET `/api/v1/knowledge/search?q=` `[P1]`
`GET /api/v1/knowledge/search?q=IP65%20IP67%20区别`
```json
{
  "code": 0, "message": "ok",
  "data": {
    "hit": true,
    "items": [
      { "id": 12, "question_pattern": "IP65与IP67区别", "answer": "IP65 防喷水…IP67 可短时浸水…", "score": 0.91, "status": "confirmed" }
    ]
  }
}
```
未命中时 `hit:false, items:[]`（编排据此走缺口流程 REQ-6）。

### 3.3 POST `/api/v1/handoffs`（人工转交，含路由） `[P1]`
请求：
```json
{
  "conversation_id": 57,
  "scenario": "presale",
  "reason": "客户对灯带选型满意并留资，需跟进报价",
  "context_ref": { "lead_id": 33, "topic": "灯带选型" }
}
```
响应（路由解析到目标员工并触发通知）：
```json
{
  "code": 0, "message": "ok",
  "data": { "handoff_id": 88, "target_staff_id": 7, "target_role": "sales", "notification_id": 201 }
}
```

### 3.4 POST `/api/v1/summaries/daily`（触发小结） `[P1]`
请求：`{ "target_role": "owner", "window": "today" }` 或定时调度无 body。
响应（小结文案作为出站消息发送给经营者，接口返回摘要）：
```json
{
  "code": 0, "message": "ok",
  "data": {
    "notification_id": 305,
    "summary": "今天上午共 26 条客户消息，多为产品参数与订单基础问题，已自动回复；其中 3 条需跟进（老周报价、工程定制询盘、一条语音消息），均已通知对应同事。"
  }
}
```

### 3.5 P2 / 愿景接口（骨架）

- **GET `/api/v1/knowledge/gaps`** `[P2]`：列 open 缺口（供拍板人补答）。响应 `{ data: { gaps: [{ id, question_text, detected_at }] } }`。
- **POST `/api/v1/knowledge/gaps/{gap_id}/answer`** `[P2]`：拍板人对缺口补答 → 创建 pending 条目（关联 gap）。请求 `{ answer, staff_id }`；响应 `{ data: { knowledge_id, status: "pending" } }`（`question_pattern` 取 gap.question_text、生成 embedding、`source_staff_id`=staff_id）。
- **GET `/api/v1/knowledge/pending`** `[P2]`：列 pending 条目（供拍板人确认）。响应 `{ data: { items: [{ id, question_pattern, answer, source_staff_id }] } }`。
- **POST `/api/v1/knowledge/{id}/confirm`** `[P2]`：拍板人确认 pending → confirmed + 回填 gap。请求 `{ staff_id }`；响应 `{ data: { id, status: "confirmed", resolved_gap_id } }`（记 `source_staff_id`、关联 gap `status=resolved` + `resolved_knowledge_id`）。
- **POST `/api/v1/sla/scan`** `[P2]`：扫描超时未答的客户消息（inbound 后同会话无 outbound 且距今 > 阈值）。请求可选 `{ threshold_minutes }`（默认取配置 30）；响应 `{ data: { overdues: [{conversation_id, group, message_id, overdue_minutes}], count, notification_id } }`，写 `dcs_notifications`(kind=sla) 提示经营者。
- **POST `/api/v1/conversations/{id}/topic-handoff`** `[P2]`：置/解除某话题转人工暂停（REQ-10 话题级）。请求 `{ topic_key, handoff_state }`；响应 `{ data: { conversation_id, topic_key, handoff_state } }`（topic_key 原型＝sender_external_id 客户）。
- **GET `/api/v1/orders/{id}/progress`** `[愿景]`：订单工序进度；依赖外部订单/生产系统集成存在性，未确定前不实现，仅占位。

---

**追溯**：接口对应 REQ 见 §2；读写的数据表见 `docs/06-db-design.md`；编排逻辑见 `docs/design/conversation-engine.md`。

## 4. REQ → 接口追溯矩阵

| REQ | 接口 / 契约 | 阶段 | 状态 | 备注 |
|---|---|---|---|---|
| REQ-1 | `POST /api/v1/messages/simulate`、`GET /api/v1/conversations`、`GET /api/v1/conversations/{id}`、通道适配契约 | P1 | 已实现 | 模拟器通道验证归一化消息管线 |
| REQ-2/3 | `GET /api/v1/knowledge/search?q=` | P1 | 已实现 | 知识命中直回；未命中供编排进入 REQ-6 |
| REQ-5/8 | `POST /api/v1/handoffs` | P1 | 已实现 | 建转交记录、按角色路由并生成通知 |
| REQ-7 | `POST /api/v1/summaries/daily` | P1 | 已实现 | Demo 手动触发；生产形态由外部 cron 调用 |
| REQ-10 | `POST /api/v1/conversations/{id}/handoff-state`、`POST /api/v1/conversations/{id}/topic-handoff` | P1/P2 | 已实现 | 会话级 + 话题级暂停 |
| REQ-13 | `GET /api/v1/knowledge/gaps`、`POST /api/v1/knowledge/gaps/{id}/answer`、`GET /api/v1/knowledge/pending`、`POST /api/v1/knowledge/{id}/confirm` | P2 | 已实现 | 拍板人补答、确认后回写知识库 |
| REQ-14 | `POST /api/v1/sla/scan` | P2 | 已实现 | Demo 手动触发；生产形态由外部 cron 调用 |
| REQ-15 | `/webhooks/wework/message` / 真实客户入口契约 | 愿景·待技术验证 | 骨架 | 企业微信客户群路径已证伪；替代通道待 Spike |
| REQ-16 | `GET /api/v1/orders/{id}/progress` | 愿景·待技术验证 | 骨架 | 依赖外部订单 / 生产系统 |
| REQ-17 | 售后规则接口 / 知识边界契约 | 愿景·待技术验证 | 未定义 | 待售后规则和高风险 AI 边界确认 |
