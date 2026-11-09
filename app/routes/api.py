from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from typing import Optional, List, Dict, Any
from ..models import (
    AppointmentCreate, AppointmentStatusUpdate, AppointmentReschedule,
    EnquiryCreate, AdminLogin, DoctorUpdate, ScheduleUpdate, BlockedDateCreate
)
from ..database import (
    get_treatments, get_treatment_by_slug, get_treatment_by_id, update_treatment,
    get_doctors, get_doctor_by_id, update_doctor,
    get_available_slots, create_appointment, get_appointment_by_ref,
    update_appointment_status, reschedule_appointment,
    save_enquiry, get_enquiries, mark_enquiry_read,
    verify_admin_credentials, get_admin_overview, get_admin_appointments,
    get_clinic_schedule, update_schedule_day, get_blocked_dates,
    add_blocked_date, delete_blocked_date
)
from ..auth import create_admin_token, get_current_admin

router = APIRouter(prefix="/api", tags=["API"])

# ================= PUBLIC API ENDPOINTS =================

@router.get("/treatments")
def api_get_treatments():
    """Returns list of active treatments."""
    return {"treatments": get_treatments(active_only=True)}

@router.get("/treatments/{slug_or_id}")
def api_get_treatment(slug_or_id: str):
    """Returns details of a specific treatment by slug or integer ID."""
    if slug_or_id.isdigit():
        trt = get_treatment_by_id(int(slug_or_id))
    else:
        trt = get_treatment_by_slug(slug_or_id)
        
    if not trt:
        raise HTTPException(status_code=404, detail="Treatment not found.")
    return trt

@router.get("/doctors")
def api_get_doctors():
    """Returns list of active doctors."""
    return {"doctors": get_doctors(active_only=True)}

@router.get("/availability")
def api_get_availability(doctor_id: int, date: str):
    """
    Computes real-time available appointment slots for a specific doctor on a given date.
    Respects operating schedule, doctor availability, blocked dates, and existing bookings.
    """
    result = get_available_slots(doctor_id, date)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/appointments", status_code=status.HTTP_201_CREATED)
