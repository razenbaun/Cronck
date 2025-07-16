from tortoise.models import Model
from tortoise import fields


class Orders(Model):
    order_id = fields.IntField(pk=True)
    client = fields.CharField(max_length=255)
    orderStatus = fields.CharField(max_length=100)
    orderNumber = fields.CharField(max_length=100, unique=True)
    productName = fields.CharField(max_length=255)
    sleeveName = fields.CharField(max_length=255)
    orderDate = fields.DateField()
    desiredCompletionDate = fields.DateField(null=True)
    quantity = fields.IntField()
    orderWeight = fields.FloatField()
    productType = fields.CharField(max_length=100)
    pack = fields.IntField()
    packaging = fields.IntField()
    comments = fields.TextField(null=True)
    width = fields.FloatField()
    length = fields.FloatField()
    thickness = fields.FloatField()
    widthSquared = fields.FloatField()
    lengthSquared = fields.FloatField()
    thicknessSquared = fields.FloatField()
    density = fields.FloatField()
    weightWithoutCutting = fields.FloatField()
    weightWithCutting = fields.FloatField()

    batches: fields.ReverseRelation["Batches"]

    class Meta:
        table = "orders"


class Batches(Model):
    batch_id = fields.IntField(pk=True)
    order: fields.ForeignKeyRelation[Orders] = fields.ForeignKeyField(
        "models.Orders", related_name="batches"
    )
    batchNumber = fields.CharField(max_length=100)
    batchStatus = fields.CharField(max_length=100)
    labelName = fields.CharField(max_length=255, null=True)
    completionDate = fields.DateField(null=True)
    shipment = fields.BooleanField(default=False)
    print = fields.CharField(max_length=255, null=True)
    accepted = fields.FloatField(null=True)
    acceptedPCS = fields.IntField(null=True)
    deviation = fields.FloatField(null=True)

    winding: fields.ReverseRelation["Winding"]
    cutting: fields.ReverseRelation["Cutting"]
    printing: fields.ReverseRelation["Printing"]
    finished_products: fields.ReverseRelation["FinishedProducts"]

    class Meta:
        table = "batches"


class Equipment(Model):
    equipment_ID = fields.IntField(pk=True)
    description = fields.TextField(null=True)
    name = fields.CharField(max_length=255)

    winding: fields.ReverseRelation["Winding"]
    cutting: fields.ReverseRelation["Cutting"]

    class Meta:
        table = "equipment"


class Workers(Model):
    worker_ID = fields.IntField(pk=True)
    FIO = fields.CharField(max_length=255)

    extrusion: fields.ReverseRelation["Extrusion"]
    paketki: fields.ReverseRelation["Paketki"]
    flexa: fields.ReverseRelation["Flexa"]
    finished_products: fields.ReverseRelation["FinishedProducts"]

    class Meta:
        table = "workers"


class Winding(Model):
    winding_ID = fields.IntField(pk=True)
    batch: fields.ForeignKeyRelation[Batches] = fields.ForeignKeyField(
        "models.Batches", related_name="winding"
    )
    equipment: fields.ForeignKeyRelation[Equipment] = fields.ForeignKeyField(
        "models.Equipment", related_name="winding"
    )
    priority = fields.IntField()
    status = fields.CharField(max_length=100)
    cuttingDate = fields.DateField(null=True)
    norm = fields.FloatField()
    days = fields.FloatField()
    winding = fields.FloatField()
    requiredToWind = fields.FloatField()
    remainToWind = fields.FloatField()
    weightCheck = fields.FloatField(null=True)

    extrusion: fields.ReverseRelation["Extrusion"]

    class Meta:
        table = "winding"


