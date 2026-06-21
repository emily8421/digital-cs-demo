"""留资入库（capture_lead）。REQ-4。"""
from sqlalchemy.orm import Session

from ...models import Lead
from .detector import find_phone, mask_phone


def capture_lead(
    db: Session, conversation_id: int, text: str | None, note: str | None = None
) -> Lead | None:
    """从文本抽取手机号；抽到则写一条脱敏留资记录并返回 lead，无则返回 None（不产生记录）。

    contact_value_enc（加密原文）本轮暂不实现，留 NULL（需密钥管理，见 06 备注）。
    仅 db.add + db.flush，由调用方统一 commit。
    """
    phone = find_phone(text)
    if phone is None:
        return None
    lead = Lead(
        conversation_id=conversation_id,
        contact_type="phone",
        contact_value_masked=mask_phone(phone),
        contact_value_enc=None,
        note=note,
    )
    db.add(lead)
    db.flush()  # 拿到 lead.id
    return lead
