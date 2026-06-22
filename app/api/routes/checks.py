from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.check import CheckResult
from app.repositories.checks import create_check_result, get_check_result, list_check_results
from app.schemas.check import CheckCreate, CheckListResponse, CheckResponse, RiskSignal
from app.services.counterparty_service import run_counterparty_check

router = APIRouter()


def _serialize_check(row: CheckResult) -> CheckResponse:
    signals = [RiskSignal.model_validate(signal) for signal in row.signals_payload]

    return CheckResponse(
        id=row.id,
        company_name=row.company_name,
        tax_id=row.tax_id,
        country=row.country,
        risk_score=row.risk_score,
        severity=row.severity,
        summary=row.summary,
        signals=signals,
        created_at=row.created_at,
    )


@router.post("/checks", response_model=CheckResponse, status_code=status.HTTP_201_CREATED)
def create_check(payload: CheckCreate, db: Session = Depends(get_db)) -> CheckResponse:
    result = run_counterparty_check(payload)

    try:
        row = create_check_result(db=db, result=result)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist the risk check result.",
        ) from exc

    return _serialize_check(row)


@router.get("/checks/{check_id}", response_model=CheckResponse)
def get_check(check_id: int, db: Session = Depends(get_db)) -> CheckResponse:
    row = get_check_result(db=db, check_id=check_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")

    return _serialize_check(row)


@router.get("/checks", response_model=CheckListResponse)
def list_checks(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> CheckListResponse:
    items, total = list_check_results(db=db, offset=offset, limit=limit)
    return CheckListResponse(
        items=[_serialize_check(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
