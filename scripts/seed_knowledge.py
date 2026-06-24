"""灌入知识库种子数据（灯带/驱动 FAQ）。

对应 docs/design/knowledge-base.md §2「种子数据」。幂等：按 question_pattern
存在则更新答案与向量，不存在则新增。首次运行会加载 BGE 模型（下载约百兆，稍慢）。

用法（仓库根目录，需已装依赖、PG+pgvector 已起、backend/.env 配好）：
    .venv/Scripts/python scripts/seed_knowledge.py
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

# 让脚本能 import backend.app.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.db import SessionLocal, init_db  # noqa: E402
from backend.app.models import KnowledgeItem  # noqa: E402
from backend.app.service.knowledge.embedder import embed  # noqa: E402

# 愿景种子（灯带/驱动参数 + 采购标准 FAQ）。采购 FAQ 的数字为示例配置值，可改。
SEEDS = [
    {
        "question_pattern": "IP65和IP67防水等级有什么区别",
        "answer": (
            "IP65 是防喷水等级，可承受任意方向低压喷水，适合户檐、雨棚等淋雨但不浸泡的场景；"
            "IP67 可短时浸水（水深1米约30分钟），适合地埋、水池边等可能短时被淹的安装。"
            "户外长期裸露建议至少 IP65；如需 IP67 请在订单注明并加价。"
        ),
        "category": "防水参数",
    },
    {
        "question_pattern": "5050灯带和2835灯带有什么区别怎么选",
        "answer": (
            "5050 灯珠尺寸较大（5.0×5.0mm），单颗亮度高、色彩好，适合主照明或氛围强调；"
            "2835（2.8×3.5mm）更省电、光效高、性价比好，适合大面积常规照明。"
            "要高亮选 5050，要省电节能选 2835。"
        ),
        "category": "型号选型",
    },
    {
        "question_pattern": "户外灯带推荐什么型号",
        "answer": (
            "户外常规推荐 IP65 的 2835 或 5050 硅胶防水灯带；若安装位置可能积水或短时浸泡"
            "（地埋、水景），选 IP67 灌胶款。具体型号可按长度和色温再确认。"
        ),
        "category": "型号选型",
    },
    {
        "question_pattern": "起订量是多少",
        "answer": "常规库存型号 100 米起订；定制色温/防水等级 500 米起订。量大可议价。",
        "category": "采购FAQ",
    },
    {
        "question_pattern": "交期要多久",
        "answer": "常规型号现货 1-2 个工作日发货；定制款 5-7 个工作日；大批量以排产为准，下单时确认。",
        "category": "采购FAQ",
    },
    {
        "question_pattern": "付款方式有哪些",
        "answer": "支持对公转账（随附专票）、支付宝/微信对公。首单可预付定金，老客户支持月结（需资质审核）。",
        "category": "采购FAQ",
    },
    {
        "question_pattern": "灯带每米多少瓦能接多长",
        "answer": (
            "2835 常规约 8-12W/米，5050 约 12-15W/米。单条不建议超过 5 米串联（压降明显），"
            "超长需中途补电或分段供电。"
        ),
        "category": "参数",
    },
]


def main() -> None:
    init_db()  # 确保表 + vector 扩展就绪
    db = SessionLocal()
    try:
        created = updated = 0
        for s in SEEDS:
            vec = embed(s["question_pattern"])  # 检索键＝问题模式
            existing = (
                db.query(KnowledgeItem)
                .filter_by(question_pattern=s["question_pattern"])
                .first()
            )
            if existing:
                existing.answer = s["answer"]
                existing.category = s["category"]
                existing.embedding = vec
                existing.status = "confirmed"
                existing.updated_at = datetime.now(timezone.utc)
                updated += 1
            else:
                db.add(
                    KnowledgeItem(
                        embedding=vec,
                        status="confirmed",
                        source_staff_id=None,
                        **s,
                    )
                )
                created += 1
        db.commit()
        print(f"seeded done: +{created} new, ~{updated} updated (total seeds={len(SEEDS)})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
