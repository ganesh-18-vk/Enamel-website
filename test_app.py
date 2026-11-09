import sys
import os
import json
import time
import datetime
import threading
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# Ensure root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn
from app.main import app

PORT = 8765
BASE_URL = f"http://127.0.0.1:{PORT}"

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def http_get(path, headers=None):
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=headers or {})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode('utf-8'), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8'), dict(e.headers)

def http_post(path, data, headers=None):
    headers = headers or {}
    headers["Content-Type"] = "application/json"
    raw_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}{path}", data=raw_data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode('utf-8'), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8'), dict(e.headers)

def http_patch(path, data, headers=None):
    headers = headers or {}
    headers["Content-Type"] = "application/json"
    raw_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}{path}", data=raw_data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode('utf-8'), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8'), dict(e.headers)

def run_tests():
    print("=" * 65)
    print("STARTING TEST SUITE: ENAMEL MICROSCOPIC DENTISTRY")
    print("=" * 65)

    server = ServerThread()
    server.daemon = True
    server.start()

    # Wait for server to spin up
    for _ in range(30):
        try:
            status, body, _ = http_get("/")
            if status == 200:
                print(f"✓ Uvicorn server started successfully on {BASE_URL}")
                break
        except Exception:
            time.sleep(0.2)
    else:
        raise RuntimeError("Server failed to start")

    try:
        # 1. Test Static Routes
        routes = [
            ("/", "Precision Dentistry"),
            ("/about", "Redefining Dental Care Through"),
            ("/doctors", "Dedicated Dental Specialists"),
            ("/treatments", "Dental Treatments"),
            ("/book", "Book Your Dental Consultation"),
            ("/testimonials", "Patient Testimonials"),
            ("/gallery", "Clinic &amp; Technology Gallery"),
            ("/contact", "Contact &amp; Location"),
            ("/privacy-policy", "Privacy Policy"),
            ("/terms-and-conditions", "Terms &amp; Conditions"),
            ("/cancellation-policy", "Appointment Cancellation Policy"),
            ("/admin/login", "Clinic Administration"),
            ("/robots.txt", "Disallow: /admin"),
            ("/sitemap.xml", "https://enamelmd.com/"),
        ]

        for path, expected_str in routes:
            status, text, _ = http_get(path)
            assert status == 200, f"Failed {path}: got {status}"
            assert expected_str in text, f"Expected '{expected_str}' in {path}"
            print(f"✓ Route {path:25} -> 200 OK")

        # 2. Test All 14 Individual Treatment Pages
        slugs = [
            "microscopic-root-canal",
            "cosmetic-dentistry",
            "smile-makeovers",
            "dental-veneers-and-laminates",
            "dental-crowns-and-restorations",
            "braces-and-orthodontics",
            "invisalign",
            "dental-implants",
            "laser-dentistry",
            "pediatric-dentistry",
            "scaling-and-polishing",
            "digital-dental-x-rays",
            "tooth-extraction",
            "oral-surgery"
        ]

        for slug in slugs:
            status, text, _ = http_get(f"/treatments/{slug}")
            assert status == 200, f"Failed /treatments/{slug}: got {status}"
            assert "Frequently Asked Questions" in text
            assert "Medical Disclaimer" in text
            print(f"✓ Treatment detail /{slug:35} -> 200 OK")

        # 3. Test API: Treatments & Doctors
        status, text, _ = http_get("/api/treatments")
        assert status == 200
        treatments = json.loads(text)["treatments"]
        assert len(treatments) == 14, f"Expected 14 treatments, got {len(treatments)}"
        print(f"✓ API /api/treatments -> 14 treatments loaded")

        status, text, _ = http_get("/api/doctors")
        assert status == 200
        doctors = json.loads(text)["doctors"]
        assert len(doctors) == 3, f"Expected 3 doctors, got {len(doctors)}"
        print(f"✓ API /api/doctors -> 3 doctors loaded")

        # 4. Test API: Availability Calculation
        test_date = datetime.date.today() + datetime.timedelta(days=2)
        while test_date.weekday() == 6: # Skip Sunday
            test_date += datetime.timedelta(days=1)
        test_date_str = test_date.isoformat()

        status, text, _ = http_get(f"/api/availability?doctor_id=1&date={test_date_str}")
        assert status == 200
        avail_data = json.loads(text)
        assert avail_data["available"] is True
        assert len(avail_data["slots"]) > 0
        test_slot = avail_data["slots"][0]["value"]
        print(f"✓ API /api/availability -> date {test_date_str} has {len(avail_data['slots'])} slots. Picking slot {test_slot}")

        # 5. Test API: Booking Creation & Double Booking Prevention
        booking_payload = {
            "patient_name": "Divya Sharma",
            "patient_phone": "+91 99887 76655",
            "patient_email": "divya.sharma@example.com",
            "treatment_id": 1,
            "doctor_id": 1,
            "appointment_date": test_date_str,
            "appointment_time": test_slot,
            "patient_notes": "First time consultation for microscopic tooth check.",
            "consent_acknowledged": True
        }

        status, text, _ = http_post("/api/appointments", booking_payload)
        assert status == 201, f"Failed booking: {text}"
        res_json = json.loads(text)
        app_data = res_json["appointment"]
        booking_ref = app_data["booking_ref"]
        assert booking_ref.startswith("EMD-")
        print(f"✓ API /api/appointments -> Created appointment with ref {booking_ref}")

        # ATTEMPT DOUBLE BOOKING for the same doctor, date and time
        status_dup, text_dup, _ = http_post("/api/appointments", booking_payload)
        assert status_dup == 400, f"Expected 400 for duplicate slot, got {status_dup}"
        assert "already been reserved" in text_dup or "not available" in text_dup
        print(f"✓ DOUBLE BOOKING PREVENTED -> Server rejected collision with 400 Bad Request")

        # 6. Test Confirmation Page with Booking Ref
        status, text, _ = http_get(f"/booking-confirmed/{booking_ref}")
        assert status == 200
        assert booking_ref in text
        assert "Divya Sharma" in text
        print(f"✓ Route /booking-confirmed/{booking_ref} -> 200 OK")

        # 7. Test API: Contact Enquiry
        enq_payload = {
            "name": "Kavitha R.",
            "phone": "+91 98765 43210",
            "email": "kavitha.r@example.com",
            "treatment_interest": "Smile Makeovers",
            "message": "Interested in cosmetic consultation for wedding."
        }
        status, text, _ = http_post("/api/enquiries", enq_payload)
        assert status == 201
        assert json.loads(text)["success"] is True
        print(f"✓ API /api/enquiries -> Enquiry created")

        # 8. Test Admin Login & Protected Endpoints
        status, _, _ = http_post("/api/admin/login", {"username": "admin", "password": "wrongpassword"})
        assert status == 401

        status, text, headers = http_post("/api/admin/login", {"username": "admin", "password": "EnamelAdmin2026!"})
        assert status == 200
        login_data = json.loads(text)
        assert login_data["success"] is True
        admin_token = login_data["token"]
        auth_headers = {"Cookie": f"admin_session={admin_token}", "Authorization": f"Bearer {admin_token}"}
        print(f"✓ API /api/admin/login -> Authentication successful")

        # Admin Overview
        status, text, _ = http_get("/api/admin/overview", headers=auth_headers)
        assert status == 200
        overview = json.loads(text)
        assert overview["total_bookings"] >= 4
        print(f"✓ API /api/admin/overview -> Returned stats: {overview['total_bookings']} total bookings")

        # Admin Appointments
        status, text, _ = http_get("/api/admin/appointments", headers=auth_headers)
        assert status == 200
        all_apps = json.loads(text)["appointments"]
        assert len(all_apps) >= 4
        print(f"✓ API /api/admin/appointments -> {len(all_apps)} appointments listed")

        # Admin Update Status
        status, _, _ = http_patch(
            f"/api/admin/appointments/{app_data['id']}/status",
            {"status": "Completed", "admin_notes": "Treated under microscope with excellent seal."},
            headers=auth_headers
        )
        assert status == 200
        print(f"✓ API /api/admin/appointments/{app_data['id']}/status -> Status updated to Completed")

        # Admin Schedule
        status, text, _ = http_get("/api/admin/schedule", headers=auth_headers)
        assert status == 200
        assert len(json.loads(text)["schedule"]) == 7
        print(f"✓ API /api/admin/schedule -> 7 days schedule retrieved")

        print("=" * 65)
        print("ALL TESTS PASSED SUCCESSFULLY! (100% VERIFIED)")
        print("=" * 65)

    finally:
        server.stop()

if __name__ == "__main__":
    run_tests()
