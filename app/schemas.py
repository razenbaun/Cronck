from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from pydantic import ConfigDict


class OrderBase(BaseModel):
    client: str
    orderStatus: str
    orderNumber: str
    productName: str
    sleeveName: str
    orderDate: date
    desiredCompletionDate: Optional[date] = None
    quantity: int
    orderWeight: float
    productType: str
    pack: int
    packaging: int
    comments: Optional[str] = None
    width: float
    length: float
    thickness: float
    widthSquared: float
    lengthSquared: float
    thicknessSquared: float
    density: float
    weightWithoutCutting: float
    weightWithCutting: float

    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    client: Optional[str] = None
    orderStatus: Optional[str] = None
    orderNumber: Optional[str] = None
    productName: Optional[str] = None
    sleeveName: Optional[str] = None
    orderDate: Optional[date] = None
    desiredCompletionDate: Optional[date] = None
    quantity: Optional[int] = None
    orderWeight: Optional[float] = None
    productType: Optional[str] = None
    pack: Optional[int] = None
    packaging: Optional[int] = None
    comments: Optional[str] = None
    width: Optional[float] = None
    length: Optional[float] = None
    thickness: Optional[float] = None
    widthSquared: Optional[float] = None
    lengthSquared: Optional[float] = None
    thicknessSquared: Optional[float] = None
    density: Optional[float] = None
    weightWithoutCutting: Optional[float] = None
    weightWithCutting: Optional[float] = None


class BatchBase(BaseModel):
    batchNumber: str
    batchStatus: str
    labelName: Optional[str] = None
    completionDate: Optional[date] = None
    shipment: bool = False
    print: Optional[str] = None
    accepted: Optional[float] = None
    acceptedPCS: Optional[int] = None
    deviation: Optional[float] = None


class BatchCreate(BatchBase):
    order_id: int


class BatchUpdate(BaseModel):
    batchNumber: Optional[str] = None
    batchStatus: Optional[str] = None
    labelName: Optional[str] = None
    completionDate: Optional[date] = None
    shipment: Optional[bool] = None
    print: Optional[str] = None
    accepted: Optional[float] = None
    acceptedPCS: Optional[int] = None
    deviation: Optional[float] = None


class BatchSchema(BatchBase):
    batch_id: int
    order_id: int
    model_config = ConfigDict(from_attributes=True)


class OrderSchema(OrderBase):
    order_id: int
    # batches: Optional[List[BatchSchema]] = None
    model_config = ConfigDict(from_attributes=True)


OrderSchema.model_rebuild()
BatchSchema.model_rebuild()


class EquipmentBase(BaseModel):
    name: str
    description: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class EquipmentSchema(EquipmentBase):
    equipment_ID: int
    model_config = ConfigDict(from_attributes=True)


class WorkerBase(BaseModel):
    FIO: str


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    FIO: Optional[str] = None


class WorkerSchema(WorkerBase):
    worker_ID: int
    model_config = ConfigDict(from_attributes=True)


class WindingBase(BaseModel):
    priority: int
    status: str
    cuttingDate: Optional[date] = None
    norm: float
    days: float
    winding: float
    requiredToWind: float
    remainToWind: float
    weightCheck: Optional[float] = None


class WindingCreate(WindingBase):
    batch_id: int
    equipment_id: int


class WindingUpdate(BaseModel):
    priority: Optional[int] = None
    status: Optional[str] = None
    cuttingDate: Optional[date] = None
    norm: Optional[float] = None
    days: Optional[float] = None
    winding: Optional[float] = None
    requiredToWind: Optional[float] = None
    remainToWind: Optional[float] = None
    weightCheck: Optional[float] = None
    batch_id: Optional[int] = None
    equipment_id: Optional[int] = None


class WindingSchema(WindingBase):
    winding_ID: int
    batch_id: int
    equipment_id: int
    model_config = ConfigDict(from_attributes=True)


class ExtrusionBase(BaseModel):
    date: date
    equipmentOperatinTime: float
    shiftNorm: float
    totalShift: float
    whiteDefective: float
    transparentDefective: float
    coloredDefective: float
    hourlyProduction: float
    seasonal: float


class ExtrusionCreate(ExtrusionBase):
    winding_id: int
    worker_id: int


class ExtrusionUpdate(BaseModel):
    date: Optional[date] = None
    equipmentOperatinTime: Optional[float] = None
    shiftNorm: Optional[float] = None
    totalShift: Optional[float] = None
    whiteDefective: Optional[float] = None
    transparentDefective: Optional[float] = None
    coloredDefective: Optional[float] = None
    hourlyProduction: Optional[float] = None
    seasonal: Optional[float] = None
    winding_id: Optional[int] = None
    worker_id: Optional[int] = None


