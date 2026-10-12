"""Endpoints de Áreas (Finanzas, Operaciones, RRHH, ...)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Area
from ..schemas import AreaIn, AreaOut

router = APIRouter(prefix="/api/areas", tags=["Áreas"])


@router.get("", response_model=list[AreaOut])
def list_areas(db: Session = Depends(get_db)):
    return db.scalars(select(Area).order_by(Area.nombre)).all()


@router.post("", response_model=AreaOut, status_code=status.HTTP_201_CREATED)
def create_area(payload: AreaIn, db: Session = Depends(get_db)):
    if db.scalar(select(Area).where(Area.nombre == payload.nombre)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un área con ese nombre.")
    area = Area(**payload.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area
