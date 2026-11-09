# Enamel Microscopic Dentistry - Premium Web & Appointment Booking Platform

A modern, responsive, production-ready dental clinic web application architected for **Enamel Microscopic Dentistry** (Mysuru, Karnataka, India).

Built with a luxury healthcare aesthetic (deep navy blue, ivory, and champagne-gold accents), semantic HTML5, Tailwind CSS, Lucide icons, and backed by a Python FastAPI + SQLite / Supabase PostgreSQL backend.

---

## 🏥 Clinic Information

- **Business Name:** Enamel Microscopic Dentistry
- **Location:** #42, 2nd Cross, Mahajana Layout, Vijaynagar Main Road, Mysuru, Karnataka 570017, India
- **Phone:** +91 88673 74949
- **Email:** contact@enamelmd.com
- **Existing Website Reference:** [https://enamelmd.com/](https://enamelmd.com/)
- **Operating Schedule:** Monday–Saturday: 10:00 AM–2:00 PM & 4:00 PM–6:30 PM (Sundays unavailable / emergency request)

---

## ✨ Key Features & Architectural Highlights

### 1. Brand Identity & Design System
- **Luxury Aesthetic:** Deep navy (`#0B1B2B`), warm ivory (`#FDFBF7`), subtle champagne gold (`#C5A880`, `#D4AF37`), soft shadows, and generous whitespace.
- **Typography:** Serif headlines (*Playfair Display*) paired with clean sans-serif body (*Plus Jakarta Sans*).
- **Responsive Layout:** Adaptive desktop navigation with interactive treatments mega-menu, mobile slide-over navigation drawer, persistent floating WhatsApp button, and sticky mobile booking CTA bar.

### 2. Specialist Doctors
- **Dr. H S Shreyas:** Chief Microscopic Dentist | Root Canal & Restorative Specialist (BDS JSS Dental College Mysuru, Style Italiano Trained, Member Microscopic Dental Club, 11+ years clinical experience).
- **Dr. Rohit:** Consultant Orthodontist | Certified Invisalign Specialist (BDS, MDS Orthodontics, 9+ years clinical experience).
- **Dr. Jithin:** Consultant Periodontist | Dental Implant Specialist (BDS, MDS Periodontics & Oral Implantology, Advanced Piezosurgery Fellow, 10+ years clinical experience).

### 3. All 14 Dental Treatments with Dedicated Detail Pages
Every service has an individual page featuring procedure background, clinical inclusions, benefits, candidacy indications, step-by-step procedure breakdown, interactive FAQ accordions, transparent medical disclaimers, and 1-click booking pre-selection:
1. **Microscopic Root Canal Treatment** (`/treatments/microscopic-root-canal`)
2. **Cosmetic Dentistry & Bonding** (`/treatments/cosmetic-dentistry`)
3. **Smile Makeovers** (`/treatments/smile-makeovers`)
4. **Dental Veneers and Laminates** (`/treatments/dental-veneers-and-laminates`)
5. **Dental Crowns and Restorations** (`/treatments/dental-crowns-and-restorations`)
6. **Braces and Orthodontics** (`/treatments/braces-and-orthodontics`)
7. **Invisalign Clear Aligners** (`/treatments/invisalign`)
8. **Dental Implants** (`/treatments/dental-implants`)
9. **Laser Dentistry** (`/treatments/laser-dentistry`)
10. **Pediatric Dentistry** (`/treatments/pediatric-dentistry`)
11. **Scaling and Polishing (Dental Cleaning)** (`/treatments/scaling-and-polishing`)
12. **Digital Dental X-rays & Diagnostics** (`/treatments/digital-dental-x-rays`)
13. **Tooth Extraction** (`/treatments/tooth-extraction`)
14. **Oral Surgery & Wisdom Tooth Removal** (`/treatments/oral-surgery`)

### 4. Interactive 6-Step Appointment Booking System
- **Step 1: Treatment Selection:** Choose from all 14 clinical procedures with category search and pricing indications.
- **Step 2: Doctor Selection:** Filtered by procedure specialty or pick any consultant.
- **Step 3: Interactive Calendar:** Visual calendar disabling past dates and Sundays, highlighting open clinic dates.
- **Step 4: Dynamic Time Slot Selection:** Server queries real-time availability (`/api/availability?doctor_id=...&date=...`). Slots respect lunch break (2:00 PM – 4:00 PM) and hide already reserved or blocked dates.
- **Step 5: Patient Details & Policy Consent:** Validates full name, 10-digit mobile number, optional email, notes, and consent acknowledgement.
- **Step 6: Backend-Verified Confirmation:**
  - Double-booking prevention enforced atomically at the database layer.
  - Generates unique reference (e.g. `EMD-2026-A101`).
  - Interactive "Add to Google Calendar", "WhatsApp Confirmation" (`+91 88673 74949`), and Print Appointment Slip actions.

### 5. Secure Admin Dashboard (`/admin`)
- **Authentication:** Protected session token cookie with PBKDF2 salt-hashed credentials.
- **Overview:** KPIs for today's visits, upcoming appointments, pending check-ins, total bookings, and cancellations.
- **Appointment Management:** Live search, date/doctor/treatment/status filters, and one-click Confirm, Cancel, Reschedule, or Complete actions.
- **Doctor Management:** Update profiles, qualifications, and active consultation status.
- **Treatment Management:** Update descriptions, durations, and consultation fees.
- **Schedule Management:** Configure clinic hours, slot duration (30 mins default), and block custom dates/holidays.
- **Enquiry Viewer:** View and manage incoming messages from the contact form.

**Default Admin Credentials:**
- Username: `admin`
- Password: `EnamelAdmin2026!`

### 6. Local SEO & Structured Data
- Schema.org JSON-LD structured data for `Dentist` and `LocalBusiness` specifying geographic coordinates in Vijaynagar Mysuru, verified contact information, and medical specialties.
- Canonical links, Open Graph tags, `/robots.txt`, and XML sitemap (`/sitemap.xml`).

---

## 🗄️ Database & Supabase Integration

The platform includes:
1. **Local Persistent SQLite (`enamel_clinic.db`):** Pre-seeded with doctors, 14 treatments, weekly schedule, sample appointments, and admin credentials. Works out of the box with zero external configuration.
2. **Supabase PostgreSQL Schema (`supabase_schema.sql`):** Complete schema script with Row Level Security (RLS) policies, indexes, foreign keys, and unique constraint preventing overlapping appointments ready to paste into the Supabase SQL Editor.

---

## 🚀 Running The Application Locally

To start the server:

```bash
cd C:\Users\ganes\.gemini\antigravity\scratch\enamel-microscopic-dentistry
python run.py
```

The web platform will be accessible at:
- **Public Website:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Appointment Booking:** [http://127.0.0.1:8000/book](http://127.0.0.1:8000/book)
- **Admin Portal:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 🧪 Automated Verification

Run the test suite:

```bash
python test_direct.py
```

Validates 100% of routes, HTML template rendering, treatment detail pages, dynamic availability calculation, atomic booking creation, double-booking rejection, and admin operations.
