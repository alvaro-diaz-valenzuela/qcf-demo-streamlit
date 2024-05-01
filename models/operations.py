from bson import ObjectId
from typing import Annotated, Optional
from .data_types import Bank, Product, TypeLeg
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]

class Operation(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    deal_number: Optional[str] = Field(default=None)
    product: Product
    receive_pay: TypeLeg
    counterparty: Bank
    amount: int
    periodicity: int
    rate: float
    model_config = ConfigDict(
        populate_by_name=True,
    )

class OperationDaily(Operation):
    client: Bank
    client_confirmed_status: Optional[bool] = Field(default=False)
    confirmed_status: Optional[bool] = Field(default=False)
    operation_pair: Optional[PyObjectId] = Field(default=None)
    model_config = ConfigDict(
        populate_by_name=True,
    )

class UpdateOperation(BaseModel):
    deal_number: Optional[str] = None
    client: Optional[Bank] = None
    product: Optional[Product] = None
    receive_pay: Optional[TypeLeg] = None
    counterparty: Optional[Bank] = None
    amount: Optional[int] = None
    periodicity: Optional[int] = None
    rate: Optional[float] = None
    client_confirmed_status: Optional[bool] = None
    confirmed_status: Optional[bool] = None
    operation_pair: Optional[PyObjectId] = None
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
    )
