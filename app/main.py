# app/main.py
from datetime import date
from ssl import SSLSession
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from datetime import datetime
from sqlalchemy import DateTime

from app import  models, schemas
from app.initializers import initialize_steps
from .database import SessionLocal, engine, get_db
from . import database


# Criar as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Pydantic model
class Item(BaseModel):
    id: int
    name: str
    description: str

# Dependency
def get_db():
    db = SessionLocal()
    initialize_steps(db)
    try:
        yield db
    finally:
        db.close()   

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: SSLSession = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: SSLSession = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.post("/materials", response_model=schemas.Material)
def create_material(material: schemas.MaterialCreate, db: SSLSession = Depends(get_db)):
    serial = f"{material.material_type.lower().strip()[0]}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    db_material = models.Material(
        name = material.name,
        material_type = material.material_type,
        expiration_date = material.expiration_date,
        serial = serial,
        current_step_id = 1
    )

    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


@app.put("/materials/{material_id}/next_step")
def advance_material_step(material_id: int, db: SSLSession = Depends(database.get_db)):
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    if material.completed:
        material.current_step_id = None 
        material.completed = False
        db.commit()
        return {"message": "Material reiniciado para o início do processo."}
    
    next_step = db.query(models.Step).filter(models.Step.id == material.current_step_id + 1).first()
    
    if not next_step:
        material.completed = True
        db.commit()
        return {"message": "Material completou todas as etapas."}
    
    # Avance para a próxima etapa
    material.current_step_id = next_step.id
    db.commit()
    return {"message": "Material avançou para a próxima etapa.", "current_step": next_step.name}



@app.get("/traceability/{serial_number}", response_model=schemas.SerialTraceability)
def get_traceability(serial_number: str, db: SSLSession = Depends(get_db)):
    serial = db.query(models.Serial).filter(models.Serial.serial_number == serial_number).first()
    if not serial:
        raise HTTPException(status_code=404, detail="Serial not found")
    
    return {
        "serial_number": serial.serial_number,
        "steps": [{"description": step.description, "process_name": step.process_name, "timestamp": step.timestamp} for step in serial.steps],
        "failures": [{"error_message": failure.error_message, "timestamp": failure.timestamp} for failure in serial.failures],
        "process_count": len(serial.steps)
    }

@app.get("/traceability/", response_model=List[schemas.SerialTraceability])
def get_all_traceability(db: SSLSession = Depends(get_db)):
    serials = db.query(models.Serial).all()
    return [{
        "serial_number": serial.serial_number,
        "steps": [{"process_name": step.process_name, "timestamp": step.timestamp} for step in serial.steps],
        "failures": [{"error_message": failure.error_message, "timestamp": failure.timestamp} for failure in serial.failures],
        "process_count": len(serial.steps)
    } for serial in serials]