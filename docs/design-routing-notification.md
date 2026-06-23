# design-routing-notification（路由与通知）

> 子系统详细设计。P1 给角色路由 + 口语化提醒 + 定时小结；P2 增时效监控。按 global-rules §8 积累式演进。

## 0. 定位与边界

- 职责：按场景把转交/提醒路由到对应角色；把事项以**普通消息**（口语化）发给员工/经营者；定时生成小结。
- 约束：员工/经营者侧无需登录系统（愿景明确）；业务知识归属在客户方。
- 对应：REQ-5/7/8（P1）、REQ-14（P2）。指向：`docs/04-architecture.md` §2。

## 1. 完整框架

- **路由规则**：`scenario → target_role → staff`（`dcs_routing_rules` + `dcs_staff`）。
- **通知**：`kind`(handoff/gap/summary) + 接收人 + 口语化 `body`，经出站通道发送，落 `dcs_notifications`。
- **小结**：按时间窗口聚合消息量/类型/需跟进清单（含已分给谁），生成经营者小结。

## 2. P1 细节 `[P1]` `[P1-已设计]`

- **角色路由（REQ-5/8）**：
  - 场景→角色示例：`presale→sales`、`unknown_question→owner`（拍板人）、`order→merchandiser`、`aftersale→tech`（售后在愿景阶段，但路由占位可用）。
  - 规则可经 `/api/v1/routing-rules` 配置；`role` 解析到在岗 `staff`。
- **口语化提醒（REQ-5）**：
  - 模板示例（售前）：「{时间}，{客户}对{主题}满意并留了联系方式（{脱敏号}），可能需要您跟进{动作}。」
  - 经出站通道发为普通消息；同时写 `dcs_handoffs` + `dcs_notifications`。
  - **员工侧出站通道＝飞书机器人**〔据 `docs/context-and-constraints.md`：内部 IM=飞书〕；MVP 可用飞书 custom robot webhook（接入简单），日报同走飞书。
- **定时小结（REQ-7）**：
  - 调度触发 `POST /api/v1/summaries/daily`（也可手动触发测试）；
  - 聚合 `dcs_messages`（量/类型）、`dcs_handoffs`（需跟进清单 + 目标）；
  - 生成小结文案发经营者，落 `dcs_notifications`(kind=summary)。
  - 模板示例：「今天共 {N} 条客户消息，多为{类型}，已自动回复；其中 {K} 条需跟进（{明细}），均已通知对应同事。」（对齐愿景中午/傍晚小结）。

## 3. P2 / 愿景骨架

### 3.1 时效监控（REQ-14）`[P2]` `[P2-已设计]`

扫描「客户消息 → 首次应答」间隔，对 > 阈值未回复者提示。

- **计时口径**：每会话最后一条客户消息(inbound)，若同会话无 received_at 更晚的 outbound（AI 应答）且 received_at 距今 > 阈值 → 超时未答。
- **扫描接口**：`POST /api/v1/sla/scan`（手动触发 / 部署层 cron 定时调，复用 §2 小结的外部 cron 调度模式）；入参可选 `threshold_minutes`，默认取配置。
- **超时提示**：扫描返回超时列表 + 写 `dcs_notifications`(kind=sla) 发经营者（口语化「{群} 的客户消息已 {N} 分钟未回复，请关注」）。
- **阈值**：默认 30 分钟（愿景口径），`config.sla_threshold_minutes` 可配。
- **边界**：只统计「客户消息后无应答」；AI 已答(outbound)的不计；告警渠道＝飞书（同 §2）；超时口径待真实场景调参。

### 3.2 订单进度转交（REQ-16）`[愿景]` `[骨架·依赖外部系统]`
依赖外部订单/生产记录系统；本子系统仅负责「转给跟单人 + 附订单信息」的通知部分，进度数据来源不在本期。

## 4. 风险

- 小结/提醒的「口语化」质量影响经营者体验；模板优先、LLM 仅做润色且须可回退到模板，避免出现「系统报表腔」（与愿景定位冲突）。

---

**追溯**：REQ-5/7/8/14/16；表见 `docs/06-db-design.md`（dcs_staff/routing_rules/handoffs/notifications）；接口见 `docs/07-api-spec.md` §3.3/3.4。
