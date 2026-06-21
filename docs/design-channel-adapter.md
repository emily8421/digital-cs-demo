# design-channel-adapter（通道适配层）

> 子系统详细设计。与 04（总体）/06-07（数据·接口）互补，承载子系统内部逻辑。按 global-rules §8 积累式演进。
> **核心认知**：合规风险集中在 I/O 边界（采集客户群消息 + 自动回复客户）；中间架构（检测/判定/通知/存档）合规中性。本层职责＝把 I/O 风险隔离在一层适配器里，业务层平台无关。

## 0. 定位与边界

- 职责：消息归一化（入站）+ 出站适配（发回客户/员工）；隔离平台差异与合规风险。
- 三种通道实现（**共用同一契约、可替换**）：
  - `simulator`（模拟器）— 保底，验证架构（P1）
  - `wxautox-real`（真实微信号，wxautox4 式）— 真实数据，灰路径，**非商用对比**
  - `official-compliant`（企业微信会话存档采集 + 飞书通知 + 微信客服回复）— 真实数据，合规
- 不做：业务判断、知识检索、路由（这些都由对话编排/知识库/路由子系统负责）。
- 对应：REQ-1（P1）、REQ-15（愿景·待验证）。指向：`docs/04-architecture.md` §2、`docs/channel-validation-plan.md`。

## 1. 完整框架

- **统一消息契约（NormalizedMessage）**：`conversation_ref`(external_group_id/topic)、`sender_external_id`、`content_type`(text/voice/image/video/other)、`content_text`、`raw_payload`、`received_at`。
- **入站适配器接口**：`InboundChannel.receive() -> NormalizedMessage`。
- **出站适配器接口**：`OutboundChannel.send(target, body, kind) -> send_result`（回客户群 / 发员工提醒 / 发经营者小结）。
- **通道注册**：按 `channel` 标识路由到三个实现之一；业务层只依赖契约，**不感知平台与合规差异**。
- 三通道**并列、共用契约、可替换**——这是三步验证路线（见 `docs/channel-validation-plan.md`）的基础。

## 2. P1 细节（模拟器通道） `[P1]` `[P1-已设计]`

- **模拟器通道（保底，必做）**：
  - 入站：`POST /api/v1/messages/simulate`（见 07 §3.1）直接构造 `NormalizedMessage` 投入编排。
  - 出站：回包写入 `dcs_messages`（direction=outbound）并可在测试界面回显，**不依赖任何外部平台即可演示完整闭环**。
- **归一化要点**：非文字类型（voice/image/video）`content_text` 置空、`content_type` 标记，交由对话编排走「非文字处理」分支（REQ-12，P1）：群内如实告知 + 提醒人工，**不声称理解内容**。

## 3. 真实通道（验证项 · 非 P1 功能 · 非商用对比）

> Sprint-0 已核实（见 `docs/sprint-0-wework-findings.md`）：企业微信「客户群群内被动监听 + 自动回复外部用户」在官方能力下**不成立**（智能机器人 `from.userid`=企业成员、消息推送只发不收、会话存档禁自动回复）。故真实数据验证改为**两条并行 I/O 载体对比**：

- **`wxautox-real`（灰路径）**：真实微信号经 wxautox4/UIAutomation 采集（可覆盖任意群，含外部微信客户群）+ 可发送。
  - ⚠️ 违微信协议（封号）、锁版本脆弱、单点；作者禁商用。**仅非商用对比**；风险 containment：专用测试号、隔离测试群、优先只读采集、回复最谨慎、数据 demo 后清理（见 channel-validation-plan §3、DEC-7）。
- **`official-compliant`（合规）**：企业微信**会话内容存档**采集（合规、需客户同意/企业认证/付费/有小延迟）+ **飞书**官方 API @负责人/日报 + **微信客服** 1:1 做 AI 自动应答。
  - 局限：会话存档**禁止用于自动回复** → 群内自动回复这一步做不到，改走微信客服 1:1 或由飞书通知驱动人工。
- **对比产出**：覆盖范围 / 延迟 / 采集合规 / 自动回复合规 / 稳定性 / 成本 / 能力边界 的对照矩阵（见 channel-validation-plan §2），回答「合规要付出什么代价」。

## 4. 风险

- **合规风险集中在 I/O 边界**（采集 + 自动回复），中间架构合规中性——这是通道抽象的存在理由。
- `wxautox-real`：封号 / 版本锁定 / 单点 / 个保法（客户未必同意被监听）；read 风险 < write 风险；**严格封在本适配层，抽掉不影响架构与合规路径**。
- `official-compliant`：会话存档门槛（认证/付费/同意/延迟）；群内自动回复受限。
- `simulator`：无外部依赖、无合规风险——故 P1 以它为唯一通道。

---

**追溯**：REQ-1/15；接口见 `docs/07-api-spec.md` §3.1/§2；数据见 `docs/06-db-design.md`（dcs_messages）；验证路线见 `docs/channel-validation-plan.md`；决定见 `docs/open-decisions.md` DEC-7。
