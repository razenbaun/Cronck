from fastapi import APIRouter, HTTPException
from typing import List

from app.models import Equipment
from app.schemas import EquipmentSchema, EquipmentCreate, EquipmentUpdate

router = APIRouter(
    prefix="/equipment",
    tags=["equipment"]
)


@router.get("/", response_model=List[EquipmentSchema])
async def get_all_equipment(
        name: str = None,
        description: str = None
):
    query = Equipment.all()

    if name:
        query = query.filter(name__icontains=name)
    if description:
        query = query.filter(description__icontains=description)

    return await EquipmentSchema.from_queryset(query)


@router.get("/{equipment_id}", response_model=EquipmentSchema)
async def get_equipment(equipment_id: int):
    equipment = await Equipment.get_or_none(equipment_ID=equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment with id {equipment_id} not found"
        )
    return await EquipmentSchema.from_tortoise_orm(equipment)


@router.post("/", response_model=EquipmentSchema)
async def create_equipment(equipment: EquipmentCreate):
    # Проверяем уникальность имени
    if await Equipment.exists(name=equipment.name):
        raise HTTPException(
            status_code=400,
            detail="Equipment with this name already exists"
        )

    equipment_obj = await Equipment.create(**equipment.model_dump())
    return await EquipmentSchema.from_tortoise_orm(equipment_obj)


@router.put("/{equipment_id}", response_model=EquipmentSchema)
async def update_equipment(
        equipment_id: int,
        equipment_data: EquipmentUpdate
):
    equipment = await Equipment.get_or_none(equipment_ID=equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment with id {equipment_id} not found"
        )

    # Проверяем уникальность имени при обновлении
    if equipment_data.name and equipment_data.name != equipment.name:
        if await Equipment.exists(name=equipment_data.name):
            raise HTTPException(
                status_code=400,
                detail="Equipment with this name already exists"
            )

    update_data = equipment_data.model_dump(exclude_unset=True)
    await equipment.update_from_dict(update_data)
    await equipment.save()

    return await EquipmentSchema.from_tortoise_orm(equipment)


@router.delete("/{equipment_id}", response_model=dict)
async def delete_equipment(equipment_id: int):
    # Проверяем, используется ли оборудование в других таблицах
    used_in_winding = await Equipment.get_or_none(
        equipment_ID=equipment_id
    ).prefetch_related('winding')

    used_in_cutting = await Equipment.get_or_none(
        equipment_ID=equipment_id
    ).prefetch_related('cutting')

    if used_in_winding.winding or used_in_cutting.cutting:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete equipment that is in use"
        )

    deleted_count = await Equipment.filter(equipment_ID=equipment_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment with id {equipment_id} not found"
        )
    return {"message": f"Equipment {equipment_id} deleted successfully"}
