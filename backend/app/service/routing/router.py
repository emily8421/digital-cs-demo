"""角色路由：scenario → target_role → 在岗 staff。REQ-8。

对应 docs/design/routing-notification.md §2。规则可经 dcs_routing_rules 配置。
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from ...models import RoutingRule, Staff


@dataclass
class RouteTarget:
    """路由解析结果。"""

    role: str | None  # 命中的目标角色（无规则则 None）
    staff_id: int | None  # 解析到的在岗员工（role 有但无在岗员工则 None）
    staff_name: str | None


def resolve_target(db: Session, scenario: str) -> RouteTarget:
    """按 scenario 查路由规则得 target_role，再解析到一名在岗 staff（取 id 最小的）。"""
    rule = db.query(RoutingRule).filter_by(scenario=scenario).first()
    if rule is None:
        return RouteTarget(role=None, staff_id=None, staff_name=None)
    staff = (
        db.query(Staff)
        .filter(Staff.role == rule.target_role, Staff.active.is_(True))
        .order_by(Staff.id)
        .first()
    )
    return RouteTarget(
        role=rule.target_role,
        staff_id=staff.id if staff else None,
        staff_name=staff.name if staff else None,
    )