def api_create_appointment(payload: AppointmentCreate):
    """
    Creates an appointment atomically.
    Validates slot availability, prevents double bookings, and persists to database.
    """
    try:
        data = payload.model_dump()
        result = create_appointment(data)
        return {
            "success": True,
            "message": "Appointment confirmed successfully.",
            "appointment": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while booking your appointment. Please try again.")

@router.get("/appointments/ref/{booking_ref}")
def api_get_appointment_by_ref(booking_ref: str):
    """Retrieves appointment details for confirmation display."""
    app = get_appointment_by_ref(booking_ref)
    if not app:
        raise HTTPException(status_code=404, detail="Booking reference not found.")
    return app

@router.post("/enquiries", status_code=status.HTTP_201_CREATED)
def api_create_enquiry(payload: EnquiryCreate):
    """Submits patient inquiry from contact page."""
    try:
        enquiry_id = save_enquiry(payload.model_dump())
        return {
            "success": True,
            "message": "Thank you for reaching out. Our team will contact you shortly.",
            "enquiry_id": enquiry_id
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send your message. Please call our clinic directly.")

# ================= ADMIN AUTHENTICATION =================

@router.post("/admin/login")
def api_admin_login(payload: AdminLogin, response: Response):
    """Authenticates admin and sets HTTP-only session cookie."""
    user = verify_admin_credentials(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    token = create_admin_token(user["username"], user["role"])
    
    # Set secure cookie
    response.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    
    return {
        "success": True,
        "token": token,
        "user": user,
        "redirect_url": "/admin"
    }

@router.post("/admin/logout")
def api_admin_logout(response: Response):
    """Clears admin session cookie."""
    response.delete_cookie("admin_session")
    return {"success": True, "message": "Logged out successfully."}

# ================= ADMIN MANAGEMENT APIS (PROTECTED) =================

@router.get("/admin/overview")
def api_admin_overview(admin: Dict[str, Any] = Depends(get_current_admin)):
    """Returns real-time clinic overview statistics."""
    return get_admin_overview()

@router.get("/admin/appointments")
def api_admin_appointments(
    search: Optional[str] = None,
    date: Optional[str] = None,
    doctor_id: Optional[int] = None,
    treatment_id: Optional[int] = None,
    status: Optional[str] = None,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Lists appointments with filters."""
    appointments = get_admin_appointments(
        search=search,
        date_filter=date,
        doctor_id=doctor_id,
        treatment_id=treatment_id,
        status_filter=status
    )
    return {"appointments": appointments, "total": len(appointments)}

@router.patch("/admin/appointments/{appointment_id}/status")
def api_admin_update_status(
    appointment_id: int, 
    payload: AppointmentStatusUpdate, 
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Updates status of an appointment (Confirmed, Cancelled, Completed, Rescheduled)."""
    success = update_appointment_status(appointment_id, payload.status, payload.admin_notes)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return {"success": True, "message": f"Appointment status updated to {payload.status}."}

@router.post("/admin/appointments/{appointment_id}/reschedule")
def api_admin_reschedule(
    appointment_id: int, 
    payload: AppointmentReschedule, 
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Reschedules an appointment with conflict validation."""
    try:
        result = reschedule_appointment(
            appointment_id=appointment_id,
            new_date=payload.new_date,
            new_time=payload.new_time,
            doctor_id=payload.doctor_id,
            reason=payload.reason
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reschedule appointment.")

@router.put("/admin/doctors/{doctor_id}")
def api_admin_update_doctor(
    doctor_id: int, 
    payload: DoctorUpdate, 
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Updates doctor profile and status."""
    success = update_doctor(doctor_id, payload.model_dump())
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return {"success": True, "message": "Doctor updated successfully."}

@router.put("/admin/treatments/{treatment_id}")
def api_admin_update_treatment(
    treatment_id: int, 
    payload: Dict[str, Any], 
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Updates treatment parameters."""
    success = update_treatment(treatment_id, payload)
    if not success:
        raise HTTPException(status_code=404, detail="Treatment not found.")
    return {"success": True, "message": "Treatment updated successfully."}

@router.get("/admin/schedule")
def api_admin_get_schedule(admin: Dict[str, Any] = Depends(get_current_admin)):
    """Returns clinic schedule and blocked dates."""
    return {
        "schedule": get_clinic_schedule(),
        "blocked_dates": get_blocked_dates()
    }

@router.put("/admin/schedule/{day_of_week}")
def api_admin_update_schedule_day(
    day_of_week: int,
    payload: ScheduleUpdate,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Updates clinic operating hours for a specific day."""
    success = update_schedule_day(
        day_of_week=day_of_week,
        is_open=payload.is_open,
        morning_start=payload.morning_start,
        morning_end=payload.morning_end,
        evening_start=payload.evening_start,
        evening_end=payload.evening_end,
        slot_duration=payload.slot_duration_minutes
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update schedule.")
    return {"success": True, "message": "Schedule updated successfully."}

@router.post("/admin/blocked-dates", status_code=status.HTTP_201_CREATED)
def api_admin_add_blocked_date(
    payload: BlockedDateCreate,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Blocks a calendar date for clinic or specific doctor."""
    blocked_id = add_blocked_date(payload.blocked_date, payload.doctor_id, payload.reason)
    return {"success": True, "blocked_id": blocked_id, "message": "Date blocked successfully."}

@router.delete("/admin/blocked-dates/{blocked_id}")
def api_admin_delete_blocked_date(
    blocked_id: int,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Unblocks a date."""
    success = delete_blocked_date(blocked_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blocked date record not found.")
    return {"success": True, "message": "Date unblocked successfully."}

@router.get("/admin/enquiries")
def api_admin_get_enquiries(admin: Dict[str, Any] = Depends(get_current_admin)):
    """Lists patient inquiries."""
    return {"enquiries": get_enquiries()}

@router.patch("/admin/enquiries/{enquiry_id}/read")
def api_admin_mark_enquiry_read(
    enquiry_id: int,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Marks patient inquiry as read."""
    success = mark_enquiry_read(enquiry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enquiry not found.")
    return {"success": True, "message": "Enquiry marked as read."}
