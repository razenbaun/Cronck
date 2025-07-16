from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.models import Flexa, Printing, Workers
from app.schemas import FlexaSchema, FlexaCreate, FlexaUpdate

router = APIRouter(
    prefix="/flexa",
    tags=["flexa"]
)


@router.get("/", response_model=List[FlexaSchema])
async def get_all_flexa(
        printing_id: Optional[int] = Query(None, description="Filter by printing ID"),
        worker_id: Optional[int] = Query(None, description="Filter by worker ID"),
        date_from: Optional[date] = Query(None, description="Filter by date from"),
        date_to: Optional[date] = Query(None, description="Filter by date to"),
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все записи флексопечати с возможностью фильтрации:
    - по printing_id (ID печати)
    - по worker_id (ID работника)
    - по диапазону дат (date_from и date_to)
    С пагинацией (skip и limit)
    """
    query = Flexa.all().offset(skip).limit(limit)

    if printing_id:
        query = query.filter(printing_id=printing_id)
    if worker_id:
        query = query.filter(worker_id=worker_id)
    if date_from:
        query = query.filter(date__gte=date_from)
    if date_to:
        query = query.filter(date__lte=date_to)

    return await FlexaSchema.from_queryset(query)


@router.get("/{flexa_id}", response_model=FlexaSchema)
async def get_flexa(flexa_id: int):
    flexa = await Flexa.get_or_none(flexa_ID=flexa_id).prefetch_related("printing", "worker")
    if not flexa:
        raise HTTPException(
            status_code=404,
            detail=f"Flexa record with id {flexa_id} not found"
        )
    return await FlexaSchema.from_tortoise_orm(flexa)


@router.post("/", response_model=FlexaSchema)
async def create_flexa(flexa: FlexaCreate):
    # Проверяем существование связанных записей
    if not await Printing.exists(printing_ID=flexa.printing_id):
        raise HTTPException(
            status_code=400,
            detail=f"Printing with id {flexa.printing_id} does not exist"
        )

    if not await Workers.exists(worker_ID=flexa.worker_id):
        raise HTTPException(
            status_code=400,
            detail=f"Worker with id {flexa.worker_id} does not exist"
        )

    flexa_dict = flexa.model_dump(exclude={"printing_id", "worker_id"})
    flexa_obj = await Flexa.create(
        **flexa_dict,
        printing_id=flexa.printing_id,
        worker_id=flexa.worker_id
    )
    return await FlexaSchema.from_tortoise_orm(flexa_obj)


@router.put("/{flexa_id}", response_model=FlexaSchema)
async def update_flexa(
        flexa_id: int,
        flexa_data: FlexaUpdate
):
    flexa = await Flexa.get_or_none(flexa_ID=flexa_id)
    if not flexa:
        raise HTTPException(
            status_code=404,
            detail=f"Flexa record with id {flexa_id} not found"
        )

    update_data = flexa_data.model_dump(exclude_unset=True)

    # Проверяем обновление связанных записей
    if "printing_id" in update_data:
        if not await Printing.exists(printing_ID=update_data["printing_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Printing with id {update_data['printing_id']} does not exist"
            )

    if "worker_id" in update_data:
        if not await Workers.exists(worker_ID=update_data["worker_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Worker with id {update_data['worker_id']} does not exist"
            )

    await flexa.update_from_dict(update_data)
    await flexa.save()

    return await FlexaSchema.from_tortoise_orm(flexa)


@router.delete("/{flexa_id}", response_model=dict)
async def delete_flexa(flexa_id: int):
    deleted_count = await Flexa.filter(flexa_ID=flexa_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail=f"Flexa record with id {flexa_id} not found"
        )
    return {"message": f"Flexa record {flexa_id} deleted successfully"}
