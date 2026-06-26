# 本机运行环境采集

> 由 `scripts/collect-env.ps1` 自动生成。自动采集项用于辅助技术方案选择；“人工确认项”仍需项目负责人补充。

## 自动采集

- 采集时间：2026-06-24 21:51:45 +08:00
- 计算机名：DESKTOP-9TC9SR2
- 当前用户：maixh
- 工作目录：D:\2-Project\0-Product\4-DigitalCustomerService\digital-cs-demo
- 操作系统：Microsoft Windows 11 家庭版 中文版 10.0.26200 64 位
- PowerShell：5.1.26100.8655
- CPU：12th Gen Intel(R) Core(TM) i7-12650H
- CPU 核心 / 线程：10 核 / 16 线程
- 内存总量：31.73 GB
- 系统架构：AMD64

### GPU

- Intel(R) UHD Graphics（显存/显存近似：2.00 GB）
- OrayIddDriver Device（显存/显存近似：未知）
- NVIDIA GeForce RTX 3050 6GB Laptop GPU（显存/显存近似：4.00 GB）

### 磁盘

- C: 可用 150.78 GB / 总计 464.95 GB
- D: 可用 99.79 GB / 总计 259.26 GB
- E: 可用 168.16 GB / 总计 195.31 GB

### 常用工具

- Git：git version 2.54.0.windows.1
- Python：Python 3.14.3
- Node.js：v22.17.1
- npm：11.11.0
- Java：已安装（未获取到版本）
- Docker：Docker version 29.5.2, build 79eb04c
- Docker 运行状态：可用

## 人工确认项

> 以下为 2026-06-25 Demo 实演实测确认值（依据见各项）；与本机自动采集（上）+ `ai/project-rules.md` §2.5 一致。

- Demo 阶段允许最大内存占用：**≤ 1 GB**（实测：PG ≈31M + TEI ≈161M + uvicorn ≈150M，合计 < 400M，预留余量）
- Demo 阶段允许最大显存占用：**0**（Demo 不用 GPU；TEI 用 `cpu-1.6` 镜像纯 CPU 推理）
- Demo 阶段允许最大磁盘占用：**≤ 3 GB**（镜像 ≈2.1G：pgvector 621M + pg 642M + TEI 914M；另含 PG 数据卷 + BGE 模型缓存）
- 是否允许联网调用外部 API：**Demo 不联网**（作答＝本地检索；LLM / 飞书 webhook / 真实通道属 MVP）
- 是否允许安装新依赖 / Docker 镜像：**允许（已装齐）**（Docker Desktop + `.venv` 就绪；新增依赖须先确认，见 `project-rules.md` §5.2）
- 是否允许使用公司服务器：**Demo 不需要**（本机先行；公司服务器属 MVP / 部署阶段，见 `docs/05-tech-spec.md` §1）
- 是否涉及公司数据 / 隐私数据：**不涉及**（全虚构演示数据；留资手机号入库已脱敏，见 `docs/design/conversation-engine.md`）
- 本机必须跑通的功能：后端（FastAPI / uvicorn）+ Docker（PG pgvector + TEI）+ 模拟器通道；8 类 REQ 闭环（2026-06-25 已验证，见 `docs/09-verification.md`）
- 可 Mock / 可远程运行的功能：TEI 不可用时编排跳过检索（`try/except + logging.warning`）；单元测试用 SQLite 内存库（不依赖 Docker）

## 服务器资源预案

> 当本机资源不足以实现完整功能时填写。若 Demo / MVP 全部可本机运行，可写“暂不需要”。

- **Demo 阶段：暂不需要**（全功能本机运行，见上「人工确认项」；本机资源充足，实测占用远低于上限）
- 触发条件：进入 MVP / 部署阶段（接真实通道、上公司服务器，见 `docs/05-tech-spec.md` §1）时再填
- CPU：MVP 阶段待确认
- 内存：MVP 阶段待确认
- GPU / 显存：MVP 阶段待确认（若 MVP 引入 GPU 推理）
- 磁盘：MVP 阶段待确认
- 网络 / 端口：MVP 阶段待确认
- 部署方式建议：MVP 阶段待确认
- 权限 / 成本 / 安全注意事项：MVP 阶段待确认
