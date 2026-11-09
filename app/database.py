import os
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "enamel_clinic.db"

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory and WAL mode enabled for high concurrency."""
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    """Initializes all database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        qualifications TEXT NOT NULL,
        experience_years INTEGER NOT NULL,
        specialization TEXT NOT NULL,
        bio TEXT NOT NULL,
        photo_url TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        short_description TEXT NOT NULL,
        full_description TEXT NOT NULL,
        involves TEXT NOT NULL,
        benefits TEXT NOT NULL,
        candidates TEXT NOT NULL,
        process_steps TEXT NOT NULL,
        faqs TEXT NOT NULL,
        default_doctor_id INTEGER,
        duration_minutes INTEGER DEFAULT 30,
        consultation_fee INTEGER DEFAULT 500,
        image_url TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (default_doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS clinic_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day_of_week INTEGER UNIQUE NOT NULL, -- 0=Monday, ..., 5=Saturday, 6=Sunday
        is_open INTEGER DEFAULT 1,
        morning_start TEXT DEFAULT '10:00',
        morning_end TEXT DEFAULT '14:00',
        evening_start TEXT DEFAULT '16:00',
        evening_end TEXT DEFAULT '18:30',
        slot_duration_minutes INTEGER DEFAULT 30
    );

    CREATE TABLE IF NOT EXISTS doctor_availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL,
        is_available INTEGER DEFAULT 1,
        morning_available INTEGER DEFAULT 1,
        evening_available INTEGER DEFAULT 1,
        UNIQUE(doctor_id, day_of_week),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS blocked_dates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER, -- NULL means clinic-wide
        blocked_date TEXT NOT NULL, -- 'YYYY-MM-DD'
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_ref TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        patient_phone TEXT NOT NULL,
        patient_email TEXT,
        treatment_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL, -- 'YYYY-MM-DD'
        appointment_time TEXT NOT NULL, -- 'HH:MM' (24-hour format)
        status TEXT NOT NULL DEFAULT 'Confirmed', -- 'Pending', 'Confirmed', 'Cancelled', 'Completed', 'Rescheduled'
        patient_notes TEXT,
        admin_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (treatment_id) REFERENCES treatments(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    );

    CREATE INDEX IF NOT EXISTS idx_appointments_date_doctor ON appointments(appointment_date, doctor_id, appointment_time);
    CREATE INDEX IF NOT EXISTS idx_appointments_ref ON appointments(booking_ref);

    CREATE TABLE IF NOT EXISTS enquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        treatment_interest TEXT,
        message TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

def generate_slots_for_window(start_time_str: str, end_time_str: str, duration_mins: int = 30) -> List[str]:
    """Generates time slot strings formatted as 'HH:MM' between start and end times."""
    slots = []
    fmt = "%H:%M"
    current = datetime.datetime.strptime(start_time_str, fmt)
    end = datetime.datetime.strptime(end_time_str, fmt)
    
    while current + datetime.timedelta(minutes=duration_mins) <= end:
        slots.append(current.strftime(fmt))
        current += datetime.timedelta(minutes=duration_mins)
        
    return slots

