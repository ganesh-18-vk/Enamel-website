from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

class AppointmentCreate(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=100)
    patient_phone: str = Field(..., min_length=10, max_length=15)
    patient_email: Optional[str] = None
    treatment_id: int
    doctor_id: int
    appointment_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    appointment_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    patient_notes: Optional[str] = None
    consent_acknowledged: bool = Field(..., description="Must acknowledge consent to clinic policies")

class AppointmentStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(Pending|Confirmed|Cancelled|Completed|Rescheduled)$")
    admin_notes: Optional[str] = None

class AppointmentReschedule(BaseModel):
    new_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    new_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    doctor_id: Optional[int] = None
    reason: Optional[str] = None

class EnquiryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[str] = None
    treatment_interest: Optional[str] = None
    message: str = Field(..., min_length=5, max_length=1000)

class AdminLogin(BaseModel):
    username: str
    password: str

class DoctorUpdate(BaseModel):
    name: str
    title: str
    qualifications: str
    experience_years: int
    specialization: str
    bio: str
    photo_url: Optional[str] = None
    is_active: bool = True

class ScheduleUpdate(BaseModel):
    day_of_week: int
    is_open: bool
    morning_start: str
    morning_end: str
    evening_start: str
    evening_end: str
    slot_duration_minutes: int = 30

class BlockedDateCreate(BaseModel):
    blocked_date: str
    doctor_id: Optional[int] = None
    reason: Optional[str] = None