class Extrusion(Model):
    extrusion_ID = fields.IntField(pk=True)
    winding: fields.ForeignKeyRelation[Winding] = fields.ForeignKeyField(
        "models.Winding", related_name="extrusion"
    )
    date = fields.DateField()
    equipmentOperatinTime = fields.FloatField()
    shiftNorm = fields.FloatField()
    totalShift = fields.FloatField()
    whiteDefective = fields.FloatField()
    transparentDefective = fields.FloatField()
    coloredDefective = fields.FloatField()
    hourlyProduction = fields.FloatField()
    seasonal = fields.FloatField()
    worker: fields.ForeignKeyRelation[Workers] = fields.ForeignKeyField(
        "models.Workers", related_name="extrusion"
    )

    paketki: fields.ReverseRelation["Paketki"]

    class Meta:
        table = "extrusion"


class Cutting(Model):
    cutting_ID = fields.IntField(pk=True)
    batch: fields.ForeignKeyRelation[Batches] = fields.ForeignKeyField(
        "models.Batches", related_name="cutting"
    )
    equipment: fields.ForeignKeyRelation[Equipment] = fields.ForeignKeyField(
        "models.Equipment", related_name="cutting"
    )
    priority = fields.IntField()
    status = fields.CharField(max_length=100)
    cutting = fields.FloatField()
    cuttingPSC = fields.IntField()
    remainToCut = fields.FloatField()
    remainToCutPSC = fields.IntField()
    days = fields.FloatField()
    norm = fields.FloatField()
    startDate = fields.DateField(null=True)
    PSCCheck = fields.IntField(null=True)

    paketki: fields.ReverseRelation["Paketki"]

    class Meta:
        table = "cutting"


class Paketki(Model):
    paketki_ID = fields.IntField(pk=True)
    extrusion: fields.ForeignKeyRelation[Extrusion] = fields.ForeignKeyField(
        "models.Extrusion", related_name="paketki"
    )
    cutting: fields.ForeignKeyRelation[Cutting] = fields.ForeignKeyField(
        "models.Cutting", related_name="paketki"
    )
    date = fields.DateField()
    operatinTime = fields.FloatField()
    shiftNorm = fields.FloatField()
    totalShift = fields.FloatField()
    whiteDefective = fields.FloatField()
    transparentDefective = fields.FloatField()
    coloredDefective = fields.FloatField()
    hourlyProduction = fields.FloatField()
    seasonal = fields.FloatField()
    worker: fields.ForeignKeyRelation[Workers] = fields.ForeignKeyField(
        "models.Workers", related_name="paketki"
    )

    class Meta:
        table = "paketki"


class Printing(Model):
    printing_ID = fields.IntField(pk=True)
    batch: fields.ForeignKeyRelation[Batches] = fields.ForeignKeyField(
        "models.Batches", related_name="printing"
    )
    printing = fields.FloatField()
    remainToPrint = fields.FloatField()

    flexa: fields.ReverseRelation["Flexa"]

    class Meta:
        table = "printing"


class Flexa(Model):
    flexa_ID = fields.IntField(pk=True)
    printing: fields.ForeignKeyRelation[Printing] = fields.ForeignKeyField(
        "models.Printing", related_name="flexa"
    )
    date = fields.DateField()
    operatinTime = fields.FloatField()
    shiftNorm = fields.FloatField()
    totalShift = fields.FloatField()
    whiteDefective = fields.FloatField()
    printDefective = fields.FloatField()
    coloredDefective = fields.FloatField()
    hourlyProduction = fields.FloatField()
    remark = fields.TextField(null=True)
    worker: fields.ForeignKeyRelation[Workers] = fields.ForeignKeyField(
        "models.Workers", related_name="flexa"
    )

    class Meta:
        table = "flexa"


class FinishedProducts(Model):
    finishedProducts_ID = fields.IntField(pk=True)
    batch: fields.ForeignKeyRelation[Batches] = fields.ForeignKeyField(
        "models.Batches", related_name="finished_products"
    )
    date = fields.DateField()
    quantity = fields.IntField()
    weight = fields.FloatField()
    worker: fields.ForeignKeyRelation[Workers] = fields.ForeignKeyField(
        "models.Workers", related_name="finished_products"
    )

    class Meta:
        table = "finished_products"
