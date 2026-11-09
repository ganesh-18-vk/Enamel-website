-- ==============================================================================
-- SUPABASE POSTGRESQL SCHEMA FOR ENAMEL MICROSCOPIC DENTISTRY
-- Location: #42, 2nd Cross, Mahajana Layout, Vijaynagar Main Road, Mysuru, Karnataka
-- Database: Supabase / PostgreSQL 15+
-- ==============================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. DOCTORS TABLE
CREATE TABLE IF NOT EXISTS public.doctors (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    title VARCHAR(255) NOT NULL,
    qualifications VARCHAR(255) NOT NULL,
    experience_years INT NOT NULL DEFAULT 5,
    specialization TEXT NOT NULL,
    bio TEXT NOT NULL,
    photo_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 2. TREATMENTS TABLE
CREATE TABLE IF NOT EXISTS public.treatments (
    id BIGSERIAL PRIMARY KEY,
    slug VARCHAR(150) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    short_description TEXT NOT NULL,
    full_description TEXT NOT NULL,
    involves JSONB NOT NULL DEFAULT '[]'::jsonb,
    benefits JSONB NOT NULL DEFAULT '[]'::jsonb,
    candidates JSONB NOT NULL DEFAULT '[]'::jsonb,
    process_steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    faqs JSONB NOT NULL DEFAULT '[]'::jsonb,
    default_doctor_id BIGINT REFERENCES public.doctors(id) ON DELETE SET NULL,
    duration_minutes INT NOT NULL DEFAULT 30,
    consultation_fee INT NOT NULL DEFAULT 500,
    image_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 3. CLINIC SCHEDULE TABLE (Weekly Operating Hours)
CREATE TABLE IF NOT EXISTS public.clinic_schedule (
    id BIGSERIAL PRIMARY KEY,
    day_of_week INT UNIQUE NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Monday, 6=Sunday
    is_open BOOLEAN NOT NULL DEFAULT TRUE,
    morning_start TIME WITHOUT TIME ZONE DEFAULT '10:00',
    morning_end TIME WITHOUT TIME ZONE DEFAULT '14:00',
    evening_start TIME WITHOUT TIME ZONE DEFAULT '16:00',
    evening_end TIME WITHOUT TIME ZONE DEFAULT '18:30',
    slot_duration_minutes INT NOT NULL DEFAULT 30
);

-- 4. DOCTOR AVAILABILITY TABLE
CREATE TABLE IF NOT EXISTS public.doctor_availability (
    id BIGSERIAL PRIMARY KEY,
    doctor_id BIGINT NOT NULL REFERENCES public.doctors(id) ON DELETE CASCADE,
    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    morning_available BOOLEAN NOT NULL DEFAULT TRUE,
    evening_available BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(doctor_id, day_of_week)
);

-- 5. BLOCKED DATES & HOLIDAYS TABLE
CREATE TABLE IF NOT EXISTS public.blocked_dates (
    id BIGSERIAL PRIMARY KEY,
    doctor_id BIGINT REFERENCES public.doctors(id) ON DELETE CASCADE, -- NULL means clinic-wide
    blocked_date DATE NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 6. APPOINTMENTS TABLE
CREATE TABLE IF NOT EXISTS public.appointments (
    id BIGSERIAL PRIMARY KEY,
    booking_ref VARCHAR(50) UNIQUE NOT NULL,
    patient_name VARCHAR(150) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    patient_email VARCHAR(150),
    treatment_id BIGINT NOT NULL REFERENCES public.treatments(id),
    doctor_id BIGINT NOT NULL REFERENCES public.doctors(id),
    appointment_date DATE NOT NULL,
    appointment_time TIME WITHOUT TIME ZONE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Confirmed' CHECK (status IN ('Pending', 'Confirmed', 'Cancelled', 'Completed', 'Rescheduled')),
    patient_notes TEXT,
    admin_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- Prevention of double-booking: Unique active index for doctor, date, and time
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_appointment 
ON public.appointments (doctor_id, appointment_date, appointment_time) 
WHERE (status IN ('Confirmed', 'Pending', 'Rescheduled'));

CREATE INDEX IF NOT EXISTS idx_appointments_ref ON public.appointments(booking_ref);
CREATE INDEX IF NOT EXISTS idx_appointments_date_doc ON public.appointments(appointment_date, doctor_id);

-- 7. PATIENT ENQUIRIES TABLE
CREATE TABLE IF NOT EXISTS public.enquiries (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(150),
    treatment_interest VARCHAR(150),
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

-- 8. ROW LEVEL SECURITY (RLS) POLICIES
ALTER TABLE public.doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.treatments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clinic_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doctor_availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blocked_dates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enquiries ENABLE ROW LEVEL SECURITY;

-- Public can read active doctors, treatments, schedules
CREATE POLICY "Public can view active doctors" ON public.doctors FOR SELECT USING (is_active = true);
CREATE POLICY "Public can view active treatments" ON public.treatments FOR SELECT USING (is_active = true);
CREATE POLICY "Public can view clinic schedule" ON public.clinic_schedule FOR SELECT USING (true);
CREATE POLICY "Public can view doctor availability" ON public.doctor_availability FOR SELECT USING (true);
CREATE POLICY "Public can view blocked dates" ON public.blocked_dates FOR SELECT USING (true);

-- Public can insert new appointments and enquiries
CREATE POLICY "Public can book appointments" ON public.appointments FOR INSERT WITH CHECK (true);
CREATE POLICY "Public can lookup appointment by reference" ON public.appointments FOR SELECT USING (true);
CREATE POLICY "Public can submit enquiries" ON public.enquiries FOR INSERT WITH CHECK (true);

-- Authenticated admins have full management permissions
CREATE POLICY "Admins have full access to doctors" ON public.doctors FOR ALL TO authenticated USING (true);
CREATE POLICY "Admins have full access to treatments" ON public.treatments FOR ALL TO authenticated USING (true);
CREATE POLICY "Admins have full access to schedule" ON public.clinic_schedule FOR ALL TO authenticated USING (true);
CREATE POLICY "Admins have full access to appointments" ON public.appointments FOR ALL TO authenticated USING (true);
CREATE POLICY "Admins have full access to enquiries" ON public.enquiries FOR ALL TO authenticated USING (true);
