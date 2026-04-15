from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.check import CheckResult
from app.schemas.check import CheckComputation


def create_check_result(db: Session, result: CheckComputation) -> CheckResult:
    row = CheckResult(
        company_name=result.company_name,
        tax_id=result.tax_id,
        country=result.country,
        risk_score=result.risk_score,
        severity=result.severity,
        summary=result.summary,
        signals_payload=[signal.model_dump() for signal in result.signals],
    )
    db.add(row)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(row)
    return row


def get_check_result(db: Session, check_id: int) -> CheckResult | None:
    statement = select(CheckResult).where(CheckResult.id == check_id)
    return db.scalar(statement)


def list_check_results(db: Session, offset: int, limit: int) -> tuple[list[CheckResult], int]:
    items_statement = (
        select(CheckResult)
        .order_by(CheckResult.created_at.desc(), CheckResult.id.desc())
        .offset(offset)
        .limit(limit)
    )
    total_statement = select(func.count()).select_from(CheckResult)
    items = list(db.scalars(items_statement).all())
    total = int(db.scalar(total_statement) or 0)
    return items, total
