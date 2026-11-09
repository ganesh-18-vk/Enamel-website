from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .seed import seed_database
from .routes import api, web

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Enamel Microscopic Dentistry",
    description="Premium dental clinic web platform with real-time appointment booking and management.",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include Routers
app.include_router(api.router)
app.include_router(web.router)

@app.on_event("startup")
def on_startup():
    """Ensure database tables, doctors, treatments and admin credentials are fully seeded."""
    seed_database()

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Custom luxury 404 page for unmatched routes."""
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Page Not Found | Enamel Microscopic Dentistry</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1B2B] text-slate-100 flex items-center justify-center min-h-screen px-4">
  <div class="max-w-md text-center p-8 bg-[#0F2438] rounded-2xl border border-[#C5A880]/30 shadow-2xl">
    <div class="text-[#C5A880] text-6xl font-serif font-bold mb-4">404</div>
    <h1 class="text-2xl font-serif font-bold text-white mb-2">Page Not Found</h1>
    <p class="text-slate-400 mb-6 text-sm">The dental page or service you are looking for has been moved or does not exist.</p>
    <a href="/" class="inline-block px-6 py-3 bg-[#C5A880] text-[#0B1B2B] font-semibold rounded-lg hover:bg-[#D4AF37] transition">Return to Home</a>
  </div>
</body>
</html>""",
        status_code=404
    )
