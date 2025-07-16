from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.models import Extrusion, Winding, Workers
from app.schemas import ExtrusionSchema, ExtrusionCreate, ExtrusionUpdate

router = APIRouter(
    prefix="/extrusion",
    tags=["extrusion"]
)


@router.get("/", response_model=List[ExtrusionSchema])
async def get_all_extrusions(
        winding_id: Optional[int] = Query(None, description="Filter by winding ID"),
        worker_id: Optional[int] = Query(None, description="Filter by worker ID"),
        start_date: Optional[date] = Query(None, description="Filter by start date"),
        end_date: Optional[date] = Query(None, description="Filter by end date"),
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все записи экструзии с возможностью фильтрации:
    - по winding_id (ID намотки)
    - по worker_id (ID работника)
    - по диапазону дат (start_date и end_date)
    С пагинацией (skip и limit)
    """
    query = Extrusion.all().offset(skip).limit(limit)

    if winding_id:
        query = query.filter(winding_id=winding_id)
    if worker_id:
        query = query.filter(worker_id=worker_id)
    if start_date:
        query = query.filter(date__gte=start_date)
    if end_date:
        query = query.filter(date__lte=end_date)

    return await ExtrusionSchema.from_queryset(query)


@router.get("/{extrusion_id}", response_model=ExtrusionSchema)
async def get_extrusion(extrusion_id: int):
    extrusion = await Extrusion.get_or_none(extrusion_ID=extrusion_id).prefetch_related("winding", "worker")
    if not extrusion:
        raise HTTPException(
            status_code=404,
            detail=f"Extrusion record with id {extrusion_id} not found"
        )
    return await ExtrusionSchema.from_tortoise_orm(extrusion)


@router.post("/", response_model=ExtrusionSchema)
async def create_extrusion(extrusion: ExtrusionCreate):
    # Проверяем существование связанных записей
    if not await Winding.exists(winding_ID=extrusion.winding_id):
        raise HTTPException(
            status_code=400,
            detail=f"Winding with id {extrusion.winding_id} does not exist"
        )

    if not await Workers.exists(worker_ID=extrusion.worker_id):
        raise HTTPException(
            status_code=400,
            detail=f"Worker with id {extrusion.worker_id} does not exist"
        )

    extrusion_dict = extrusion.model_dump(exclude={"winding_id", "worker_id"})
    extrusion_obj = await Extrusion.create(
        **extrusion_dict,
        winding_id=extrusion.winding_id,
        worker_id=extrusion.worker_id
    )
    return await ExtrusionSchema.from_tortoise_orm(extrusion_obj)


@router.put("/{extrusion_id}", response_model=ExtrusionSchema)
async def update_extrusion(
        extrusion_id: int,
        extrusion_data: ExtrusionUpdate
):
    extrusion = await Extrusion.get_or_none(extrusion_ID=extrusion_id)
    if not extrusion:
        raise HTTPException(
            status_code=404,
            detail=f"Extrusion record with id {extrusion_id} not found"
        )

    update_data = extrusion_data.model_dump(exclude_unset=True)

    # Проверяем обновление связанных записей
    if "winding_id" in update_data:
        if not await Winding.exists(winding_ID=update_data["winding_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Winding with id {update_data['winding_id']} does not exist"
            )

    if "worker_id" in update_data:
        if not await Workers.exists(worker_ID=update_data["worker_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Worker with id {update_data['worker_id']} does not exist"
            )

    await extrusion.update_from_dict(update_data)
    await extrusion.save()

    return await ExtrusionSchema.from_tortoise_orm(extrusion)


@router.delete("/{extrusion_id}", response_model=dict)
async def delete_extrusion(extrusion_id: int):
    # Проверяем, используется ли запись в других таблицах
    extrusion = await Extrusion.get_or_none(extrusion_ID=extrusion_id).prefetch_related('paketki')

    if not extrusion:
        raise HTTPException(
            status_code=404,
            detail=f"Extrusion record with id {extrusion_id} not found"
        )

    if extrusion.paketki:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete extrusion that has related paketki records"
        )

    await extrusion.delete()
    return {"message": f"Extrusion record {extrusion_id} deleted successfully"}