def get_available_slots(doctor_id: int, date_str: str) -> Dict[str, Any]:
    """
    Computes available slots for a given doctor on a given date (YYYY-MM-DD).
    Respects clinic hours (Mon-Sat 10:00-14:00 and 16:00-18:30, Sunday closed),
    blocked dates/holidays, doctor-specific day availability, and existing bookings.
    """
    conn = get_db_connection()
    try:
        booking_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        conn.close()
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    # Don't allow bookings in the past
    today = datetime.date.today()
    if booking_date < today:
        conn.close()
        return {"available": False, "slots": [], "reason": "Cannot book appointments in the past."}

    day_of_week = booking_date.weekday() # 0 = Monday, ..., 6 = Sunday

    # 1. Check clinic schedule for this day
    schedule_row = conn.execute(
        "SELECT * FROM clinic_schedule WHERE day_of_week = ?", (day_of_week,)
    ).fetchone()

    if not schedule_row or not schedule_row["is_open"]:
        conn.close()
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {
            "available": False, 
            "slots": [], 
            "reason": f"Clinic is closed on {day_names[day_of_week]}s. Please contact the clinic for emergency requests."
        }

    # 2. Check blocked dates (clinic-wide or doctor-specific)
    blocked = conn.execute(
        "SELECT reason FROM blocked_dates WHERE blocked_date = ? AND (doctor_id IS NULL OR doctor_id = ?)",
        (date_str, doctor_id)
    ).fetchone()
    if blocked:
        conn.close()
        return {
            "available": False,
            "slots": [],
            "reason": f"Clinic or doctor is unavailable on this date: {blocked['reason'] or 'Scheduled Leave/Holiday'}."
        }

    # 3. Check doctor specific day availability
    doc_avail = conn.execute(
        "SELECT * FROM doctor_availability WHERE doctor_id = ? AND day_of_week = ?",
        (doctor_id, day_of_week)
    ).fetchone()

    morning_allowed = True
    evening_allowed = True
    if doc_avail:
        if not doc_avail["is_available"]:
            conn.close()
            return {"available": False, "slots": [], "reason": "Doctor is not consulting on this day of the week."}
        morning_allowed = bool(doc_avail["morning_available"])
        evening_allowed = bool(doc_avail["evening_available"])

    slot_duration = schedule_row["slot_duration_minutes"] or 30

    # 4. Generate all potential slots
    candidate_slots = []
    if morning_allowed and schedule_row["morning_start"] and schedule_row["morning_end"]:
        candidate_slots.extend(
            generate_slots_for_window(schedule_row["morning_start"], schedule_row["morning_end"], slot_duration)
        )
    if evening_allowed and schedule_row["evening_start"] and schedule_row["evening_end"]:
        candidate_slots.extend(
            generate_slots_for_window(schedule_row["evening_start"], schedule_row["evening_end"], slot_duration)
        )

    # 5. Fetch booked slots for this doctor on this date
    # Only active statuses block slots: 'Confirmed', 'Pending', 'Rescheduled'
    booked_rows = conn.execute(
        """
        SELECT appointment_time FROM appointments 
        WHERE doctor_id = ? AND appointment_date = ? AND status IN ('Confirmed', 'Pending', 'Rescheduled')
        """,
        (doctor_id, date_str)
    ).fetchall()
    booked_times = set(row["appointment_time"] for row in booked_rows)

    # If booking for today, filter out past time slots
    now = datetime.datetime.now()
    available_slots = []
    for slot in candidate_slots:
        if slot in booked_times:
            continue
        if booking_date == today:
            slot_dt = datetime.datetime.strptime(f"{date_str} {slot}", "%Y-%m-%d %H:%M")
            if slot_dt <= now + datetime.timedelta(minutes=30): # Allow at least 30m advance notice
                continue
        available_slots.append(slot)

    conn.close()

    # Format slots with 12-hour AM/PM label for user display
    formatted_slots = []
    for s in available_slots:
        dt = datetime.datetime.strptime(s, "%H:%M")
        formatted_slots.append({
            "value": s,
            "label": dt.strftime("%I:%M %p")
        })

    return {
        "available": len(formatted_slots) > 0,
        "date": date_str,
        "doctor_id": doctor_id,
        "slots": formatted_slots,
        "total_available": len(formatted_slots)
    }