class ExtrusionSchema(ExtrusionBase):
    extrusion_ID: int
    winding_id: int
    worker_id: int
    model_config = ConfigDict(from_attributes=True)


class CuttingBase(BaseModel):
    priority: int
    status: str
    cutting: float
    cuttingPSC: int
    remainToCut: float
    remainToCutPSC: int
    days: float
    norm: float
    startDate: Optional[date] = None
    PSCCheck: Optional[int] = None


class CuttingCreate(CuttingBase):
    batch_id: int
    equipment_id: int


class CuttingUpdate(BaseModel):
    priority: Optional[int] = None
    status: Optional[str] = None
    cutting: Optional[float] = None
    cuttingPSC: Optional[int] = None
    remainToCut: Optional[float] = None
    remainToCutPSC: Optional[int] = None
    days: Optional[float] = None
    norm: Optional[float] = None
    startDate: Optional[date] = None
    PSCCheck: Optional[int] = None
    batch_id: Optional[int] = None
    equipment_id: Optional[int] = None


class CuttingSchema(CuttingBase):
    cutting_ID: int
    batch_id: int
    equipment_id: int
    model_config = ConfigDict(from_attributes=True)


class PaketkiBase(BaseModel):
    date: date
    operatinTime: float
    shiftNorm: float
    totalShift: float
    whiteDefective: float
    transparentDefective: float
    coloredDefective: float
    hourlyProduction: float
    seasonal: float


class PaketkiCreate(PaketkiBase):
    extrusion_id: int
    cutting_id: int
    worker_id: int


class PaketkiUpdate(BaseModel):
    date: Optional[date] = None
    operatinTime: Optional[float] = None
    shiftNorm: Optional[float] = None
    totalShift: Optional[float] = None
    whiteDefective: Optional[float] = None
    transparentDefective: Optional[float] = None
    coloredDefective: Optional[float] = None
    hourlyProduction: Optional[float] = None
    seasonal: Optional[float] = None
    extrusion_id: Optional[int] = None
    cutting_id: Optional[int] = None
    worker_id: Optional[int] = None


class PaketkiSchema(PaketkiBase):
    paketki_ID: int
    extrusion_id: int
    cutting_id: int
    worker_id: int
    model_config = ConfigDict(from_attributes=True)


class PrintingBase(BaseModel):
    printing: float
    remainToPrint: float


class PrintingCreate(PrintingBase):
    batch_id: int


class PrintingUpdate(BaseModel):
    printing: Optional[float] = None
    remainToPrint: Optional[float] = None
    batch_id: Optional[int] = None


class PrintingSchema(PrintingBase):
    printing_ID: int
    batch_id: int
    model_config = ConfigDict(from_attributes=True)


class FlexaBase(BaseModel):
    date: date
    operatinTime: float
    shiftNorm: float
    totalShift: float
    whiteDefective: float
    printDefective: float
    coloredDefective: float
    hourlyProduction: float
    remark: Optional[str] = None


class FlexaCreate(FlexaBase):
    printing_id: int
    worker_id: int


class FlexaUpdate(BaseModel):
    date: Optional[date] = None
    operatinTime: Optional[float] = None
    shiftNorm: Optional[float] = None
    totalShift: Optional[float] = None
    whiteDefective: Optional[float] = None
    printDefective: Optional[float] = None
    coloredDefective: Optional[float] = None
    hourlyProduction: Optional[float] = None
    remark: Optional[str] = None
    printing_id: Optional[int] = None
    worker_id: Optional[int] = None


class FlexaSchema(FlexaBase):
    flexa_ID: int
    printing_id: int
    worker_id: int
    model_config = ConfigDict(from_attributes=True)


class FinishedProductsBase(BaseModel):
    date: date
    quantity: int
    weight: float


class FinishedProductsCreate(FinishedProductsBase):
    batch_id: int
    worker_id: int


class FinishedProductsUpdate(BaseModel):
    date: Optional[date] = None
    quantity: Optional[int] = None
    weight: Optional[float] = None
    batch_id: Optional[int] = None
    worker_id: Optional[int] = None


class FinishedProductsSchema(FinishedProductsBase):
    finishedProducts_ID: int
    batch_id: int
    worker_id: int
    model_config = ConfigDict(from_attributes=True)
