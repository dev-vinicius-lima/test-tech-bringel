# app/schemas.py
from datetime import date
from datetime import datetime
from typing import List
from pydantic import BaseModel
from enum import Enum

class UserType(str, Enum):
    technician = "technician"
    nursing = "nursing"
    admin = "admin"

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    user_type: UserType

class User(BaseModel):
    id: int
    name: str
    email: str
    user_type: UserType

class MaterialCreate(BaseModel):
    name: str
    material_type: str
    expiration_date: date
  
class Material(BaseModel):
    id: int
    name: str
    material_type: str
    expiration_date: date
    serial: str


class Step(BaseModel):
    name: str
    description: str
    timestamp: datetime

class Failure(BaseModel):
    error_message: str
    timestamp: datetime

class SerialTraceability(BaseModel):
    serial_number: str
    steps: List[Step]
    failures: List[Failure]
    process_count: int

    class Config:
        from_attributes = True