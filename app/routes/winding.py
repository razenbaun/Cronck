from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models import Winding, Batches, Equipment
from app.schemas import WindingSchema, WindingCreate, WindingUpdate

router = APIRouter(
    prefix="/winding",
    tags=["winding"]
)


@router.get("/", response_model=List[WindingSchema])
async def get_all_windings(
        batch_id: Optional[int] = Query(None, description="Filter by batch ID"),
        equipment_id: Optional[int] = Query(None, description="Filter by equipment ID"),
        status: Optional[str] = Query(None, description="Filter by status"),
        skip: int = 0,
        limit: int = 100
):
    query = Winding.all().offset(skip).limit(limit)

    if batch_id:
        query = query.filter(batch_id=batch_id)
    if equipment_id:
        query = query.filter(equipment_id=equipment_id)
    if status:
        query = query.filter(status__icontains=status)

    return await WindingSchema.from_queryset(query)


@router.get("/{winding_id}", response_model=WindingSchema)
async def get_winding(winding_id: int):
    winding = await Winding.get_or_none(winding_ID=winding_id).prefetch_related("batch", "equipment")
    if not winding:
        raise HTTPException(
            status_code=404,
            detail=f"Winding record with id {winding_id} not found"
        )
    return await WindingSchema.from_tortoise_orm(winding)


@router.post("/", response_model=WindingSchema)
async def create_winding(winding: WindingCreate):
    # Проверяем существование связанных записей
    if not await Batches.exists(batch_id=winding.batch_id):
        raise HTTPException(
            status_code=400,
            detail=f"Batch with id {winding.batch_id} does not exist"
        )

    if not await Equipment.exists(equipment_ID=winding.equipment_id):
        raise HTTPException(
            status_code=400,
            detail=f"Equipment with id {winding.equipment_id} does not exist"
        )

    winding_dict = winding.model_dump(exclude={"batch_id", "equipment_id"})
    winding_obj = await Winding.create(
        **winding_dict,
        batch_id=winding.batch_id,
        equipment_id=winding.equipment_id
    )
    return await WindingSchema.from_tortoise_orm(winding_obj)


@router.put("/{winding_id}", response_model=WindingSchema)
async def update_winding(
        winding_id: int,
        winding_data: WindingUpdate
):
    winding = await Winding.get_or_none(winding_ID=winding_id)
    if not winding:
        raise HTTPException(
            status_code=404,
            detail=f"Winding record with id {winding_id} not found"
        )

    update_data = winding_data.model_dump(exclude_unset=True)

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

    await winding.update_from_dict(update_data)
    await winding.save()

    return await WindingSchema.from_tortoise_orm(winding)


@router.delete("/{winding_id}", response_model=dict)
async def delete_winding(winding_id: int):
    # Проверяем, используется ли запись в других таблицах
    winding = await Winding.get_or_none(winding_ID=winding_id).prefetch_related('extrusion')

    if not winding:
        raise HTTPException(
            status_code=404,
            detail=f"Winding record with id {winding_id} not found"
        )

    if winding.extrusion:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete winding that has related extrusion records"
        )

    await winding.delete()
    return {"message": f"Winding record {winding_id} deleted successfully"}
