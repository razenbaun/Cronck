from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date

from app.models import FinishedProducts, Batches, Workers
from app.schemas import FinishedProductsSchema, FinishedProductsCreate, FinishedProductsUpdate

router = APIRouter(
    prefix="/finished-products",
    tags=["finished_products"]
)


@router.get("/", response_model=List[FinishedProductsSchema])
async def get_all_finished_products(
        batch_id: Optional[int] = Query(None, description="Filter by batch ID"),
        worker_id: Optional[int] = Query(None, description="Filter by worker ID"),
        date_from: Optional[date] = Query(None, description="Filter by date from"),
        date_to: Optional[date] = Query(None, description="Filter by date to"),
        min_quantity: Optional[int] = Query(None, description="Filter by minimum quantity"),
        max_quantity: Optional[int] = Query(None, description="Filter by maximum quantity"),
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все записи готовой продукции с возможностью фильтрации:
    - по batch_id (ID партии)
    - по worker_id (ID работника)
    - по диапазону дат (date_from и date_to)
    - по количеству (min_quantity и max_quantity)
    С пагинацией (skip и limit)
    """
    query = FinishedProducts.all().offset(skip).limit(limit)

    if batch_id:
        query = query.filter(batch_id=batch_id)
    if worker_id:
        query = query.filter(worker_id=worker_id)
    if date_from:
        query = query.filter(date__gte=date_from)
    if date_to:
        query = query.filter(date__lte=date_to)
    if min_quantity is not None:
        query = query.filter(quantity__gte=min_quantity)
    if max_quantity is not None:
        query = query.filter(quantity__lte=max_quantity)

    return await FinishedProductsSchema.from_queryset(query)


@router.get("/{fproduct_id}", response_model=FinishedProductsSchema)
async def get_finished_product(fproduct_id: int):
    fproduct = await FinishedProducts.get_or_none(finishedProducts_ID=fproduct_id) \
        .prefetch_related("batch", "worker")
    if not fproduct:
        raise HTTPException(
            status_code=404,
            detail=f"Finished product with id {fproduct_id} not found"
        )
    return await FinishedProductsSchema.from_tortoise_orm(fproduct)


@router.post("/", response_model=FinishedProductsSchema)
async def create_finished_product(fproduct: FinishedProductsCreate):
    # Проверяем существование связанных записей
    if not await Batches.exists(batch_id=fproduct.batch_id):
        raise HTTPException(
            status_code=400,
            detail=f"Batch with id {fproduct.batch_id} does not exist"
        )

    if not await Workers.exists(worker_ID=fproduct.worker_id):
        raise HTTPException(
            status_code=400,
            detail=f"Worker with id {fproduct.worker_id} does not exist"
        )

    fproduct_dict = fproduct.model_dump(exclude={"batch_id", "worker_id"})
    fproduct_obj = await FinishedProducts.create(
        **fproduct_dict,
        batch_id=fproduct.batch_id,
        worker_id=fproduct.worker_id
    )
    return await FinishedProductsSchema.from_tortoise_orm(fproduct_obj)


@router.put("/{fproduct_id}", response_model=FinishedProductsSchema)
async def update_finished_product(
        fproduct_id: int,
        fproduct_data: FinishedProductsUpdate
):
    fproduct = await FinishedProducts.get_or_none(finishedProducts_ID=fproduct_id)
    if not fproduct:
        raise HTTPException(
            status_code=404,
            detail=f"Finished product with id {fproduct_id} not found"
        )

    update_data = fproduct_data.model_dump(exclude_unset=True)

    # Проверяем обновление связанных записей
    if "batch_id" in update_data:
        if not await Batches.exists(batch_id=update_data["batch_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Batch with id {update_data['batch_id']} does not exist"
            )

    if "worker_id" in update_data:
        if not await Workers.exists(worker_ID=update_data["worker_id"]):
            raise HTTPException(
                status_code=400,
                detail=f"Worker with id {update_data['worker_id']} does not exist"
            )

    await fproduct.update_from_dict(update_data)
    await fproduct.save()

    return await FinishedProductsSchema.from_tortoise_orm(fproduct)


@router.delete("/{fproduct_id}", response_model=dict)
async def delete_finished_product(fproduct_id: int):
    deleted_count = await FinishedProducts.filter(finishedProducts_ID=fproduct_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail=f"Finished product with id {fproduct_id} not found"
        )
    return {"message": f"Finished product {fproduct_id} deleted successfully"}
