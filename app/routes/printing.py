from fastapi import APIRouter, HTTPException, Query
from tortoise.expressions import Q
from typing import List, Optional

from app.models import Printing, Batches
from app.schemas import PrintingSchema, PrintingCreate, PrintingUpdate

router = APIRouter(
    prefix="/printing",
    tags=["printing"]
)


@router.get("/", response_model=List[PrintingSchema])
async def get_all_printings(
        batch_id: Optional[int] = Query(None, description="Filter by batch ID"),
        printing_min: Optional[float] = Query(None, description="Filter by min printing value"),
        printing_max: Optional[float] = Query(None, description="Filter by max printing value"),
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все записи печати с возможностью фильтрации:
    - по batch_id (ID партии)
    - по диапазону значений printing (printing_min и printing_max)
    С пагинацией (skip и limit)
    """
    query = Printing.all().offset(skip).limit(limit)

    if batch_id:
        query = query.filter(batch_id=batch_id)
    if printing_min is not None:
        query = query.filter(printing__gte=printing_min)
    if printing_max is not None:
        query = query.filter(printing__lte=printing_max)

    return await PrintingSchema.from_queryset(query)


@router.get("/{printing_id}", response_model=PrintingSchema)
async def get_printing(printing_id: int):
    printing = await Printing.get_or_none(printing_ID=printing_id).prefetch_related("batch", "flexa")
    if not printing:
        raise HTTPException(
            status_code=404,
            detail=f"Printing record with id {printing_id} not found"
        )
    return await PrintingSchema.from_tortoise_orm(printing)


@router.post("/", response_model=PrintingSchema)
async def create_printing(printing: PrintingCreate):
    # Проверяем существование связанной партии
    if not await Batches.exists(batch_id=printing.batch_id):
        raise HTTPException(
            status_code=400,
            detail=f"Batch with id {printing.batch_id} does not exist"
        )

    printing_obj = await Printing.create(
        **printing.model_dump(exclude={"batch_id"}),
        batch_id=printing.batch_id
    )
    return await PrintingSchema.from_tortoise_orm(printing_obj)


@router.put("/{printing_id}", response_model=PrintingSchema)
async def update_printing(
        printing_id: int,
        printing_data: PrintingUpdate
):
    printing = await Printing.get_or_none(printing_ID=printing_id)
    if not printing:
        raise HTTPException(
            status_code=404,
            detail=f"Printing record with id {printing_id} not found"
        )

    update_data = printing_data.model_dump(exclude_unset=True)

    # Проверяем обновление связанной партии
    if "batch_id" in update_data:
        if not await Batches.exists(batch_id=update_data["batch_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Batch with id {update_data['batch_id']} does not exist"
            )

    await printing.update_from_dict(update_data)
    await printing.save()

    return await PrintingSchema.from_tortoise_orm(printing)


@router.delete("/{printing_id}", response_model=dict)
async def delete_printing(printing_id: int):
    # Проверяем, используется ли запись в таблице Flexa
    printing = await Printing.get_or_none(printing_ID=printing_id).prefetch_related('flexa')

    if not printing:
        raise HTTPException(
            status_code=404,
            detail=f"Printing record with id {printing_id} not found"
        )

    if printing.flexa:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete printing that has related flexa records"
        )

    await printing.delete()
    return {"message": f"Printing record {printing_id} deleted successfully"}
