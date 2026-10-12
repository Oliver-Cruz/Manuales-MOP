"""
Endpoints de Procedimientos.

    POST /api/procedimientos                 → guarda + dispara la IA (flujo principal)
    PUT  /api/procedimientos/{id}            → actualiza correcciones + vuelve a disparar la IA
    POST /api/procedimientos/{id}/auditar    → re-audita sin cambiar el contenido
    GET  /api/procedimientos[?area_id=]      → listado (para el selector del frontend)
    GET  /api/procedimientos/{id}            → captura + feedback para pintar la pantalla

Los endpoints que llaman a la IA son `def` (no `async def`) a propósito:
FastAPI los ejecuta en un threadpool, así la llamada bloqueante al SDK no
congela el servidor para otros usuarios.

Si la IA falla, el procedimiento SÍ queda guardado y la respuesta trae
`estado_auditoria="error"` + `error_auditoria`, para que el usuario no
pierda lo capturado.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Area, Procedimiento
from ..schemas import ProcedimientoIn, ProcedimientoOut, ProcedimientoResumen
from ..services.audit_flow import run_audit, to_out

router = APIRouter(prefix="/api/procedimientos", tags=["Procedimientos"])


def _get_proc(db: Session, proc_id: int) -> Procedimiento:
    proc = db.get(Procedimiento, proc_id)
    if not proc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Procedimiento no encontrado.")
    return proc


def _ensure_area(db: Session, area_id: int) -> None:
    if not db.get(Area, area_id):
        raise HTTPException(422, "El área seleccionada no existe.")


@router.get("", response_model=list[ProcedimientoResumen])
def list_procedimientos(area_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Procedimiento).order_by(Procedimiento.actualizado_en.desc())
    if area_id is not None:
        stmt = stmt.where(Procedimiento.area_id == area_id)
    return db.scalars(stmt).all()


@router.get("/{proc_id}", response_model=ProcedimientoOut)
def get_procedimiento(proc_id: int, db: Session = Depends(get_db)):
    return to_out(_get_proc(db, proc_id))


@router.post("", response_model=ProcedimientoOut, status_code=status.HTTP_201_CREATED)
def create_procedimiento(
    payload: ProcedimientoIn,
    auditar: bool = Query(True, description="Disparar la auditoría con IA al guardar."),
    db: Session = Depends(get_db),
):
    """ENDPOINT PRINCIPAL: guarda el procedimiento y dispara el flujo de IA."""
    _ensure_area(db, payload.area_id)
    proc = Procedimiento(**payload.model_dump())
    db.add(proc)
    db.commit()
    db.refresh(proc)

    if auditar:
        proc = run_audit(db, proc)
    return to_out(proc)


@router.put("/{proc_id}", response_model=ProcedimientoOut)
def update_procedimiento(
    proc_id: int,
    payload: ProcedimientoIn,
    auditar: bool = Query(True, description="Volver a auditar con IA tras guardar las correcciones."),
    db: Session = Depends(get_db),
):
    """Guarda las correcciones del usuario y vuelve a pedir feedback a la IA."""
    proc = _get_proc(db, proc_id)
    _ensure_area(db, payload.area_id)
    for field, value in payload.model_dump().items():
        setattr(proc, field, value)
    db.commit()
    db.refresh(proc)

    if auditar:
        proc = run_audit(db, proc)
    return to_out(proc)


@router.post("/{proc_id}/auditar", response_model=ProcedimientoOut)
def auditar_procedimiento(proc_id: int, db: Session = Depends(get_db)):
    """Re-ejecuta la auditoría de IA sobre el contenido ya guardado."""
    return to_out(run_audit(db, _get_proc(db, proc_id)))
