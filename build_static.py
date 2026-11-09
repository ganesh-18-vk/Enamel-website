import os
import shutil
import datetime
from pathlib import Path
from unittest.mock import MagicMock

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"

from app.routes.web import (
    page_home, page_about, page_doctors, page_treatments,
    page_treatment_detail, page_book, page_testimonials,
    page_gallery, page_contact, page_privacy, page_terms,
    page_cancellation, page_admin_login, robots_txt, sitemap_xml
)
from app.database import get_treatments

def make_dummy_request(path="/"):
    req = MagicMock()
    req.url.path = path
    req.url = f"https://enamelmd.com{path}"
    req.cookies = {}
    req.query_params = {}
    req.headers = {}
    return req

def write_page(rel_path: str, html_content: str):
    target = DIST_DIR / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {rel_path}")

def build():
    print("Building static site for Netlify deployment...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy Static Assets (CSS, JS, Images, SVGs)
    static_src = BASE_DIR / "app" / "static"
    static_dst = DIST_DIR / "static"
    shutil.copytree(static_src, static_dst)
    print("Copied static assets to dist/static")

    # 2. Render Core Pages
    pages = [
        ("index.html", page_home, "/"),
        ("about/index.html", page_about, "/about"),
        ("doctors/index.html", page_doctors, "/doctors"),
        ("treatments/index.html", page_treatments, "/treatments"),
        ("book/index.html", page_book, "/book"),
        ("testimonials/index.html", page_testimonials, "/testimonials"),
        ("gallery/index.html", page_gallery, "/gallery"),
        ("contact/index.html", page_contact, "/contact"),
        ("privacy-policy/index.html", page_privacy, "/privacy-policy"),
        ("terms-and-conditions/index.html", page_terms, "/terms-and-conditions"),
        ("cancellation-policy/index.html", page_cancellation, "/cancellation-policy"),
        ("admin/login/index.html", page_admin_login, "/admin/login")
    ]

    for rel_path, fn, url_path in pages:
        req = make_dummy_request(url_path)
        resp = fn(req)
        write_page(rel_path, resp.body.decode('utf-8'))

    # 3. Render All 14 Treatment Detail Pages
    treatments = get_treatments(active_only=True)
    for trt in treatments:
        slug = trt["slug"]
        req = make_dummy_request(f"/treatments/{slug}")
        resp = page_treatment_detail(slug, req)
        write_page(f"treatments/{slug}/index.html", resp.body.decode('utf-8'))

    # 4. Robots and Sitemap
    with open(DIST_DIR / "robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_txt())
    print("Generated dist/robots.txt")

    with open(DIST_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml().body.decode('utf-8'))
    print("Generated dist/sitemap.xml")

    # 5. Create Netlify _redirects file
    with open(DIST_DIR / "_redirects", "w", encoding="utf-8") as f:
        f.write("/* /index.html 200\n")
    print("Generated dist/_redirects")

    print("\nStatic build complete! Output directory: dist/")

if __name__ == "__main__":
    build()