def create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates an appointment atomically with double-booking prevention.
    Returns the created appointment record with doctor and treatment details.
    """
    import secrets
    conn = get_db_connection()
    cursor = conn.cursor()

    doctor_id = data["doctor_id"]
    treatment_id = data["treatment_id"]
    app_date = data["appointment_date"]
    app_time = data["appointment_time"]

    try:
        # Atomic lock check inside transaction
        cursor.execute("BEGIN IMMEDIATE;")
        
        # 1. Double-booking check
        existing = cursor.execute("""
            SELECT id, booking_ref FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? 
            AND status IN ('Confirmed', 'Pending', 'Rescheduled')
        """, (doctor_id, app_date, app_time)).fetchone()

        if existing:
            conn.rollback()
            conn.close()
            raise ValueError(f"Selected slot {app_time} on {app_date} has already been reserved. Please choose another time.")

        # 2. Verify doctor and treatment exist
        doc = cursor.execute("SELECT name, title, specialization FROM doctors WHERE id = ? AND is_active = 1", (doctor_id,)).fetchone()
        if not doc:
            conn.rollback()
            conn.close()
            raise ValueError("Selected doctor is not available.")

        trt = cursor.execute("SELECT name, duration_minutes, consultation_fee FROM treatments WHERE id = ? AND is_active = 1", (treatment_id,)).fetchone()
        if not trt:
            conn.rollback()
            conn.close()
            raise ValueError("Selected treatment is not available.")

        # 3. Generate unique booking reference: EMD-YYYY-XXXX
        year = datetime.datetime.now().year
        random_suffix = secrets.token_hex(2).upper()
        count_today = cursor.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] + 1
        booking_ref = f"EMD-{year}-{random_suffix}{count_today:02d}"

        # 4. Insert appointment record
        cursor.execute("""
            INSERT INTO appointments (
                booking_ref, patient_name, patient_phone, patient_email,
                treatment_id, doctor_id, appointment_date, appointment_time,
                status, patient_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
        """, (
            booking_ref,
            data["patient_name"].strip(),
            data["patient_phone"].strip(),
            data.get("patient_email", "").strip() if data.get("patient_email") else None,
            treatment_id,
            doctor_id,
            app_date,
            app_time,
            data.get("patient_notes", "").strip() if data.get("patient_notes") else None
        ))

        appointment_id = cursor.lastrowid
        conn.commit()

        # Format readable time for confirmation
        time_obj = datetime.datetime.strptime(app_time, "%H:%M")
        formatted_time = time_obj.strftime("%I:%M %p")

        result = {
            "id": appointment_id,
            "booking_ref": booking_ref,
            "patient_name": data["patient_name"].strip(),
            "patient_phone": data["patient_phone"].strip(),
            "patient_email": data.get("patient_email"),
            "doctor_id": doctor_id,
            "doctor_name": doc["name"],
            "doctor_title": doc["title"],
            "doctor_specialization": doc["specialization"],
            "treatment_id": treatment_id,
            "treatment_name": trt["name"],
            "duration_minutes": trt["duration_minutes"],
            "consultation_fee": trt["consultation_fee"],
            "appointment_date": app_date,
            "appointment_time": app_time,
            "formatted_time": formatted_time,
            "status": "Confirmed",
            "clinic_name": "Enamel Microscopic Dentistry",
            "clinic_address": "#42, 2nd Cross, Mahajana Layout, Vijaynagar Main Road, Mysuru, Karnataka 570017",
            "clinic_phone": "+91 88673 74949",
            "clinic_email": "contact@enamelmd.com"
        }
        return result

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_appointment_by_ref(booking_ref: str) -> Optional[Dict[str, Any]]:
    """Fetches an appointment by its unique booking reference with doctor and treatment details."""
    conn = get_db_connection()
    row = conn.execute("""
        SELECT a.*, 
               d.name AS doctor_name, d.title AS doctor_title, d.specialization AS doctor_specialization, d.photo_url AS doctor_photo,
               t.name AS treatment_name, t.slug AS treatment_slug, t.duration_minutes, t.consultation_fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN treatments t ON a.treatment_id = t.id
        WHERE a.booking_ref = ?
    """, (booking_ref.strip(),)).fetchone()
    conn.close()

    if not row:
        return None

    app = dict(row)
    time_obj = datetime.datetime.strptime(app["appointment_time"], "%H:%M")
    app["formatted_time"] = time_obj.strftime("%I:%M %p")
    return app

def update_appointment_status(appointment_id: int, status: str, admin_notes: Optional[str] = None) -> bool:
    """Updates appointment status and administrative notes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments 
        SET status = ?, admin_notes = COALESCE(?, admin_notes), updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, admin_notes, appointment_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def reschedule_appointment(appointment_id: int, new_date: str, new_time: str, doctor_id: Optional[int] = None, reason: Optional[str] = None) -> Dict[str, Any]:
    """Reschedules an existing appointment to a new date and time."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE;")
        app = cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
        if not app:
            raise ValueError("Appointment not found.")

        target_doctor_id = doctor_id if doctor_id is not None else app["doctor_id"]

        # Check collision
        collision = cursor.execute("""
            SELECT id FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ? 
            AND id != ? AND status IN ('Confirmed', 'Pending', 'Rescheduled')
        """, (target_doctor_id, new_date, new_time, appointment_id)).fetchone()

        if collision:
            raise ValueError(f"Slot {new_time} on {new_date} is already occupied.")

        note_append = f"Rescheduled to {new_date} {new_time}. Reason: {reason or 'Requested by patient'}"
        cursor.execute("""
            UPDATE appointments 
            SET doctor_id = ?, appointment_date = ?, appointment_time = ?, 
                status = 'Rescheduled', 
                admin_notes = CASE WHEN admin_notes IS NULL THEN ? ELSE admin_notes || ' | ' || ? END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (target_doctor_id, new_date, new_time, note_append, note_append, appointment_id))

        conn.commit()
        return {"success": True, "message": "Appointment rescheduled successfully."}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_doctors(active_only: bool = True) -> List[Dict[str, Any]]:
    """Returns list of doctors with their profiles."""
    conn = get_db_connection()
    query = "SELECT * FROM doctors"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY id ASC"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_doctor_by_id(doctor_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_doctor_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM doctors WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_doctor(doctor_id: int, data: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE doctors SET 
            name = ?, title = ?, qualifications = ?, experience_years = ?, 
            specialization = ?, bio = ?, photo_url = COALESCE(?, photo_url), is_active = ?
        WHERE id = ?
    """, (
        data["name"], data["title"], data["qualifications"], data["experience_years"],
        data["specialization"], data["bio"], data.get("photo_url"),
        1 if data.get("is_active", True) else 0, doctor_id
    ))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_treatments(active_only: bool = True) -> List[Dict[str, Any]]:
    """Returns all treatments with JSON fields parsed into Python data structures."""
    import json
    conn = get_db_connection()
    query = """
        SELECT t.*, d.name AS default_doctor_name, d.specialization AS default_doctor_specialization
        FROM treatments t
        LEFT JOIN doctors d ON t.default_doctor_id = d.id
    """
    if active_only:
        query += " WHERE t.is_active = 1"
    query += " ORDER BY t.id ASC"
    rows = conn.execute(query).fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        for key in ["involves", "benefits", "candidates", "process_steps", "faqs"]:
            if item.get(key):
                try:
                    item[key] = json.loads(item[key])
                except Exception:
                    item[key] = []
            else:
                item[key] = []
        result.append(item)
    return result

def get_treatment_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    import json
    conn = get_db_connection()
    row = conn.execute("""
        SELECT t.*, d.name AS default_doctor_name, d.title AS default_doctor_title, 
               d.specialization AS default_doctor_specialization, d.photo_url AS default_doctor_photo
        FROM treatments t
        LEFT JOIN doctors d ON t.default_doctor_id = d.id
        WHERE t.slug = ?
    """, (slug,)).fetchone()
    conn.close()

    if not row:
        return None

    item = dict(row)
    for key in ["involves", "benefits", "candidates", "process_steps", "faqs"]:
        if item.get(key):
            try:
                item[key] = json.loads(item[key])
            except Exception:
                item[key] = []
        else:
            item[key] = []
    return item

def get_treatment_by_id(treatment_id: int) -> Optional[Dict[str, Any]]:
    import json
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,)).fetchone()
    conn.close()
    if not row:
        return None
    item = dict(row)
    for key in ["involves", "benefits", "candidates", "process_steps", "faqs"]:
        if item.get(key):
            try:
                item[key] = json.loads(item[key])
            except Exception:
                item[key] = []
        else:
            item[key] = []
    return item

def update_treatment(treatment_id: int, data: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE treatments SET 
            short_description = COALESCE(?, short_description),
            full_description = COALESCE(?, full_description),
            duration_minutes = COALESCE(?, duration_minutes),
            consultation_fee = COALESCE(?, consultation_fee),
            is_active = COALESCE(?, is_active)
        WHERE id = ?
    """, (
        data.get("short_description"), data.get("full_description"),
        data.get("duration_minutes"), data.get("consultation_fee"),
        data.get("is_active"), treatment_id
    ))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def save_enquiry(data: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO enquiries (name, phone, email, treatment_interest, message)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["name"].strip(),
        data["phone"].strip(),
        data.get("email", "").strip() if data.get("email") else None,
        data.get("treatment_interest"),
        data["message"].strip()
    ))
    enquiry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return enquiry_id

