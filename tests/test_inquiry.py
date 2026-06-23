"""Sprint-8 多轮引导纯逻辑测试（REQ-9）：意图识别/拆项 + 摘要模板。

纯函数测试，不依赖 DB/TEI/pgvector。
状态机逐项确认 + 摘要转交的端到端见 scripts/demo.py + 手动多轮测试
（2026-06-23 验证：5 轮流转 → 摘要转交 handoff，见 08 Sprint-8 验收记录）。
"""
from backend.app.service.conversation.inquiry import (
    _DEFAULT_DIMS,
    build_summary,
    detect_custom_inquiry,
)


def test_detect_triggered_with_stated_dims():
    """含定制触发词 + 陈述规格 → 抽到对应维度。"""
    items = detect_custom_inquiry("我要定制灯带，蓝色，100米，要Logo")
    assert items is not None
    assert "颜色" in items and "数量" in items and "Logo" in items


def test_detect_triggered_falls_back_to_default_dims():
    """仅定制触发词、无具体规格 → 默认核心维度。"""
    items = detect_custom_inquiry("我想定做一批灯带")
    assert items == _DEFAULT_DIMS  # ["颜色","数量","Logo","交期"]


def test_detect_not_triggered_for_normal_questions():
    """普通问题（无定制触发词）→ None，不误判（走检索）。"""
    assert detect_custom_inquiry("5050和2835区别") is None
    assert detect_custom_inquiry("能做IP67吗") is None
    assert detect_custom_inquiry("订货电话13912345678") is None


def test_detect_empty_input():
    assert detect_custom_inquiry("") is None
    assert detect_custom_inquiry(None) is None


def test_build_summary_with_collected():
    assert build_summary({"颜色": "蓝", "数量": "100米"}) == "颜色=蓝 / 数量=100米"


def test_build_summary_empty():
    assert build_summary({}) == "（未收集到具体规格）"
