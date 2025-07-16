from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.models import Cutting, Batches, Equipment
from app.schemas import CuttingSchema, CuttingCreate, CuttingUpdate

router = APIRouter(
    prefix="/cutting",
    tags=["cutting"]
)


@router.get("/", response_model=List[CuttingSchema])
async def get_all_cuttings(
        batch_id: Optional[int] = Query(None, description="Filter by batch ID"),
        equipment_id: Optional[int] = Query(None, description="Filter by equipment ID"),
        status: Optional[str] = Query(None, description="Filter by status"),
        start_date: Optional[date] = Query(None, description="Filter by start date"),
        end_date: Optional[date] = Query(None, description="Filter by end date"),
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все записи резки с возможностью фильтрации:
    - по batch_id (ID партии)
    - по equipment_id (ID оборудования)
    - по status (статусу резки)
    - по диапазону дат (start_date и end_date)
    С пагинацией (skip и limit)
    """
    query = Cutting.all().offset(skip).limit(limit)

    if batch_id:
        query = query.filter(batch_id=batch_id)
    if equipment_id:
        query = query.filter(equipment_id=equipment_id)
    if status:
        query = query.filter(status__icontains=status)
    if start_date:
        query = query.filter(startDate__gte=start_date)
    if end_date:
        query = query.filter(startDate__lte=end_date)

    return await CuttingSchema.from_queryset(query)


@router.get("/{cutting_id}", response_model=CuttingSchema)
async def get_cutting(cutting_id: int):
    cutting = await Cutting.get_or_none(cutting_ID=cutting_id).prefetch_related("batch", "equipment")
    if not cutting:
        raise HTTPException(
            status_code=404,
            detail=f"Cutting record with id {cutting_id} not found"
        )
    return await CuttingSchema.from_tortoise_orm(cutting)


@router.post("/", response_model=CuttingSchema)
async def create_cutting(cutting: CuttingCreate):
    # Проверяем существование связанных записей
    if not await Batches.exists(batch_id=cutting.batch_id):
        raise HTTPException(
            status_code=400,
            detail=f"Batch with id {cutting.batch_id} does not exist"
        )

    if not await Equipment.exists(equipment_ID=cutting.equipment_id):
        raise HTTPException(
            status_code=400,
            detail=f"Equipment with id {cutting.equipment_id} does not exist"
        )

    cutting_dict = cutting.model_dump(exclude={"batch_id", "equipment_id"})
    cutting_obj = await Cutting.create(
        **cutting_dict,
        batch_id=cutting.batch_id,
        equipment_id=cutting.equipment_id
    )
    return await CuttingSchema.from_tortoise_orm(cutting_obj)


@router.put("/{cutting_id}", response_model=CuttingSchema)
async def update_cutting(
        cutting_id: int,
        cutting_data: CuttingUpdate
):
    cutting = await Cutting.get_or_none(cutting_ID=cutting_id)
    if not cutting:
        raise HTTPException(
            status_code=404,
            detail=f"Cutting record with id {cutting_id} not found"
        )

    update_data = cutting_data.model_dump(exclude_unset=True)

    # Проверяем обновление связанных записей
    if "batch_id" in update_data:
        if not await Batches.exists(batch_id=update_data["batch_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Batch with id {update_data['batch_id']} does not exist"
            )

    if "equipment_id" in update_data:
        if not await Equipment.exists(equipment_ID=update_data["equipment_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Equipment with id {update_data['equipment_id']} does not exist"
            )

    await cutting.update_from_dict(update_data)
    await cutting.save()

    return await CuttingSchema.from_tortoise_orm(cutting)


@router.delete("/{cutting_id}", response_model=dict)
async def delete_cutting(cutting_id: int):
    # Проверяем, используется ли запись в других таблицах
    cutting = await Cutting.get_or_none(cutting_ID=cutting_id).prefetch_related('paketki')

    if not cutting:
        raise HTTPException(
            status_code=404,
            detail=f"Cutting record with id {cutting_id} not found"
        )

    if cutting.paketki:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete cutting that has related paketki records"
        )

    await cutting.delete()
    return {"message": f"Cutting record {cutting_id} deleted successfully"}
