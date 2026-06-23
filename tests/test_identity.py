"""Sprint-9 身份披露纯逻辑测试（REQ-11）：意图识别 + 话术。

纯函数测试，不依赖 DB/TEI/pgvector。
"""
from backend.app.service.conversation.identity import (
    build_identity_reply,
    detect_identity_question,
)


def test_detect_identity_explicit_questions():
    """明确问身份 → 触发。"""
    assert detect_identity_question("你是机器人吗")
    assert detect_identity_question("你是不是AI")
    assert detect_identity_question("你是真人吗")
    assert detect_identity_question("你是人工智能吗")
    assert detect_identity_question("你是程序吗")


def test_detect_identity_not_triggered_for_normal():
    """普通问题/陈述 → 不触发（不误判，走多轮/检索）。"""
    assert not detect_identity_question("5050和2835区别")
    assert not detect_identity_question("能做IP67吗")
    assert not detect_identity_question("订货电话13912345678")
    assert not detect_identity_question("我要定制灯带")


def test_detect_identity_empty():
    assert not detect_identity_question("")
    assert not detect_identity_question(None)


def test_disclosure_reply_acknowledges_identity():
    """既定话术承认身份 + 角色 + 回归服务。"""
    r = build_identity_reply()
    assert "小辰" in r  # 角色
    assert "AI" in r  # 承认身份
    assert "帮您" in r  # 回归服务
