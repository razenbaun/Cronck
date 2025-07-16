from fastapi import APIRouter, HTTPException
from app.models import Orders, Batches
from app.schemas import OrderSchema, OrderCreate, OrderUpdate, BatchSchema

router = APIRouter(prefix="/orders", tags=["Orders"])


# Получить все заказы
@router.get("/", response_model=list[OrderSchema])
async def get_orders():
    return await Orders.all()


# Получить заказ по ID
@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int):
    order = await Orders.get_or_none(order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Создать новый заказ
@router.post("/", response_model=OrderSchema)
async def create_order(order_data: OrderCreate):
    order = await Orders.create(**order_data.model_dump())
    return order


# Обновить заказ по ID
@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(order_id: int, order_data: OrderUpdate):
    order = await Orders.get_or_none(order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await order.update_from_dict(order_data.model_dump(exclude_unset=True))
    await order.save()
    return order


# Удалить заказ по ID
@router.delete("/{order_id}")
async def delete_order(order_id: int):
    order = await Orders.get_or_none(order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await order.delete()
    return {"message": "Order deleted successfully"}


# Получить все партии для заказа
@router.get("/{order_id}/batches", response_model=list[BatchSchema])
async def get_batches_by_order(order_id: int):
    order = await Orders.get_or_none(order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    batches = await order.batches.all()
    return batches
