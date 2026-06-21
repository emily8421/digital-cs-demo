# Digital Customer Service (Demo) — 后端

本机原型（Sprint-1）：消息接入 + 通道适配层 + 内置模拟器（REQ-1）。

## 1. 准备

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows（macOS/Linux 用 source .venv/bin/activate）
pip install -r requirements.txt
```

起 PostgreSQL（本机 Docker，在**仓库根目录**执行）：

```bash
docker compose -f docker/docker-compose.yml up -d
```

复制配置（默认值即可直接跑）：

```bash
cp .env.example .env
```

## 2. 运行

```bash
cd backend
uvicorn app.main:app --reload
```

浏览器打开 http://127.0.0.1:8000/docs 看 Swagger UI（可直接点按钮试接口）；或 http://127.0.0.1:8000/ui 看**演示辅助 UI**（聊天窗 + 控制台，P1 收官后补，更直观地演示全流程）。

## 3. 试一下（对应 REQ-1）

```bash
# 投递一条文本消息
curl -X POST http://127.0.0.1:8000/api/v1/messages/simulate \
  -H "Content-Type: application/json" \
  -d '{"external_group_id":"sim_group_001","sender_external_id":"cust_laozhou","content_type":"text","content_text":"5050和2835防水区别？能做IP67吗？"}'

# 读回消息流（{id} 换成上一步返回的 conversation_id）
curl http://127.0.0.1:8000/api/v1/conversations/{id}
```

## 4. 测试（不依赖 PG / Docker，用 SQLite 内存库）

```bash
# 在仓库根目录
pytest -q
```

## 目录结构（对应 ai/project-rules.md §5.1 分层）

```
app/
  channels/   通道适配层（模拟器在此；换企业微信/真实通道只改这里）
  service/    业务编排（一条消息进来 → 一处编排）
  api/        HTTP 接口（仅此层对外）
  models.py   ORM（对应 docs/06-db-design.md）
  db.py       引擎/会话/建表
  schemas.py  入参/出参 + 统一响应
  main.py     FastAPI 入口
```
