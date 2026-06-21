# design-knowledge-base（知识库 / RAG）

> 子系统详细设计。P1 给检索 + 缺口检测；P2 给确认回写。按 global-rules §8 积累式演进。

## 0. 定位与边界

- 职责：知识检索与作答、缺口检测；P2 增「确认回写」。业务知识的归属与决定权在客户方（拍板人），系统只整理录入。
- 对应：REQ-2/3/6（P1）、REQ-13（P2）。指向：`docs/04-architecture.md` §2。

## 1. 完整框架

- **知识条目**：`question_pattern` + `answer` + `category` + `embedding` + `status`(confirmed/pending)。
- **检索**：query → embedding → 向量相似检索 → 阈值判定命中/未命中。
- **缺口**：未命中即记 `dcs_knowledge_gaps`，交对话编排走留资转人。
- **回写（P2）**：拍板人答复 → pending → 征询确认 → confirmed。

## 2. P1 细节 `[P1]` `[P1-已设计]`

- **检索接口**：`GET /api/v1/knowledge/search?q=`（07 §3.2），返回 `hit` 与带 `score` 的 `items`。
- **命中口径**：仅返回 `status=confirmed` 且相似度 ≥ 阈值者；阈值待调参（待确认）。命中作答限定在条目内容内。
- **缺口口径**：未命中 → 写 `dcs_knowledge_gaps`(open)，原文留存，供拍板人查看；编排据此请客户留资并转人。
- **标准 FAQ（REQ-3）**：起订量/交期/付款等以「问题模式 + 带具体数字答案」配置，数字来自已配置值，非杜撰。
- **种子数据**：以愿景中的灯带/驱动参数为示例种子（IP65/67、5050/2835、户外型号等），用于演示与测试。

## 3. P2 / 愿景骨架

- `[P2]` **确认回写（REQ-13）**：
  - 拍板人答复缺口后，生成 `status=pending` 条目；
  - 系统征询「是否作为以后标准答案」；
  - 经 `POST /api/v1/knowledge/{id}/confirm` 确认 → 置 confirmed，记 `source_staff_id`；
  - 待细化：征询时机/交互载体（消息内 vs 轻量页面）、版本与归属、撤销。
- `[愿景]` 无额外项；售后推理（REQ-17）属对话编排，不在本子系统。

## 4. 风险

- 中文向量化质量与阈值直接影响「命中/缺口」判定，需评测（embedding 选型见 05 §1 待确认）。
- 防止把临时性回答误固化为标准答案——P1 不做回写，P2 回写必须经确认（与愿景 v4.0 调整点 5 一致）。

---

**追溯**：REQ-2/3/6/13；表见 `docs/06-db-design.md`（dcs_knowledge_items/gaps）；接口见 `docs/07-api-spec.md` §3.2。
