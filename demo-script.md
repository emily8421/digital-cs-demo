# Demo 演示操作手册

> 数字客服 Demo 完整操作手册：环境准备 → 启动 → 扫码演示 → 故障排查 → 关闭。
> 覆盖 P1+P2 全部能力（REQ-1~14 + 话题级 10）。三个前端页面共用自建后端。

## 0. 系统组成

- **后端**：Python + FastAPI + PostgreSQL（pgvector 向量）+ TEI（embedding，Docker），模拟器通道
- **三个前端页面**（同后端，StaticFiles 挂 `/ui`）：
  - `/ui`（index.html）— PC 全功能控制台（演示者/深度）
  - `/ui/h5.html` — 客户视角 H5（扫码即聊）
  - `/ui/confirm.html` — 知识确认页面（拍板人）
- **项目根**：`D:\2-Project\0-Product\4-DigitalCustomerService\digital-cs-demo`

## 1. 环境准备（首次 / 换机）

### 1.1 依赖
- **Docker Desktop**（起 PG + TEI 容器）
- **Python 3.14 + 项目 `.venv`**（后端依赖；统一用 `.venv/Scripts/python.exe`）
- **`qrcode[pil]`**（仅 §3.3 一键生成二维码脚本用，**非后端运行依赖**）：`.venv/Scripts/python -m pip install 'qrcode[pil]'`

### 1.2 旧库迁移提醒
本项目原型用 `Base.metadata.create_all` 建表（不自动迁移）。若 PG 库是早期建的，P2 新增列/约束需手动 ALTER（各 Sprint 验收时已执行）：
- `dcs_notifications` CHECK 加 `sla`（Sprint-11）
- `dcs_knowledge_items` 加 `confirmed_by_staff_id`（打磨批次2）

全新库（drop 后 `create_all`）则自动含全部，无需 ALTER。

### 1.3 防火墙（扫码必需，管理员 PowerShell 一次性）
```
netsh advfirewall firewall add rule name="DCS-H5-8000" dir=in action=allow protocol=TCP localport=8000 profile=any
```
演示完删除：`netsh advfirewall firewall delete rule name="DCS-H5-8000"`

## 2. 启动

### 2.1 起依赖容器（PG + TEI）
```
docker compose -f docker/docker-compose.yml up -d
```
确认两个容器 Up：`docker ps`（dcs-db、dcs-embeddings）。TEI 首次拉模型可能慢（缓存后秒起）。

### 2.2 起后端（绑 0.0.0.0 让手机访问）
```
.venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

### 2.3 确认就绪
- `curl http://localhost:8000/health` → `{"status":"ok"}`
- TEI Ready：`docker logs dcs-embeddings --tail 3`（末行 `Ready`）

### 2.4 种子数据（首次 / 重置知识库）
```
.venv/Scripts/python.exe scripts/seed_knowledge.py      # 灯带/驱动 FAQ
.venv/Scripts/python.exe scripts/seed_staff_routing.py  # 员工/路由规则
```

## 3. 访问 + 扫码

### 3.1 查电脑局域网 IP
```
ipconfig | findstr IPv4
```
取 `192.168.x.x`（**忽略 `172.28.x.x`**——WSL 虚拟网卡，手机访问不了）。

### 3.2 扫码地址（手机电脑同 WiFi）
- **H5（客户）**：`http://<IP>:8000/ui/h5.html`
- **知识确认**：`http://<IP>:8000/ui/confirm.html`
- **PC 控制台**：`http://<IP>:8000/ui`

贴地址到在线二维码工具生成码，手机扫码即开。

### 3.3 一键生成二维码（推荐，免手动查 IP）

`scripts/gen_demo_qrcodes.py` 自动探测本机局域网 IP（UDP 路由探测，不联网），一次性把上面三个地址生成 PNG 到项目根：

```
.venv/Scripts/python scripts/gen_demo_qrcodes.py
```

输出 `demo-h5-qrcode.png` / `demo-ui-qrcode.png` / `demo-confirm-qrcode.png`，双击打开即可扫码。
**IP 变了（换 WiFi / 路由器重启）再跑一次即刷新全部码**，无需手动 `ipconfig`。依赖 `qrcode[pil]`（未装：`.venv/Scripts/python -m pip install 'qrcode[pil]'`）。