def get_enquiries() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM enquiries ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_enquiry_read(enquiry_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE enquiries SET is_read = 1 WHERE id = ?", (enquiry_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def verify_admin_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    import hashlib
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if not user:
        return None

    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(user["salt"]), 100000).hex()
    if pw_hash == user["password_hash"]:
        return {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"]
        }
    return None

def get_admin_overview() -> Dict[str, Any]:
    conn = get_db_connection()
    today_str = datetime.date.today().isoformat()

    total_bookings = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    today_appointments = conn.execute(
        "SELECT COUNT(*) FROM appointments WHERE appointment_date = ? AND status != 'Cancelled'", (today_str,)
    ).fetchone()[0]
    upcoming_appointments = conn.execute(
        "SELECT COUNT(*) FROM appointments WHERE appointment_date >= ? AND status IN ('Confirmed', 'Pending', 'Rescheduled')", (today_str,)
    ).fetchone()[0]
    pending_requests = conn.execute(
        "SELECT COUNT(*) FROM appointments WHERE status = 'Pending'"
    ).fetchone()[0]
    cancelled_count = conn.execute(
        "SELECT COUNT(*) FROM appointments WHERE status = 'Cancelled'"
    ).fetchone()[0]
    unread_enquiries = conn.execute(
        "SELECT COUNT(*) FROM enquiries WHERE is_read = 0"
    ).fetchone()[0]

    # Recent 5 appointments
    recent_rows = conn.execute("""
        SELECT a.*, d.name AS doctor_name, t.name AS treatment_name
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN treatments t ON a.treatment_id = t.id
        ORDER BY a.created_at DESC LIMIT 5
    """).fetchall()

    conn.close()

    return {
        "today_appointments": today_appointments,
        "upcoming_appointments": upcoming_appointments,
        "total_bookings": total_bookings,
        "pending_requests": pending_requests,
        "cancelled_count": cancelled_count,
        "unread_enquiries": unread_enquiries,
        "recent_appointments": [dict(r) for r in recent_rows]
    }

