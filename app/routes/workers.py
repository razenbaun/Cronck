from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models import Workers
from app.schemas import WorkerSchema, WorkerCreate, WorkerUpdate

router = APIRouter(
    prefix="/workers",
    tags=["workers"]
)


@router.get("/", response_model=List[WorkerSchema])
async def get_all_workers(
        fio: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
):
    query = Workers.all().offset(skip).limit(limit)

    if fio:
        query = query.filter(FIO__icontains=fio)

    return await WorkerSchema.from_queryset(query)


@router.get("/{worker_id}", response_model=WorkerSchema)
async def get_worker(worker_id: int):
    worker = await Workers.get_or_none(worker_ID=worker_id)
    if not worker:
        raise HTTPException(
            status_code=404,
            detail=f"Worker with id {worker_id} not found"
        )
    return await WorkerSchema.from_tortoise_orm(worker)


@router.post("/", response_model=WorkerSchema)
async def create_worker(worker: WorkerCreate):
    # Проверяем уникальность ФИО
    if await Workers.exists(FIO=worker.FIO):
        raise HTTPException(
            status_code=400,
            detail="Worker with this FIO already exists"
        )

    worker_obj = await Workers.create(**worker.model_dump())
    return await WorkerSchema.from_tortoise_orm(worker_obj)


@router.put("/{worker_id}", response_model=WorkerSchema)
async def update_worker(
        worker_id: int,
        worker_data: WorkerUpdate
):
    worker = await Workers.get_or_none(worker_ID=worker_id)
    if not worker:
        raise HTTPException(
            status_code=404,
            detail=f"Worker with id {worker_id} not found"
        )

    # Проверяем уникальность ФИО при обновлении
    if worker_data.FIO and worker_data.FIO != worker.FIO:
        if await Workers.exists(FIO=worker_data.FIO):
            raise HTTPException(
                status_code=400,
                detail="Worker with this FIO already exists"
            )

    update_data = worker_data.model_dump(exclude_unset=True)
    await worker.update_from_dict(update_data)
    await worker.save()

    return await WorkerSchema.from_tortoise_orm(worker)


@router.delete("/{worker_id}", response_model=dict)
async def delete_worker(worker_id: int):
    # Проверяем, используется ли работник в других таблицах
    worker = await Workers.get_or_none(worker_ID=worker_id).prefetch_related(
        'extrusion', 'paketki', 'flexa', 'finished_products'
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail=f"Worker with id {worker_id} not found"
        )

    if (worker.extrusion or worker.paketki or
            worker.flexa or worker.finished_products):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete worker that has related records"
        )

    await worker.delete()
    return {"message": f"Worker {worker_id} deleted successfully"}
