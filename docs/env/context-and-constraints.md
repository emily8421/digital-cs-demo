# 背景与约束（Context & Constraints）

> **独立维护的项目背景与约束清单**。与 00-09 / design-\* 物理分离，方便随时修改。
> 作用：`docs/04-architecture.md`、`docs/05-tech-spec.md` 等的**选型依据**；改了本文件，就据此调整那两份的建议。
> 来源：2026-06-21 与项目方确认（AI 问答）。标注「待补充」处需项目方继续提供。

## 1. 团队与技能

- **主导者技能**：Python **会一些**（脚本级偏上）；后端 Web 框架、数据库、向量库、LLM 集成、部署等多为**初学者**。
- **含义（对架构的约束）**：
  - 选型须**主流、教程多、踩坑少**；避免冷门/高运维组件。
  - 倾向**少组件**（能复用一个就不拆两个），降低初学者的认知与运维负担。
  - 编码约定与目录结构要**简单清晰**（见 `ai/project-rules.md` §5）。
- **待补充**：团队规模（是否一人推进）、是否有前端/运维同事协作。

## 2. 已有资源（项目方确认）

| 维度 | 现状 | 来源 |
|---|---|---|
| AI 大模型（对话） | 经公司**中转站**调用：GLM-5.2、DeepSeek 等（OpenAI 兼容） | 确认 |
| AI 向量（embedding） | **是否经中转站可用，待测**（中转站通常只带对话、未必带向量） | 待测 |
| 企业微信 | 有，**计划认证**（当前未认证、未使用客户群） | 确认 |
| 内部协作 IM | **飞书** | 确认 |
| 部署环境 | **当前：本机跑原型**；后续：公司自有 Linux 服务器（可 Docker + 外网，**暂缓启用**） | 确认 |

## 3. 约束 → 对架构/技术方案的含义

- **AI 对话＝经中转站（已定）**：GLM-5.2 / DeepSeek，OpenAI 兼容，复用公司现有账号。
- **AI 向量 embedding（已定，Sprint-2）**：**本地 BGE via Docker TEI（text-embeddings-inference）**。
  - 选定 (B) 本地 BGE：原拟「进程内 sentence-transformers」，但 Python 3.14 + Windows 下 torch/onnxruntime 原生 DLL（`c10.dll`/pybind）加载失败（`WinError 1114`），改容器内 Linux 跑 TEI、宿主以 httpx 调用（`POST /embed`，512 维 bge-small-zh-v1.5）；向量库 pgvector。
  - (A) 中转站 `/v1/embeddings` 未采用（待测、未必支持）；海外 API 仍作备选，注意客户数据出境合规。
- **企业微信计划认证**：MVP（模拟器）不受影响；真实接客户（微信客服/会话存档）需认证完成（见 DEC-8）。
- **内部 IM＝飞书**：员工侧「转交提醒 / 日报」出站通道＝**飞书机器人**（custom robot webhook，接入简单），MVP 即可用。
- **部署＝本机原型优先**：当前在**本机**跑通原型（Docker Desktop + 本地 Python），**暂不启用公司服务器**——即当前无需折腾服务器访问/Docker-on-server。公司 Linux 服务器作为后续部署资源，原型稳定后再上。

## 4. 据此的技术取向（给 04 / 05 的输入）

| 项 | 取向 | 状态 |
|---|---|---|
| 部署 | **本机原型**（Docker Desktop / 本地 Python）；公司 Linux 服务器＝后续 | 当前本机 |
| 数据库 | PostgreSQL（本机先用 Docker 起；服务器后续） | 已定（栈级） |
| 向量检索 | pgvector（复用 PG） | 已定 |
| LLM 对话 | 经中转站：GLM-5.2 / DeepSeek（OpenAI 兼容） | 已定 |
| Embedding | 本地 BGE via Docker TEI（text-embeddings-inference） | **已定**（Sprint-2） |
| 员工通知出站 | 飞书机器人（custom robot） | 已定 |
| 真实客户通道 | 企业微信合规途径（微信客服/会话存档） | 前置：认证（已计划） |

## 5. 仍待项目方补充 / 确认

1. ~~LLM provider~~ → **已定**：对话经中转站（GLM-5.2 / DeepSeek）。
2. ~~embedding 走中转站还是本地 BGE~~ → **已定（Sprint-2）**：本地 BGE via Docker **TEI（text-embeddings-inference）**。原因：Python 3.14 + Windows 下进程内 torch/onnx 原生 DLL 加载失败（`WinError 1114`），改容器内 Linux 跑 TEI、宿主 httpx 调用；向量库 pgvector。
3. ~~企业微信是否认证~~ → **已定**：计划认证（DEC-8）。
4. ~~服务器~~ → **本机原型先**；公司服务器后续（暂缓）。
5. **海外 API 是哪家的 key**？（若启用备选）— 待补。
6. **团队规模 / 是否有前端或运维同事**？— 待补。
7. 各组件**版本号**（Python/PG/FastAPI 等）— 待补（Sprint-1 第一步钉）。

## 6. 维护说明

- 本文件独立于 00-09 / design-\*；改这里 → 据此调 `docs/04-architecture.md`、`docs/05-tech-spec.md`、`ai/project-rules.md` §2。
- 新增约束直接在 §2/§3 增行，不要散落到其他文档。
- 变更记录：2026-06-21 首次建立；同日更新——部署改**本机优先**（公司服务器后续）、对话经**中转站**(GLM-5.2/DeepSeek)、embedding 改**待测**（中转站未必带向量，兜底本地 BGE）、企业微信**计划认证**。
