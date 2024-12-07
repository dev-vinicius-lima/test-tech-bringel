# app/models.py
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.schemas import UserType
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    user_type = Column(Enum(UserType))

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    material_type = Column(String)
    expiration_date = Column(Date)
    serial = Column(String, unique=True)
    current_step_id = Column(Integer, ForeignKey('steps.id'))
    current_step = relationship("Step", back_populates="materials")
    completed = Column(Boolean, default=False)  

class Serial(Base):
    __tablename__ = 'serials'
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True)
    step_id = Column(Integer, ForeignKey('steps.id'))
    step = relationship("Step", back_populates="serials")
    failures = relationship("Failure", back_populates="serial")

class Step(Base):
    __tablename__ = 'steps'
    id = Column(Integer, primary_key=True, index=True)
    process_name = Column(String, nullable=False)  
    description = Column(String, nullable=False)  
    timestamp = Column(DateTime(timezone=True), nullable=False)
    serials = relationship("Serial", back_populates="step")
    materials = relationship("Material", back_populates="current_step")


class Failure(Base):
    __tablename__ = 'failures'
    id = Column(Integer, primary_key=True, index=True)
    serial_id = Column(Integer, ForeignKey('serials.id'))
    error_message = Column(String)
    timestamp = Column(Date)
    serial = relationship("Serial", back_populates="failures")