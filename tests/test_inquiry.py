"""Sprint-8 多轮引导纯逻辑测试（REQ-9）：意图识别/拆项（抽值预填）+ 摘要模板。

纯函数测试，不依赖 DB/TEI/pgvector。
状态机逐项确认 + 摘要转交的端到端见 scripts/demo.py + 手动多轮测试。
"""
from backend.app.service.conversation.inquiry import (
    _DEFAULT_DIMS,
    build_summary,
    detect_custom_inquiry,
)


def test_detect_stated_dims_prefilled():
    """客户陈述规格 → 抽值预填 collected，pending 只剩未陈述的。"""
    collected, pending = detect_custom_inquiry("我要定制灯带，蓝色，100米，要logo")
    assert collected["颜色"] == "蓝色"
    assert collected["数量"] == "100米"
    assert collected["Logo"] == "要logo"
    assert "交期" in pending  # 未陈述 → 待确认


def test_detect_all_stated_no_pending():
    """客户全部陈述 → pending 为空（start 时直接摘要转交，不重复问）。"""
    collected, pending = detect_custom_inquiry("定制灯带，蓝色，100米，要logo，7天交货")
    assert collected["颜色"] == "蓝色"
    assert collected["交期"] == "7天"
    assert pending == []


def test_detect_no_stated_falls_back_to_default():
    """仅定制触发词、无具体规格 → collected 空，pending = 默认核心维度。"""
    collected, pending = detect_custom_inquiry("我想定做一批灯带")
    assert collected == {}
    assert pending == _DEFAULT_DIMS


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
