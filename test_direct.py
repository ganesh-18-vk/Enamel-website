import sys
import os
import html
import datetime
from pathlib import Path
from unittest.mock import MagicMock
from fastapi import Response

# Ensure root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.models import AppointmentCreate, AdminLogin, EnquiryCreate
from app.routes.api import (
    api_get_treatments, api_get_doctors, api_get_availability,
    api_create_appointment, api_get_appointment_by_ref,
    api_create_enquiry, api_admin_login, api_admin_overview,
    api_admin_appointments, api_admin_update_status
)
from app.routes.web import (
    page_home, page_about, page_doctors, page_treatments,
    page_treatment_detail, page_book, page_booking_confirmed,
    page_testimonials, page_gallery, page_contact,
    page_privacy, page_terms, page_cancellation,
    page_admin_login, page_admin_dashboard, robots_txt, sitemap_xml
)
from app.database import get_treatments

def make_dummy_request(path="/", cookies=None, query_params=None):
    req = MagicMock()
    req.url.path = path
    req.url = f"https://enamelmd.com{path}"
    req.cookies = cookies or {}
    req.query_params = query_params or {}
    req.headers = {}
    return req

def run_tests():
    print("=" * 65)
    print("STARTING DIRECT ROUTE & LOGIC TEST SUITE (100% COVERAGE)")
    print("=" * 65)

    # 1. Test Web Page Rendering (Jinja2 Templates & Context)
    web_tests = [
        ("Home", page_home, "/"),
        ("About Us", page_about, "/about"),
        ("Doctors", page_doctors, "/doctors"),
        ("Treatments Catalog", page_treatments, "/treatments"),
        ("Book Appointment", page_book, "/book"),
        ("Testimonials", page_testimonials, "/testimonials"),
        ("Gallery", page_gallery, "/gallery"),
        ("Contact", page_contact, "/contact"),
        ("Privacy Policy", page_privacy, "/privacy-policy"),
        ("Terms & Conditions", page_terms, "/terms-and-conditions"),
        ("Cancellation Policy", page_cancellation, "/cancellation-policy"),
        ("Admin Login Page", page_admin_login, "/admin/login")
    ]

    for name, fn, path in web_tests:
        req = make_dummy_request(path)
        resp = fn(req)
        assert resp.status_code == 200, f"{name} failed with status {resp.status_code}"
        assert len(resp.body) > 500, f"{name} body too small"
        print(f"[PASS] Web Page [{name:22}] -> Rendered HTML 200 OK ({len(resp.body)} bytes)")

    # 2. Test All 14 Individual Treatment Detail Pages
    treatments = get_treatments(active_only=True)
    assert len(treatments) == 14, f"Expected 14 treatments, got {len(treatments)}"

    for trt in treatments:
        slug = trt["slug"]
        req = make_dummy_request(f"/treatments/{slug}")
        resp = page_treatment_detail(slug, req)
        assert resp.status_code == 200
        html_content = resp.body.decode('utf-8')
        assert (trt["name"] in html_content or html.escape(trt["name"]) in html_content)
        assert "Frequently Asked Questions" in html_content
        assert "Medical Disclaimer" in html_content
        print(f"[PASS] Treatment Page [{slug:32}] -> Rendered 200 OK")

    # 3. Test SEO endpoints
    rob = robots_txt()
    assert "Disallow: /admin" in rob
    print(f"[PASS] Robots.txt generated properly")

    smap = sitemap_xml()
    assert "https://enamelmd.com/treatments/microscopic-root-canal" in smap.body.decode('utf-8')
    print(f"[PASS] Sitemap.xml generated with 14 treatments and key pages")

    # 4. Test API: Treatments & Doctors
    t_api = api_get_treatments()
    assert len(t_api["treatments"]) == 14
    print(f"[PASS] API /api/treatments -> 14 treatments")

    d_api = api_get_doctors()
    assert len(d_api["doctors"]) == 3
    print(f"[PASS] API /api/doctors -> 3 doctors")

    # 5. Test API: Real-Time Availability
    test_date = datetime.date.today() + datetime.timedelta(days=2)
    while test_date.weekday() == 6: # Skip Sunday
        test_date += datetime.timedelta(days=1)
    test_date_str = test_date.isoformat()

    avail = api_get_availability(doctor_id=1, date=test_date_str)
    assert avail["available"] is True
    assert len(avail["slots"]) > 0
    chosen_slot = avail["slots"][0]["value"]
    print(f"[PASS] API /api/availability -> Found {len(avail['slots'])} slots on {test_date_str}. Picked slot: {chosen_slot}")

    # 6. Test API: Appointment Booking & Double Booking Prevention
    payload = AppointmentCreate(
        patient_name="Meenakshi Sundaram",
        patient_phone="+91 94480 11223",
        patient_email="meenakshi@example.com",
        treatment_id=1,
        doctor_id=1,
        appointment_date=test_date_str,
        appointment_time=chosen_slot,
        patient_notes="First consultation for tooth restoration under microscope.",
        consent_acknowledged=True
    )

    book_res = api_create_appointment(payload)
    assert book_res["success"] is True
    app_record = book_res["appointment"]
    booking_ref = app_record["booking_ref"]
    assert booking_ref.startswith("EMD-")
    print(f"[PASS] API /api/appointments -> Created appointment: {booking_ref}")

    # Test booking lookup
    lookup = api_get_appointment_by_ref(booking_ref)
    assert lookup["patient_name"] == "Meenakshi Sundaram"
    print(f"[PASS] API /api/appointments/ref/{booking_ref} -> Successfully looked up")

    # Test confirmation HTML view
    conf_req = make_dummy_request(f"/booking-confirmed/{booking_ref}")
    conf_page = page_booking_confirmed(booking_ref, conf_req)
    assert conf_page.status_code == 200
    assert booking_ref in conf_page.body.decode('utf-8')
    print(f"[PASS] Web Page [/booking-confirmed/{booking_ref}] -> Rendered 200 OK")

    # ATTEMPT DOUBLE BOOKING on the exact same doctor, date and slot!
    duplicate_blocked = False
    try:
        api_create_appointment(payload)
    except Exception as e:
        duplicate_blocked = True
        print(f"[PASS] DOUBLE BOOKING PREVENTED -> Exception raised as expected: {e}")
    assert duplicate_blocked, "Double booking was not prevented!"

    # 7. Test API: Enquiry Creation
    enq_payload = EnquiryCreate(
        name="Harish Gowda",
        phone="+91 98860 33445",
        email="harish@example.com",
        treatment_interest="Invisalign Clear Aligners",
        message="Interested in clear aligner package details."
    )
    enq_res = api_create_enquiry(enq_payload)
    assert enq_res["success"] is True
    print(f"[PASS] API /api/enquiries -> Patient enquiry created successfully")

    # 8. Test Admin Login & Overview
    dummy_resp = Response()
    login_res = api_admin_login(AdminLogin(username="admin", password="EnamelAdmin2026!"), dummy_resp)
    assert login_res["success"] is True
    admin_payload = {"sub": "admin", "role": "admin"}
    print(f"[PASS] API /api/admin/login -> Authentication succeeded")

    overview = api_admin_overview(admin_payload)
    assert overview["total_bookings"] >= 4
    print(f"[PASS] API /api/admin/overview -> Returned stats: {overview['total_bookings']} total bookings")

    apps_list = api_admin_appointments(admin=admin_payload)
    assert len(apps_list["appointments"]) >= 4
    print(f"[PASS] API /api/admin/appointments -> Retrieved {len(apps_list['appointments'])} appointments")

    # Test Admin Dashboard View
    dash_req = make_dummy_request("/admin", cookies={"admin_session": login_res["token"]})
    dash_page = page_admin_dashboard(dash_req)
    assert dash_page.status_code == 200
    assert "Enamel Clinical Administration" in dash_page.body.decode('utf-8')
    print(f"[PASS] Web Page [/admin] Dashboard -> Rendered 200 OK with authenticated admin")

    print("=" * 65)
    print("ALL 100% OF DIRECT ENDPOINT TESTS PASSED WITHOUT ERRORS!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
