from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.models import Paketki, Extrusion, Cutting, Workers
from app.schemas import PaketkiSchema, PaketkiCreate, PaketkiUpdate

router = APIRouter(
    prefix="/paketki",
    tags=["paketki"]
)


@router.get("/", response_model=List[PaketkiSchema])
async def get_all_paketki(
        extrusion_id: Optional[int] = Query(None, description="Filter by extrusion ID"),
        cutting_id: Optional[int] = Query(None, description="Filter by cutting ID"),
        worker_id: Optional[int] = Query(None, description="Filter by worker ID"),
        date_from: Optional[date] = Query(None, description="Filter by date from"),
        date_to: Optional[date] = Query(None, description="Filter by date to"),
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все записи с возможностью фильтрации:
    - по extrusion_id (ID экструзии)
    - по cutting_id (ID резки)
    - по worker_id (ID работника)
    - по диапазону дат (date_from и date_to)
    С пагинацией (skip и limit)
    """
    query = Paketki.all().offset(skip).limit(limit)

    if extrusion_id:
        query = query.filter(extrusion_id=extrusion_id)
    if cutting_id:
        query = query.filter(cutting_id=cutting_id)
    if worker_id:
        query = query.filter(worker_id=worker_id)
    if date_from:
        query = query.filter(date__gte=date_from)
    if date_to:
        query = query.filter(date__lte=date_to)

    return await PaketkiSchema.from_queryset(query)


@router.get("/{paketki_id}", response_model=PaketkiSchema)
async def get_paketki(paketki_id: int):
    paketki = await Paketki.get_or_none(paketki_ID=paketki_id).prefetch_related("extrusion", "cutting", "worker")
    if not paketki:
        raise HTTPException(
            status_code=404,
            detail=f"Paketki record with id {paketki_id} not found"
        )
    return await PaketkiSchema.from_tortoise_orm(paketki)


@router.post("/", response_model=PaketkiSchema)
async def create_paketki(paketki: PaketkiCreate):
    # Проверяем существование связанных записей
    if not await Extrusion.exists(extrusion_ID=paketki.extrusion_id):
        raise HTTPException(
            status_code=400,
            detail=f"Extrusion with id {paketki.extrusion_id} does not exist"
        )

    if not await Cutting.exists(cutting_ID=paketki.cutting_id):
        raise HTTPException(
            status_code=400,
            detail=f"Cutting with id {paketki.cutting_id} does not exist"
        )

    if not await Workers.exists(worker_ID=paketki.worker_id):
        raise HTTPException(
            status_code=400,
            detail=f"Worker with id {paketki.worker_id} does not exist"
        )

    paketki_dict = paketki.model_dump(exclude={"extrusion_id", "cutting_id", "worker_id"})
    paketki_obj = await Paketki.create(
        **paketki_dict,
        extrusion_id=paketki.extrusion_id,
        cutting_id=paketki.cutting_id,
        worker_id=paketki.worker_id
    )
    return await PaketkiSchema.from_tortoise_orm(paketki_obj)


@router.put("/{paketki_id}", response_model=PaketkiSchema)
async def update_paketki(
        paketki_id: int,
        paketki_data: PaketkiUpdate
):
    paketki = await Paketki.get_or_none(paketki_ID=paketki_id)
    if not paketki:
        raise HTTPException(
            status_code=404,
            detail=f"Paketki record with id {paketki_id} not found"
        )

    update_data = paketki_data.model_dump(exclude_unset=True)

    # Проверяем обновление связанных записей
    if "extrusion_id" in update_data:
        if not await Extrusion.exists(extrusion_ID=update_data["extrusion_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Extrusion with id {update_data['extrusion_id']} does not exist"
            )

    if "cutting_id" in update_data:
        if not await Cutting.exists(cutting_ID=update_data["cutting_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Cutting with id {update_data['cutting_id']} does not exist"
            )

    if "worker_id" in update_data:
        if not await Workers.exists(worker_ID=update_data["worker_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Worker with id {update_data['worker_id']} does not exist"
            )

    await paketki.update_from_dict(update_data)
    await paketki.save()

    return await PaketkiSchema.from_tortoise_orm(paketki)


@router.delete("/{paketki_id}", response_model=dict)
async def delete_paketki(paketki_id: int):
    deleted_count = await Paketki.filter(paketki_ID=paketki_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail=f"Paketki record with id {paketki_id} not found"
        )
    return {"message": f"Paketki record {paketki_id} deleted successfully"}