### 3.4 让二维码长期有效（可选）

本机 IP 由路由器 DHCP 动态分配，同一 WiFi 下通常稳定（租约续约），换网络才会变。想一劳永逸：路由器后台把电脑 MAC 绑定到固定 IP（DHCP「地址保留」），此后该 WiFi 下 IP 不变，三张码长期有效；换网络时再用 §3.3 脚本一键刷新。

## 4. 演示场景

### 4.1 客户视角（H5 `/ui/h5.html`）
扫码后输入框发消息（或点右上「▶ 演示」一键）。

| # | 演示项 | REQ | 发什么 | 客户看到 |
|---|---|---|---|---|
| 1 | 知识问答 | 2/3 | `5050和2835区别` / `能做IP67吗` | AI 作答（命中知识库） |
| 2 | 缺口转人 | 6 | `你们公司地址在哪`（未命中） | "…帮您请同事确认…方便留个联系方式吗？" + "已请同事为您跟进 🙋" |
| 3 | 留资识别 | 4 | `满意，想订货，电话13912345678` | "📝 您的联系方式已收到…"（后端 messages 表存脱敏 `139****5678`） |
| 4 | 多轮引导 | 9 | `我要定制灯带` | 逐项问【颜色→数量→Logo→交期】，答完摘要转核价 |
| 5 | 多轮（智能预填） | 9 | `我要定制灯带，蓝色，100米，要logo` | 预填 3 项，只追问【交期】→ 答 `7天` → 摘要转交 |
| 6 | 多轮（跳过） | 9 | 多轮中某项发 `跳过` | 该维度标「（跳过）」，摘要可见核价人知晓 |
| 7 | 身份披露 | 11 | `你是机器人吗` | "我是小辰，汇辰灯饰的 AI 客服助理 🤖 …" |
| 8 | 非文字 | 12 | 点 🎤 发语音 | "收到您的语音，我暂时看不了内容…" |

### 4.2 员工 / 经营者侧（`/ui` 控制台，PC）
- **转交通知**（REQ-5/8）：「转人工转交」选场景+原因 → 飞书卡片（角色+口语化提醒）
- **经营者小结**（REQ-7）：「生成经营者小结」→ "今天共 N 条…X 条需跟进…"
- **会话级暂停**（REQ-10）：「转人工暂停」填会话 ID 置 `handed_off` → 回 H5 发消息无回复；`auto` 恢复
- **P2 时效扫描**（REQ-14）：「P2 时效扫描」→ 超时未答列表 + 提示经营者
- **P2 知识确认入口**（REQ-13）：跳 `/ui/confirm.html`
- **P2 多轮/身份**（REQ-9/11）：左侧聊天发「我要定制灯带」/「你是机器人吗」

### 4.3 知识回写闭环（`/ui/confirm.html`，REQ-13）
演示"知识库自增长"——答不上的，拍板人补答确认后下次能答。
1. **造缺口**：H5 发 `能帮我写一首关于月亮的诗吗`（未命中）→ 客户侧"已请同事确认"
2. **补答**：confirm 页左侧填答案 →「补答 → 待确认」→ 进右侧
3. **确认**：右侧「确认 → 回写标准答案」→ confirmed + 缺口 resolved（补答人/确认人分别记录）
4. **验证**：回 H5 再发 `能帮我写一首关于月亮的诗吗` → AI 作答了

> 注：不用「今天天气怎么样」造缺口——早期 Sprint 演示已将其回写进 KB（「灯饰客服不查天气」消歧条目），再发会命中而走不通缺口路径；故改用此冷门问句（2026-06-25 实演验证 gap + handoff + 通知全生成）。

### 4.4 话题级暂停（REQ-10 话题级，API 触发）
`/ui` 暂无按钮，用 API 演示（同群多客户，某客户转人工只暂停他）：
```
curl -X POST http://localhost:8000/api/v1/conversations/<会话ID>/topic-handoff ^
  -H "Content-Type: application/json" ^
  -d "{\"topic_key\":\"cust_A\",\"handoff_state\":\"handed_off\"}"
```
然后 H5：cust_A 发消息无回复，cust_B 发消息正常作答。

