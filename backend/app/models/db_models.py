from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="doctor")  # doctor, radiologist, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    external_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    studies = relationship("Study", back_populates="patient")


class Study(Base):
    __tablename__ = "studies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    modality = Column(String(50), default="CR")
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # png, jpg, dicom
    original_filename = Column(String(255), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="studies")
    prediction = relationship("Prediction", back_populates="study", uselist=False)
    report = relationship("Report", back_populates="study", uselist=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), unique=True, nullable=False)
    primary_label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), nullable=True)  # mild, moderate, severe
    uncertainty_level = Column(String(50), nullable=True)  # high, medium, needs_review
    differential_diagnosis = Column(Text, nullable=True)  # JSON string
    heatmap_path = Column(String(500), nullable=True)
    model_version = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    study = relationship("Study", back_populates="prediction")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(Integer, ForeignKey("studies.id"), unique=True, nullable=False)
    findings = Column(Text, nullable=False)
    impression = Column(Text, nullable=False)
    pdf_path = Column(String(500), nullable=True)
    generated_by = Column(String(50), default="template")  # template, llm
    created_at = Column(DateTime, default=datetime.utcnow)

    study = relationship("Study", back_populates="report")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
