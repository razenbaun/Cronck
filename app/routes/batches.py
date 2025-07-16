from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models import Batches, Orders
from app.schemas import BatchSchema, BatchCreate, BatchUpdate

router = APIRouter(
    prefix="/batches",
    tags=["batches"]
)


@router.get("/", response_model=List[BatchSchema])
async def get_all_batches(
        order_id: Optional[int] = None,
        batch_status: Optional[str] = None
):
    """
    Получить все партии с возможностью фильтрации:
    - по order_id (идентификатору заказа)
    - по batch_status (статусу партии)
    """
    query = Batches.all()

    if order_id:
        query = query.filter(order_id=order_id)
    if batch_status:
        query = query.filter(batchStatus__icontains=batch_status)

    return await BatchSchema.from_queryset(query)


@router.get("/{batch_id}", response_model=BatchSchema)
async def get_batch(batch_id: int):
    """
    Получить конкретную партию по ID
    """
    batch = await Batches.get_or_none(batch_id=batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail=f"Batch with id {batch_id} not found"
        )
    return await BatchSchema.from_tortoise_orm(batch)


@router.post("/", response_model=BatchSchema)
async def create_batch(batch: BatchCreate):
    """
    Создать новую партию
    """
    # Проверяем существует ли заказ
    if not await Orders.exists(order_id=batch.order_id):
        raise HTTPException(
            status_code=400,
            detail=f"Order with id {batch.order_id} does not exist"
        )

    batch_dict = batch.model_dump(exclude={"order_id"})
    batch_obj = await Batches.create(
        **batch_dict,
        order_id=batch.order_id
    )
    return await BatchSchema.from_tortoise_orm(batch_obj)


@router.put("/{batch_id}", response_model=BatchSchema)
async def update_batch(batch_id: int, batch_data: BatchUpdate):
    """
    Обновить информацию о партии
    """
    batch = await Batches.get_or_none(batch_id=batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail=f"Batch with id {batch_id} not found"
        )

    update_data = batch_data.model_dump(exclude_unset=True)
    await batch.update_from_dict(update_data)
    await batch.save()

    return await BatchSchema.from_tortoise_orm(batch)


@router.delete("/{batch_id}", response_model=dict)
async def delete_batch(batch_id: int):
    """
    Удалить партию по ID
    """
    deleted_count = await Batches.filter(batch_id=batch_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail=f"Batch with id {batch_id} not found"
        )
    return {"message": f"Batch {batch_id} deleted successfully"}


@router.get("/order/{order_id}", response_model=List[BatchSchema])
async def get_batches_by_order(order_id: int):
    """
    Получить все партии для конкретного заказа
    """
    if not await Orders.exists(order_id=order_id):
        raise HTTPException(
            status_code=404,
            detail=f"Order with id {order_id} not found"
        )

    batches = await Batches.filter(order_id=order_id)
    return await BatchSchema.from_queryset(batches)
