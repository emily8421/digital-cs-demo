# 06 数据库设计

> AI 生成初稿，**人工确认**。完整表清单 + 阶段标签/状态；**P1 表写全字段/索引，P2/愿景表留骨架**。按 global-rules §8 积累式演进（只增不删、原位细化）。
> 引擎：PostgreSQL（版本待确认，见 05）。表前缀 `dcs_`。

## 1. 表清单

| 表 | 用途 | 对应 REQ | 阶段 | 状态 |
|---|---|---|---|---|
| `dcs_messages` | 入站/出站消息原始与归一化记录 | REQ-1 | P1 | P1-已设计 |
| `dcs_conversations` | 会话（群/话题）与会话级状态 | REQ-1/5/10 | P1（handoff_state 供 REQ-10 暂停消费） | P1-已设计 |
| `dcs_knowledge_items` | 知识条目（FAQ/参数/选型）及其确认状态 | REQ-2/3/13 | P1 + P2 回写 | P1-已设计 |
| `dcs_knowledge_gaps` | 答不上的缺口问题记录 | REQ-6 | P1 | P1-已设计 |
| `dcs_leads` | 识别出的客户留资（联系方式） | REQ-4 | P1 | P1-已设计 |
| `dcs_handoffs` | 转人工/转交记录（对象/原因/上下文/状态） | REQ-5/8/10 | P1（暂停已 P1） | P1-已设计 |
| `dcs_staff` | 员工/角色花名册与对接通道 | REQ-5/8 | P1 | P1-已设计 |
| `dcs_routing_rules` | 场景→角色路由规则 | REQ-8 | P1 | P1-已设计 |
| `dcs_notifications` | 出站提醒与定时小结的发送记录 | REQ-5/7 | P1 + P2 时效 | P1-已设计 |
| `dcs_inquiries` | 定制询盘多轮收集状态 | REQ-9 | P2 | P2-已设计 |
| `dcs_orders` | 订单/进度（售中转人工依赖） | REQ-16 | 愿景·待技术验证 | 骨架·待细化 |

## 2. 表结构（P1 表详写；愿景表骨架）

### dcs_messages `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | 主键 |
| conversation_id | bigint | NOT NULL, FK→dcs_conversations.id | 所属会话 |
| direction | varchar(16) | NOT NULL, CHECK in(inbound,outbound) | 方向 |
| channel | varchar(32) | NOT NULL | 来源通道：simulator / wework |
| sender_external_id | varchar(128) | NOT NULL | 发送方外部标识（客户/群成员） |
| content_type | varchar(16) | NOT NULL, CHECK in(text,voice,image,video,other) | 内容类型 |
| content_text | text |  | 文本内容（非文字类型可为空） |
| raw_payload | jsonb |  | 平台原始报文（归一化前） |
| received_at | timestamptz | NOT NULL | 接收时间 |
| created_at | timestamptz | NOT NULL default now() | 入库时间 |

### dcs_conversations `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| external_group_id | varchar(128) | NOT NULL | 外部群标识（企业微信群/模拟器群） |
| topic_key | varchar(128) |  | 话题键（P1 暂停按会话级；话题级精化时用，目前可空） |
| handoff_state | varchar(16) | NOT NULL default auto, CHECK in(auto,handed_off) | 是否已转人工（P1 编排消费：handed_off 时暂停自动回复） |
| last_active_at | timestamptz | NOT NULL | 最近活动时间（小结/时效用） |
| created_at | timestamptz | NOT NULL default now() | |

### dcs_knowledge_items `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| question_pattern | text | NOT NULL | 问题/意图描述 |
| answer | text | NOT NULL | 标准答案 |
| category | varchar(64) |  | 分类（参数/选型/采购 FAQ…） |
| embedding | vector |  | 向量（随向量库选型，待确认字段类型） |
| status | varchar(16) | NOT NULL default confirmed, CHECK in(confirmed,pending) | confirmed＝已确认可答；pending＝P2 待确认回写 |
| source_staff_id | bigint | FK→dcs_staff.id | 内容来源（确认人） |
| created_at / updated_at | timestamptz | NOT NULL | |

### dcs_knowledge_gaps `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| conversation_id | bigint | FK→dcs_conversations.id | 来源会话 |
| question_text | text | NOT NULL | 客户原问题 |
| detected_at | timestamptz | NOT NULL | 发现时间 |
| status | varchar(16) | NOT NULL default open, CHECK in(open,resolved) | 是否已补答 |
| resolved_knowledge_id | bigint | FK→dcs_knowledge_items.id | 解决后回填的知识条目（P2 回写链路） |

### dcs_leads `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| conversation_id | bigint | FK→dcs_conversations.id | |
| contact_type | varchar(16) | NOT NULL, CHECK in(phone,…) | 联系方式类型 |
| contact_value_masked | varchar(64) | NOT NULL | 脱敏值（如 138****6677） |
| contact_value_enc | bytea |  | 加密原文（合规存储，访问受限） |
| captured_at | timestamptz | NOT NULL | |
| note | text |  | 留资语境摘要 |