### 4.5 一键重放
H5 右上「▶ 演示」→ 自动跑：问答→缺口转人→留资→语音（约 10 秒主闭环）。

## 5. 话术速查

| 场景 | 话术 | 来源 |
|---|---|---|
| 知识命中 | （知识条目标准答案原文） | 后端出站 |
| 缺口（未命中） | "这个问题我暂时还答不准，帮您请同事确认一下。方便留个联系方式吗？回复后会有专人跟进。" | 后端出站 |
| 非文字 | "收到您的{语音/图片/视频}，我暂时看不了内容，麻烦用文字说明一下，或者稍等我请同事看一下。" | 后端出站 |
| 身份披露 | "我是小辰，汇辰灯饰的 AI 客服助理 🤖 能帮您查产品参数、记需求转同事跟进。有什么可以帮您的？" | 后端出站 |
| 多轮首轮 | "好的，定制询盘帮您逐项确认。请问【颜色】是？" | 后端出站 |
| 多轮预填 | "收到您的需求：颜色=… / 数量=… / …。还需确认几项。请问【X】是？" | 后端出站 |
| 多轮完成 | "收到，已为您整理：颜色=… / …，转给同事核价，稍后回复您 🙂" | 后端出站 |
| 留资 | "📝 您的联系方式已收到，会有同事尽快联系您" | **H5 前端合成**（按 `lead_id`） |
| 缺口转人 | "这个问题我需要确认一下，已请同事为您跟进 🙋" | **H5 前端合成**（按 `handoff_id`） |
| 转人工暂停 | （无自动回复，客户侧显示"已为您转接人工客服，稍候由同事为您服务 🙂"） | **H5 前端合成**（按 `handoff_state`） |

## 6. 故障排查

| 现象 | 原因 | 解决 |
|---|---|---|
| 手机扫码打不开 | 防火墙未放行 8000 | 管理员加规则（§1.3） |
| 打不开（规则已加） | IP 变了（调过网络） | `ipconfig` 重查用新 `192.168.x.x`，或直接跑 §3.3 脚本一键刷新码 |
| `/health` 连不上 | uvicorn 没起 / 端口占用 | 重起 uvicorn（§2.2）；`netstat -ano\|findstr :8000` 查占用 |
| 检索全 `hit:false` | TEI 没起 / 没 Ready | `docker logs dcs-embeddings` 看 Ready；`docker compose ... up -d embeddings` |
| `uvicorn: command not found` | 没用 .venv | 用 `.venv/Scripts/python.exe -m uvicorn`（§2.2） |
| PG 报列不存在（confirm/sla） | 旧库 schema 没更新 | ALTER 加列/约束（§1.2）；或 drop 库重建 |
| 中文显示乱码 | Windows 控制台 GBK | 仅显示问题，存储 UTF-8 正确 |
| 检索召回偏宽（误命中） | 阈值 0.5 margin 薄 | 已知限制（Sprint-4）；改进需 category 预筛，留优化 |

## 7. 关闭 / 重启

### 关闭
- **后端**：找 8000 端口进程 kill：`netstat -ano | findstr :8000` → `taskkill /PID <pid> /F`
- **容器**：`docker compose -f docker/docker-compose.yml down`（数据 volume `dcs_pgdata` 保留，下次起数据还在）
- **彻底清数据**：`docker compose ... down -v`（删 volume，知识/消息全清，需重新种子）

### 重启（改代码后）
1. 停旧后端（上）
2. 容器已在则跳过（否则 §2.1）
3. 重起 uvicorn（§2.2，加载新代码）

## 8. 演示推荐路径
- **给客户/老板**：H5「▶ 演示」一键 + 几个典型问答（IP67/5050）+ 多轮定制 → 10 分钟讲清"AI 接消息、答得上的答、答不上转人"
- **给技术评审**：/ui 控制台全功能 + 话题级暂停（API）+ 知识回写闭环 + SLA scan
- **给拍板人（业务方）**：`/ui/confirm.html` 知识确认（补答→确认→自增长）

---

**追溯**：功能/Demo 步骤见 `docs/03-prd.md` §3；REQ 见 `docs/02-srs.md`；Sprint 验收见 `docs/08-dev-plan.md`；阶段见 `docs/09-verification.md`。
