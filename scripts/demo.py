"""Sprint-7 Demo 脚本：模拟器通道走通 P1 全流程（03 §3 Demo 步骤 1-5）。

固化模拟器演示路径（企业微信客户群群内自动回复 Sprint-0 已核实不成立，真实通道待替代方案）。

前置（本机，按顺序）：
    docker compose -f docker/docker-compose.yml up -d   # pgvector + TEI
    .venv/Scripts/python scripts/seed_knowledge.py      # 知识种子
    .venv/Scripts/python scripts/seed_staff_routing.py  # staff/routing 种子
    .venv/Scripts/python -m uvicorn app.main:app --app-dir backend

用法：.venv/Scripts/python scripts/demo.py
"""
import httpx

BASE = "http://127.0.0.1:8000/api/v1"


def simulate(group, text=None, ctype="text"):
    body = {
        "external_group_id": group,
        "sender_external_id": "cust_laozhou",
        "content_type": ctype,
    }
    if text is not None:
        body["content_text"] = text
    return httpx.post(f"{BASE}/messages/simulate", json=body, timeout=60).json()["data"]


def main() -> None:
    print("=== 步骤1：产品参数问题 → 知识作答（REQ-2/3）===")
    d = simulate("demo", "5050和2835灯带有什么区别，能做IP67吗")
    print(f"  hit={d['hit']} | 作答: {d['reply_text']}")

    print("\n=== 步骤2：未覆盖问题 → 请留资 + 缺口转交（REQ-6）===")
    d = simulate("demo", "你们的灯带能用在海里潜水吗")
    print(f"  hit={d['hit']} | 回复: {d['reply_text']}")
    print(f"  gap_id={d['gap_id']} handoff_id={d['handoff_id']}（缺口转拍板人）")

    print("\n=== 步骤3：含手机号 → 留资记录（REQ-4/5）===")
    d = simulate("demo", "满意，想订500米，电话13912345678，报个价")
    print(f"  lead_id={d['lead_id']}（脱敏留资，如 139****5678）")

    print("\n=== 步骤4：定时小结 → 经营者（REQ-7）===")
    s = httpx.post(f"{BASE}/summaries/daily", timeout=30).json()["data"]
    print(f"  summary: {s['summary']}")

    print("\n=== 步骤5a：语音 → 如实告知 + 提醒（REQ-12）===")
    d = simulate("demo5", ctype="voice")
    print(f"  回复: {d['reply_text']} | notif={d['notification_id']}")

    print("\n=== 步骤5b：转人工暂停 → 不自动回（REQ-10）===")
    httpx.post(
        f"{BASE}/conversations/{d['conversation_id']}/handoff-state",
        json={"handoff_state": "handed_off"},
        timeout=10,
    )
    d2 = simulate("demo5", "还在吗")
    print(f"  handed_off 后回复: {d2['reply_text']}（应为 None = 已暂停）")

    print("\n=== Demo 完成（P1 全流程，模拟器通道）===")


if __name__ == "__main__":
    main()
