"""灌入员工花名册 + 路由规则种子（Sprint-3）。

对应 docs/design/routing-notification.md §2。幂等：按 name/scenario 存在则更新。
用法（仓库根目录）：.venv/Scripts/python scripts/seed_staff_routing.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.db import SessionLocal, init_db  # noqa: E402
from backend.app.models import RoutingRule, Staff  # noqa: E402

# 业务角色（虚构，见 ai/project-rules.md §0）
STAFF = [
    {"name": "小雯", "role": "sales", "external_id": None, "active": True},
    {"name": "阿杰", "role": "tech", "external_id": None, "active": True},
    {"name": "老黄", "role": "merchandiser", "external_id": None, "active": True},
    {"name": "陈总", "role": "owner", "external_id": None, "active": True},
]

# 场景→角色（design-routing-notification §2）
ROUTING = [
    {"scenario": "presale", "target_role": "sales", "priority": 0},
    {"scenario": "unknown_question", "target_role": "owner", "priority": 0},
    {"scenario": "order", "target_role": "merchandiser", "priority": 0},
    {"scenario": "aftersale", "target_role": "tech", "priority": 0},
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        s_new = s_upd = 0
        for s in STAFF:
            existing = db.query(Staff).filter_by(name=s["name"]).first()
            if existing:
                existing.role = s["role"]
                existing.active = s["active"]
                s_upd += 1
            else:
                db.add(Staff(**s))
                s_new += 1

        r_new = r_upd = 0
        for r in ROUTING:
            existing = db.query(RoutingRule).filter_by(scenario=r["scenario"]).first()
            if existing:
                existing.target_role = r["target_role"]
                existing.priority = r["priority"]
                r_upd += 1
            else:
                db.add(RoutingRule(**r))
                r_new += 1

        db.commit()
        print(f"staff: +{s_new} new, ~{s_upd} updated; routing: +{r_new} new, ~{r_upd} updated")
    finally:
        db.close()


if __name__ == "__main__":
    main()
