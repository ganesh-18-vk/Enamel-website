from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from ..database import (
    get_treatments, get_treatment_by_slug, get_doctors, get_doctor_by_slug,
    get_appointment_by_ref, get_clinic_schedule
)
from ..auth import optional_admin

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)

CLINIC_INFO = {
    "name": "Enamel Microscopic Dentistry",
    "tagline": "Precision Dentistry. Beautiful Smiles. Exceptional Care.",
    "phone": "+91 88673 74949",
    "phone_clean": "918867374949",
    "email": "contact@enamelmd.com",
    "address": "#42, 2nd Cross, Mahajana Layout, Vijaynagar Main Road, Mysuru, Karnataka 570017",
    "city": "Mysuru",
    "state": "Karnataka",
    "pincode": "570017",
    "map_url": "https://maps.google.com/?q=Enamel+Microscopic+Dentistry+Vijaynagar+Main+Road+Mysuru",
    "whatsapp_prefill": "Hello Enamel Microscopic Dentistry, I would like to enquire about booking a dental appointment.",
    "hours": "Mon–Sat: 10:00 AM–2:00 PM & 4:00 PM–6:30 PM | Sun: Contact clinic to confirm availability"
}

@router.get("/", response_class=HTMLResponse)
def page_home(request: Request):
    doctors = get_doctors(active_only=True)
    treatments = get_treatments(active_only=True)
    return templates.TemplateResponse(request=request, name="index.html", context={
        "clinic": CLINIC_INFO,
        "doctors": doctors,
        "treatments": treatments,
        "active_page": "home"
    })

@router.get("/about", response_class=HTMLResponse)
def page_about(request: Request):
    doctors = get_doctors(active_only=True)
    return templates.TemplateResponse(request=request, name="about.html", context={
        "clinic": CLINIC_INFO,
        "doctors": doctors,
        "active_page": "about"
    })

@router.get("/doctors", response_class=HTMLResponse)
def page_doctors(request: Request):
    doctors = get_doctors(active_only=True)
    return templates.TemplateResponse(request=request, name="doctors.html", context={
        "clinic": CLINIC_INFO,
        "doctors": doctors,
        "active_page": "doctors"
    })

@router.get("/treatments", response_class=HTMLResponse)
def page_treatments(request: Request):
    treatments = get_treatments(active_only=True)
    return templates.TemplateResponse(request=request, name="treatments.html", context={
        "clinic": CLINIC_INFO,
        "treatments": treatments,
        "active_page": "treatments"
    })

@router.get("/treatments/{slug}", response_class=HTMLResponse)
def page_treatment_detail(slug: str, request: Request):
    treatment = get_treatment_by_slug(slug)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found.")
    all_treatments = get_treatments(active_only=True)
    related = [t for t in all_treatments if t["slug"] != slug and t["category"] == treatment["category"]][:3]
    if not related:
        related = [t for t in all_treatments if t["slug"] != slug][:3]
    return templates.TemplateResponse(request=request, name="treatment_detail.html", context={
        "clinic": CLINIC_INFO,
        "treatment": treatment,
        "related": related,
        "active_page": "treatments"
    })

@router.get("/book", response_class=HTMLResponse)
def page_book(request: Request, treatment: str = None, doctor: int = None):
    treatments = get_treatments(active_only=True)
    doctors = get_doctors(active_only=True)
    return templates.TemplateResponse(request=request, name="book.html", context={
        "clinic": CLINIC_INFO,
        "treatments": treatments,
        "doctors": doctors,
        "preselect_treatment": treatment,
        "preselect_doctor": doctor,
        "active_page": "book"
    })

@router.get("/booking-confirmed/{booking_ref}", response_class=HTMLResponse)
def page_booking_confirmed(booking_ref: str, request: Request):
    appointment = get_appointment_by_ref(booking_ref)
    if not appointment:
        return RedirectResponse(url="/book")
    return templates.TemplateResponse(request=request, name="confirmation.html", context={
        "clinic": CLINIC_INFO,
        "appointment": appointment,
        "active_page": "book"
    })

@router.get("/testimonials", response_class=HTMLResponse)
def page_testimonials(request: Request):
    return templates.TemplateResponse(request=request, name="testimonials.html", context={
        "clinic": CLINIC_INFO,
        "active_page": "testimonials"
    })

@router.get("/gallery", response_class=HTMLResponse)
def page_gallery(request: Request):
    return templates.TemplateResponse(request=request, name="gallery.html", context={
        "clinic": CLINIC_INFO,
        "active_page": "gallery"
    })

@router.get("/contact", response_class=HTMLResponse)
def page_contact(request: Request):
    schedule = get_clinic_schedule()
    return templates.TemplateResponse(request=request, name="contact.html", context={
        "clinic": CLINIC_INFO,
        "schedule": schedule,
        "active_page": "contact"
    })

@router.get("/privacy-policy", response_class=HTMLResponse)
def page_privacy(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.html", context={
        "clinic": CLINIC_INFO,
        "active_page": "privacy"
    })

@router.get("/terms-and-conditions", response_class=HTMLResponse)
def page_terms(request: Request):
    return templates.TemplateResponse(request=request, name="terms.html", context={
        "clinic": CLINIC_INFO,
        "active_page": "terms"
    })

@router.get("/cancellation-policy", response_class=HTMLResponse)
def page_cancellation(request: Request):
    return templates.TemplateResponse(request=request, name="cancellation.html", context={
        "clinic": CLINIC_INFO,
        "active_page": "cancellation"
    })

# ================= ADMIN VIEWS =================

@router.get("/admin/login", response_class=HTMLResponse)
def page_admin_login(request: Request):
    admin = optional_admin(request)
    if admin:
        return RedirectResponse(url="/admin")
    return templates.TemplateResponse(request=request, name="admin_login.html", context={
        "clinic": CLINIC_INFO,
        "active_page": "admin"
    })

@router.get("/admin", response_class=HTMLResponse)
def page_admin_dashboard(request: Request):
    admin = optional_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login")
    doctors = get_doctors(active_only=False)
    treatments = get_treatments(active_only=False)
    return templates.TemplateResponse(request=request, name="admin_dashboard.html", context={
        "clinic": CLINIC_INFO,
        "admin_user": admin,
        "doctors": doctors,
        "treatments": treatments,
        "active_page": "admin"
    })

# ================= SEO FILES =================

@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/admin

Sitemap: https://enamelmd.com/sitemap.xml
"""
    return content

@router.get("/sitemap.xml")
def sitemap_xml():
    treatments = get_treatments(active_only=True)
    urls = [
        "https://enamelmd.com/",
        "https://enamelmd.com/about",
        "https://enamelmd.com/doctors",
        "https://enamelmd.com/treatments",
        "https://enamelmd.com/book",
        "https://enamelmd.com/testimonials",
        "https://enamelmd.com/gallery",
        "https://enamelmd.com/contact",
        "https://enamelmd.com/privacy-policy",
        "https://enamelmd.com/terms-and-conditions",
        "https://enamelmd.com/cancellation-policy"
    ]
    for t in treatments:
        urls.append(f"https://enamelmd.com/treatments/{t['slug']}")

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        priority = "1.0" if url == "https://enamelmd.com/" else ("0.9" if "/treatments" in url or "/book" in url else "0.8")
        xml.append("  <url>")
        xml.append(f"    <loc>{url}</loc>")
        xml.append("    <changefreq>weekly</changefreq>")
        xml.append(f"    <priority>{priority}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")
    return Response(content="\n".join(xml), media_type="application/xml")