### dcs_handoffs `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| conversation_id | bigint | FK→dcs_conversations.id | |
| scenario | varchar(32) | NOT NULL | 场景：presale/aftersale/order/unknown_question/… |
| target_staff_id | bigint | FK→dcs_staff.id | 转交对象（路由结果） |
| reason | text | NOT NULL | 转交原因/摘要 |
| context_ref | jsonb |  | 附带上文（订单号/购买时间/证据指针等） |
| status | varchar(16) | NOT NULL default open, CHECK in(open,accepted,closed) | |
| created_at | timestamptz | NOT NULL default now() | |

### dcs_staff `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| name | varchar(64) | NOT NULL | 姓名（如 小雯/阿杰/老黄/陈总） |
| role | varchar(32) | NOT NULL | 角色：sales/tech/merchandiser/owner |
| external_id | varchar(128) |  | 接收提醒的外部标识（企业微信 userid 等） |
| active | boolean | NOT NULL default true | 是否在岗 |

### dcs_routing_rules `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| scenario | varchar(32) | NOT NULL UNIQUE | 场景键（与 handoffs.scenario 对齐） |
| target_role | varchar(32) | NOT NULL | 目标角色（解析到具体 staff） |
| priority | int | NOT NULL default 0 | 多规则优先级 |

### dcs_notifications `[P1]`
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| kind | varchar(16) | NOT NULL, CHECK in(handoff,summary,gap,… ) | 类型 |
| target_staff_id | bigint | FK→dcs_staff.id | 接收人（小结可为经营者） |
| channel | varchar(32) | NOT NULL | 出站通道 |
| body | text | NOT NULL | 文案（口语化） |
| sent_at | timestamptz | NOT NULL | |
| ref_handoff_id / ref_gap_id | bigint |  | 关联转交/缺口 |

### dcs_inquiries `[P2]` `[P2-已设计]`
定制询盘多轮收集（REQ-9）：一询盘一行，记录拆项/收集/摘要/转交状态。
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | bigserial | PK | |
| conversation_id | bigint | NOT NULL, FK→dcs_conversations.id | 所属会话 |
| status | varchar(16) | NOT NULL default collecting, CHECK in(collecting,completed,abandoned) | 询盘状态 |
| items_pending | jsonb | NOT NULL default '[]' | 待确认维度（如 ["尺寸","颜色","数量","Logo"]） |
| items_collected | jsonb | NOT NULL default '{}' | 已收集 {维度:值}（如 {"颜色":"蓝","数量":"100米"}） |
| current_item | varchar(32) |  | 当前确认维度（items_pending[0] 镜像，便于查询） |
| summary | text |  | 可核价摘要（completed 时生成） |
| created_at / updated_at | timestamptz | NOT NULL default now() | |
| completed_at | timestamptz |  | 完成/转交时间 |

### dcs_orders `[愿景·待技术验证]` `[骨架·待细化]`
订单/进度表，依赖外部订单或生产记录系统是否存在与可集成（REQ-16）。字段待外部系统确定后补：订单号、产品、客户标识、工序进度、来源系统指针等。**本期不实现、不建表**，仅占位说明。

## 3. 索引设计（P1）

- `dcs_messages`：`(conversation_id, received_at)`——按会话拉取消息流；`(channel, received_at)`——按通道/时间审计。
- `dcs_conversations`：`(external_group_id)`——按群定位会话；`(last_active_at)`——小结与时效扫描。
- `dcs_knowledge_items`：`(status)` 过滤可答条目；`embedding` 向量索引（类型随向量库待确认，如 ivfflat/hnsw）。
- `dcs_knowledge_gaps`：`(status)` 找未解决缺口。
- `dcs_leads`：`(conversation_id)`。
- `dcs_handoffs`：`(conversation_id, created_at)`、`(target_staff_id, status)`——员工待办视图。
- `dcs_routing_rules`：`scenario` 唯一索引（已含）。
- `dcs_inquiries`：`(conversation_id, status)`——查某会话进行中(collecting)的询盘；`(status)`——统计/扫尾（P2 落地补）。

## 4. 表间关系

- `conversations 1—N messages`、`conversations 1—N leads`、`conversations 1—N handoffs`、`conversations 1—N knowledge_gaps`、`conversations 1—N inquiries`。
- `handoffs N—1 routing_rules`(经 scenario)、`handoffs N—1 staff`(目标)。
- `knowledge_gaps 1—1 knowledge_items`(resolved 链路，P2 回写)。
- `staff 1—N notifications`、`staff 1—N knowledge_items`(来源确认人)。
- `orders`(愿景) 经订单号与 `handoffs.context_ref` 弱关联，不强制外键（外部系统）。

---

**追溯**：每张表对应 REQ 见 §1；接口读写见 `docs/07-api-spec.md`；子系统逻辑见各 `design-*.md`。