def get_admin_appointments(
    search: Optional[str] = None,
    date_filter: Optional[str] = None,
    doctor_id: Optional[int] = None,
    treatment_id: Optional[int] = None,
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    query = """
        SELECT a.*, 
               d.name AS doctor_name, d.specialization AS doctor_specialization,
               t.name AS treatment_name, t.duration_minutes, t.consultation_fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN treatments t ON a.treatment_id = t.id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (a.patient_name LIKE ? OR a.patient_phone LIKE ? OR a.booking_ref LIKE ?)"
        s = f"%{search.strip()}%"
        params.extend([s, s, s])
    if date_filter:
        query += " AND a.appointment_date = ?"
        params.append(date_filter)
    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id)
    if treatment_id:
        query += " AND a.treatment_id = ?"
        params.append(treatment_id)
    if status_filter:
        query += " AND a.status = ?"
        params.append(status_filter)

    query += " ORDER BY a.appointment_date DESC, a.appointment_time ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        dt = datetime.datetime.strptime(item["appointment_time"], "%H:%M")
        item["formatted_time"] = dt.strftime("%I:%M %p")
        result.append(item)
    return result

def get_clinic_schedule() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM clinic_schedule ORDER BY day_of_week ASC").fetchall()
    conn.close()
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result = []
    for r in rows:
        d = dict(r)
        d["day_name"] = day_names[d["day_of_week"]]
        result.append(d)
    return result

def update_schedule_day(day_of_week: int, is_open: bool, morning_start: str, morning_end: str, evening_start: str, evening_end: str, slot_duration: int = 30) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clinic_schedule SET 
            is_open = ?, morning_start = ?, morning_end = ?, 
            evening_start = ?, evening_end = ?, slot_duration_minutes = ?
        WHERE day_of_week = ?
    """, (1 if is_open else 0, morning_start, morning_end, evening_start, evening_end, slot_duration, day_of_week))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_blocked_dates() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT b.*, d.name AS doctor_name 
        FROM blocked_dates b
        LEFT JOIN doctors d ON b.doctor_id = d.id
        ORDER BY b.blocked_date ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_blocked_date(blocked_date: str, doctor_id: Optional[int] = None, reason: Optional[str] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blocked_dates (blocked_date, doctor_id, reason)
        VALUES (?, ?, ?)
    """, (blocked_date, doctor_id, reason))
    blocked_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return blocked_id

def delete_blocked_date(blocked_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_dates WHERE id = ?", (blocked_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
