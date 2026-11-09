import os
from pathlib import Path

IMAGES_DIR = Path(__file__).resolve().parent / "static" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def create_svg(filename: str, content: str):
    path = IMAGES_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Generated {filename}")

# 1. LOGO
logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 80" width="340" height="80">
  <defs>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E2CA9E"/>
      <stop offset="50%" stop-color="#C5A880"/>
      <stop offset="100%" stop-color="#9E7B47"/>
    </linearGradient>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#162E47"/>
      <stop offset="100%" stop-color="#0B1B2B"/>
    </linearGradient>
  </defs>
  <!-- Icon Symbol: Stylized tooth with microscopic crosshairs and gold facets -->
  <g transform="translate(10, 8)">
    <rect x="0" y="0" width="64" height="64" rx="16" fill="url(#blueGrad)" stroke="url(#goldGrad)" stroke-width="1.5"/>
    <!-- Tooth silhouette -->
    <path d="M 22 20 C 22 16, 27 15, 32 18 C 37 15, 42 16, 42 20 C 42 26, 40 32, 38 46 C 37 49, 34 50, 33 44 C 32 40, 32 40, 31 44 C 30 50, 27 49, 26 46 C 24 32, 22 26, 22 20 Z" fill="none" stroke="#FDFBF7" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
    <!-- Microscopic optical reticle & lens ring -->
    <circle cx="32" cy="28" r="9" fill="none" stroke="url(#goldGrad)" stroke-width="1.8"/>
    <circle cx="32" cy="28" r="3" fill="url(#goldGrad)"/>
    <line x1="32" y1="15" x2="32" y2="21" stroke="url(#goldGrad)" stroke-width="1.5"/>
    <line x1="32" y1="35" x2="32" y2="41" stroke="url(#goldGrad)" stroke-width="1.5"/>
    <line x1="19" y1="28" x2="25" y2="28" stroke="url(#goldGrad)" stroke-width="1.5"/>
    <line x1="39" y1="28" x2="45" y2="28" stroke="url(#goldGrad)" stroke-width="1.5"/>
    <!-- Precision sparkle -->
    <polygon points="46,14 48,18 52,19 48,20 46,24 44,20 40,19 44,18" fill="url(#goldGrad)"/>
  </g>
  <!-- Text Brand -->
  <g transform="translate(86, 22)">
    <text x="0" y="20" font-family="'Playfair Display', Georgia, serif" font-size="22" font-weight="700" letter-spacing="3" fill="#0B1B2B">ENAMEL</text>
    <text x="1" y="38" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="9.5" font-weight="600" letter-spacing="2.2" fill="#C5A880">MICROSCOPIC DENTISTRY</text>
    <text x="1" y="49" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="7.5" font-weight="500" letter-spacing="1.5" fill="#64748B">MYSURU • KARNATAKA</text>
  </g>
</svg>"""
create_svg("logo.svg", logo_svg)

# 2. LOGO WHITE (for dark footer and hero navbar)
logo_white_svg = logo_svg.replace('fill="#0B1B2B">ENAMEL', 'fill="#FFFFFF">ENAMEL').replace('fill="#64748B">MYSURU', 'fill="#94A3B8">MYSURU')
create_svg("logo-white.svg", logo_white_svg)

# Doctor SVGs
def doctor_svg(name: str, spec: str, exp: str, bg_color: str, tie_color: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 480" width="400" height="480">
  <defs>
    <linearGradient id="docBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="#0B1B2B"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#E2CA9E"/>
      <stop offset="100%" stop-color="#C5A880"/>
    </linearGradient>
    <radialGradient id="lightSpot" cx="50%" cy="30%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="400" height="480" fill="url(#docBg)"/>
  <rect width="400" height="480" fill="url(#lightSpot)"/>
  
  <!-- Optical grid pattern background -->
  <g opacity="0.1" stroke="#FDFBF7" stroke-width="0.8">
    <line x1="50" y1="0" x2="50" y2="480"/>
    <line x1="150" y1="0" x2="150" y2="480"/>
    <line x1="250" y1="0" x2="250" y2="480"/>
    <line x1="350" y1="0" x2="350" y2="480"/>
    <line x1="0" y1="100" x2="400" y2="100"/>
    <line x1="0" y1="200" x2="400" y2="200"/>
    <line x1="0" y1="300" x2="400" y2="300"/>
    <circle cx="200" cy="180" r="140" fill="none" stroke="url(#gold)" stroke-width="1.5" stroke-dasharray="4 4"/>
  </g>

  <!-- Doctor Silhouette & Attire -->
  <g transform="translate(0, 10)">
    <!-- Coat shoulders -->
    <path d="M 60 480 L 110 320 L 160 260 L 240 260 L 290 320 L 340 480 Z" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="2"/>
    <!-- Medical collar / inner scrub shirt -->
    <polygon points="160,260 200,350 240,260" fill="{tie_color}"/>
    <polygon points="175,260 200,320 225,260" fill="#FFFFFF"/>
    <!-- Neck -->
    <rect x="175" y="210" width="50" height="60" rx="10" fill="#D4A373"/>
    <!-- Head / Face -->
    <ellipse cx="200" cy="165" rx="55" ry="68" fill="#E8C39E"/>
    <!-- Professional Hair -->
    <path d="M 140 160 C 140 95, 170 85, 200 85 C 230 85, 260 95, 260 160 C 260 130, 240 100, 200 100 C 160 100, 140 130, 140 160 Z" fill="#1E293B"/>
    <!-- Glasses / Loupe Magnifier indicator -->
    <rect x="160" y="148" width="32" height="22" rx="4" fill="none" stroke="url(#gold)" stroke-width="2.5"/>
    <rect x="208" y="148" width="32" height="22" rx="4" fill="none" stroke="url(#gold)" stroke-width="2.5"/>
    <line x1="192" y1="158" x2="208" y2="158" stroke="url(#gold)" stroke-width="2.5"/>
    <circle cx="176" cy="159" r="6" fill="none" stroke="#60A5FA" stroke-width="1.5" opacity="0.8"/>
    <circle cx="224" cy="159" r="6" fill="none" stroke="#60A5FA" stroke-width="1.5" opacity="0.8"/>
    <!-- Subtle smile & features -->
    <path d="M 188 198 Q 200 206 212 198" fill="none" stroke="#8D5B4C" stroke-width="2" stroke-linecap="round"/>
    
    <!-- Stethoscope or Dental Loupe Headlamp -->
    <circle cx="200" cy="100" r="12" fill="#0F172A" stroke="url(#gold)" stroke-width="2"/>
    <circle cx="200" cy="100" r="6" fill="#38BDF8"/>
    <!-- Lab coat lapels -->
    <path d="M 140 280 L 180 380 L 160 480" fill="none" stroke="#CBD5E1" stroke-width="2"/>
    <path d="M 260 280 L 220 380 L 240 480" fill="none" stroke="#CBD5E1" stroke-width="2"/>
    <!-- Doctor ID Badge -->
    <rect x="90" y="360" width="60" height="40" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>
    <line x1="98" y1="372" x2="135" y2="372" stroke="#0F2438" stroke-width="2.5"/>
    <line x1="98" y1="380" x2="125" y2="380" stroke="url(#gold)" stroke-width="2"/>
    <line x1="98" y1="388" x2="142" y2="388" stroke="#94A3B8" stroke-width="1.5"/>
  </g>

  <!-- Bottom Name Banner Overlay -->
  <rect x="20" y="390" width="360" height="74" rx="12" fill="#0B1B2B" fill-opacity="0.92" stroke="url(#gold)" stroke-width="1"/>
  <text x="40" y="420" font-family="'Playfair Display', Georgia, serif" font-size="19" font-weight="700" fill="#FFFFFF">{name}</text>
  <text x="40" y="440" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="11.5" font-weight="600" fill="#E2CA9E">{spec}</text>
  <text x="40" y="455" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="10" font-weight="500" fill="#94A3B8">{exp} Verified Clinical Experience</text>
</svg>"""

create_svg("dr-shreyas.svg", doctor_svg("Dr. H S Shreyas", "Microscopic Dentist & Endodontist", "11+ Years", "#162E47", "#0284C7"))
create_svg("dr-rohit.svg", doctor_svg("Dr. Rohit", "Consultant Orthodontist & Invisalign Specialist", "9+ Years", "#1E293B", "#6366F1"))
create_svg("dr-jithin.svg", doctor_svg("Dr. Jithin", "Consultant Periodontist & Implantologist", "10+ Years", "#0F2438", "#059669"))

# Treatment Cards Vector Artwork
treatments_art = [
    ("microscopic-rct.svg", "Microscopic Root Canal", "Precision Endodontics under 25x Magnification", "#0F2438"),
    ("cosmetic-dentistry.svg", "Cosmetic Dentistry", "Biomimetic Enamel Artistry & Veneering", "#162E47"),
    ("smile-makeover.svg", "Smile Makeovers", "3D Digital Full-Arch Aesthetic Transformation", "#1E293B"),
    ("dental-veneers.svg", "Veneers & Laminates", "Ultra-thin 0.3mm Porcelain Shells", "#0B1B2B"),
    ("dental-crowns.svg", "Crowns & Restorations", "Zirconia & E.max Monolithic Precision Caps", "#162E47"),
    ("braces-ortho.svg", "Braces & Orthodontics", "Damon Self-Ligating Ceramic & Metal Braces", "#0F2438"),
    ("invisalign.svg", "Invisalign Clear Aligners", "Virtually Invisible 3D SmartTrack Aligners", "#1E293B"),
    ("dental-implants.svg", "Dental Implants", "Titanium & Zirconia Permanent Root Replacements", "#0B1B2B"),
    ("laser-dentistry.svg", "Laser Dentistry", "Minimally Invasive Biolase Gum & Cavity Care", "#162E47"),
    ("pediatric-dentistry.svg", "Pediatric Dentistry", "Gentle, Fear-Free Dental Care for Children", "#0F2438"),
    ("scaling-polishing.svg", "Scaling & Polishing", "Ultrasonic Piezo Micro-Cleaning & Air-Polishing", "#1E293B"),
    ("digital-xrays.svg", "Digital Dental X-rays", "Ultra-Low Radiation RVG & HD Diagnostics", "#0B1B2B"),
    ("tooth-extraction.svg", "Tooth Extraction", "Atraumatic Tooth Removal Conserving Bone", "#162E47"),
    ("oral-surgery.svg", "Oral Surgery & Wisdom Teeth", "Piezosurgical Impacted Tooth Management", "#0F2438")
]

def treatment_card_svg(title: str, subtitle: str, bg_color: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}"/>
      <stop offset="100%" stop-color="#07111C"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F3EFE6"/>
      <stop offset="50%" stop-color="#C5A880"/>
      <stop offset="100%" stop-color="#8F6B38"/>
    </linearGradient>
    <radialGradient id="glow" cx="65%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#C5A880" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="600" height="400" fill="url(#bg)"/>
  <rect width="600" height="400" fill="url(#glow)"/>
  
  <!-- Modern medical geometric lines -->
  <g opacity="0.15" stroke="#FFFFFF" stroke-width="1">
    <circle cx="440" cy="180" r="160" fill="none" stroke="url(#gold)" stroke-width="1.5"/>
    <circle cx="440" cy="180" r="100" fill="none" stroke-dasharray="6 6"/>
    <line x1="260" y1="180" x2="580" y2="180"/>
    <line x1="440" y1="20" x2="440" y2="340"/>
  </g>

  <!-- Central Graphic Icon Feature -->
  <g transform="translate(380, 110)">
    <rect x="0" y="0" width="120" height="120" rx="24" fill="#0B1B2B" stroke="url(#gold)" stroke-width="2" opacity="0.9"/>
    <!-- Tooth emblem -->
    <path d="M 45 35 C 45 28, 52 26, 60 30 C 68 26, 75 28, 75 35 C 75 44, 72 54, 70 75 C 68 80, 64 81, 62 72 C 60 67, 60 67, 58 72 C 56 81, 52 80, 50 75 C 48 54, 45 44, 45 35 Z" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linejoin="round"/>
    <!-- Microscopic target lens -->
    <circle cx="60" cy="48" r="16" fill="none" stroke="url(#gold)" stroke-width="2.5"/>
    <circle cx="60" cy="48" r="5" fill="url(#gold)"/>
    <line x1="60" y1="26" x2="60" y2="34" stroke="url(#gold)" stroke-width="2"/>
    <line x1="60" y1="62" x2="60" y2="70" stroke="url(#gold)" stroke-width="2"/>
    <line x1="38" y1="48" x2="46" y2="48" stroke="url(#gold)" stroke-width="2"/>
    <line x1="74" y1="48" x2="82" y2="48" stroke="url(#gold)" stroke-width="2"/>
  </g>

  <!-- Left Info Overlay -->
  <g transform="translate(45, 75)">
    <rect x="-8" y="-8" width="160" height="26" rx="13" fill="#C5A880" fill-opacity="0.2" stroke="url(#gold)" stroke-width="1"/>
    <text x="8" y="10" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="10" font-weight="700" letter-spacing="1.5" fill="#E2CA9E">ENAMEL CLINICAL CARE</text>
    
    <text x="0" y="65" font-family="'Playfair Display', Georgia, serif" font-size="24" font-weight="700" fill="#FFFFFF">{title}</text>
    <text x="0" y="95" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="13" font-weight="400" fill="#CBD5E1">{subtitle}</text>
    
    <g transform="translate(0, 135)">
      <circle cx="10" cy="10" r="9" fill="#C5A880" fill-opacity="0.2"/>
      <text x="6" y="14" font-family="system-ui" font-size="11" fill="#E2CA9E">✓</text>
      <text x="28" y="14" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="12.5" font-weight="500" fill="#F1F5F9">Microscopic Precision Protocol</text>
      
      <circle cx="10" cy="38" r="9" fill="#C5A880" fill-opacity="0.2"/>
      <text x="6" y="42" font-family="system-ui" font-size="11" fill="#E2CA9E">✓</text>
      <text x="28" y="42" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="12.5" font-weight="500" fill="#F1F5F9">Specialist-Led Examination</text>
      
      <circle cx="10" cy="66" r="9" fill="#C5A880" fill-opacity="0.2"/>
      <text x="6" y="70" font-family="system-ui" font-size="11" fill="#E2CA9E">✓</text>
      <text x="28" y="70" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="12.5" font-weight="500" fill="#F1F5F9">Strict International Sterilisation</text>
    </g>
  </g>
</svg>"""

for fname, title, sub, bg in treatments_art:
    create_svg(fname, treatment_card_svg(title, sub, bg))

# 3. HERO MICROSCOPE BANNER SVG
hero_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 650" width="1200" height="650">
  <defs>
    <linearGradient id="heroBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B1B2B"/>
      <stop offset="50%" stop-color="#0F2438"/>
      <stop offset="100%" stop-color="#050C14"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FBF7EE"/>
      <stop offset="50%" stop-color="#C5A880"/>
      <stop offset="100%" stop-color="#8C652E"/>
    </linearGradient>
    <radialGradient id="beam" cx="70%" cy="35%" r="50%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.25"/>
      <stop offset="50%" stop-color="#C5A880" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="650" fill="url(#heroBg)"/>
  <rect width="1200" height="650" fill="url(#beam)"/>
  
  <!-- Optical Grid & Scale lines -->
  <g opacity="0.12" stroke="#FFFFFF" stroke-width="1">
    <line x1="0" y1="150" x2="1200" y2="150"/>
    <line x1="0" y1="300" x2="1200" y2="300"/>
    <line x1="0" y1="450" x2="1200" y2="450"/>
    <line x1="300" y1="0" x2="300" y2="650"/>
    <line x1="600" y1="0" x2="600" y2="650"/>
    <line x1="900" y1="0" x2="900" y2="650"/>
    <circle cx="850" cy="300" r="220" fill="none" stroke="url(#gold)" stroke-width="2"/>
    <circle cx="850" cy="300" r="160" fill="none" stroke-dasharray="8 8"/>
    <circle cx="850" cy="300" r="100" fill="none"/>
  </g>

  <!-- Surgical Operating Microscope Representation -->
  <g transform="translate(680, 80)">
    <!-- Articulated Suspension Arm -->
    <path d="M 400 -50 L 300 100 L 220 180" fill="none" stroke="#64748B" stroke-width="18" stroke-linecap="round"/>
    <circle cx="300" cy="100" r="20" fill="#0F172A" stroke="url(#gold)" stroke-width="4"/>
    <circle cx="220" cy="180" r="24" fill="#0F172A" stroke="url(#gold)" stroke-width="4"/>

    <!-- Microscope Body / Optics Optical Carrier -->
    <rect x="150" y="180" width="140" height="90" rx="16" fill="#1E293B" stroke="url(#gold)" stroke-width="2.5"/>
    <text x="170" y="235" font-family="system-ui" font-size="15" font-weight="700" letter-spacing="3" fill="#E2CA9E">ZEISS 25X</text>
    
    <!-- Dual Binocular Eyepieces -->
    <path d="M 120 160 L 160 190" stroke="#475569" stroke-width="14" stroke-linecap="round"/>
    <path d="M 140 130 L 180 180" stroke="#475569" stroke-width="14" stroke-linecap="round"/>
    <ellipse cx="115" cy="155" rx="12" ry="16" fill="#020617" stroke="url(#gold)" stroke-width="3"/>
    <ellipse cx="135" cy="125" rx="12" ry="16" fill="#020617" stroke="url(#gold)" stroke-width="3"/>
    <circle cx="115" cy="155" r="5" fill="#38BDF8"/>
    <circle cx="135" cy="125" r="5" fill="#38BDF8"/>

    <!-- Objective Lens Turret & LED Coaxial Illuminator -->
    <polygon points="180,270 260,270 240,330 200,330" fill="#0F172A" stroke="#94A3B8" stroke-width="2"/>
    <ellipse cx="220" cy="330" rx="20" ry="8" fill="#38BDF8" stroke="url(#gold)" stroke-width="2.5"/>
    
    <!-- Focus knobs -->
    <circle cx="150" cy="225" r="14" fill="#C5A880" stroke="#0F172A" stroke-width="3"/>
    <circle cx="290" cy="225" r="14" fill="#C5A880" stroke="#0F172A" stroke-width="3"/>

    <!-- High-intensity Coaxial Light Cone targeting tooth -->
    <polygon points="205,335 235,335 290,490 150,490" fill="url(#beam)" opacity="0.8"/>

    <!-- Target Tooth under Operating Illumination -->
    <g transform="translate(190, 460)">
      <ellipse cx="30" cy="25" rx="35" ry="12" fill="#000000" opacity="0.4"/>
      <!-- Tooth body -->
      <path d="M 10 0 C 10 -15, 20 -20, 30 -15 C 40 -20, 50 -15, 50 0 C 50 15, 45 28, 42 45 C 40 50, 35 50, 32 40 C 30 35, 30 35, 28 40 C 25 50, 20 50, 18 45 C 15 28, 10 15, 10 0 Z" fill="#F8FAFC" stroke="url(#gold)" stroke-width="2.5"/>
      <!-- Glowing pulp chamber -->
      <path d="M 24 10 Q 30 14 36 10 L 33 30 Q 30 32 27 30 Z" fill="#E2CA9E" opacity="0.9"/>
      <!-- Microscopic reticle indicator overlay -->
      <circle cx="30" cy="8" r="18" fill="none" stroke="#38BDF8" stroke-width="1.5" stroke-dasharray="3 3"/>
      <line x1="12" y1="8" x2="48" y2="8" stroke="#38BDF8" stroke-width="1"/>
      <line x1="30" y1="-10" x2="30" y2="26" stroke="#38BDF8" stroke-width="1"/>
    </g>
  </g>

  <!-- Left Technical Overlay Metrics -->
  <g transform="translate(60, 460)">
    <rect x="0" y="0" width="460" height="130" rx="16" fill="#0B1B2B" fill-opacity="0.85" stroke="url(#gold)" stroke-width="1.2"/>
    <g transform="translate(30, 30)">
      <text x="0" y="24" font-family="'Playfair Display', Georgia, serif" font-size="32" font-weight="700" fill="#E2CA9E">25x</text>
      <text x="0" y="44" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="11" font-weight="600" fill="#94A3B8">SURGICAL MAGNIFICATION</text>
      
      <line x1="140" y1="5" x2="140" y2="55" stroke="#334155" stroke-width="1.5"/>

      <text x="170" y="24" font-family="'Playfair Display', Georgia, serif" font-size="32" font-weight="700" fill="#E2CA9E">100%</text>
      <text x="170" y="44" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="11" font-weight="600" fill="#94A3B8">STERILITY PROTOCOL</text>

      <line x1="300" y1="5" x2="300" y2="55" stroke="#334155" stroke-width="1.5"/>

      <text x="330" y="24" font-family="'Playfair Display', Georgia, serif" font-size="32" font-weight="700" fill="#E2CA9E">30+</text>
      <text x="330" y="44" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="11" font-weight="600" fill="#94A3B8">YRS COMBINED EXP</text>
    </g>
  </g>
</svg>"""
create_svg("hero-microscope.svg", hero_svg)

# 4. GALLERY IMAGES
gallery_items = [
    ("gallery-clinic-interior.svg", "Clinic Interior", "Spacious, soothing lounge designed for patient comfort", "#0B1B2B"),
    ("gallery-tech-microscope.svg", "Dental Operating Microscope", "Surgical magnification revealing micro-anatomy up to 25x", "#0F2438"),
    ("gallery-operatory.svg", "Advanced Operatory", "Ergonomic dental suite with ceiling relaxation displays", "#162E47"),
    ("gallery-sterilization.svg", "Sterilisation Suite", "Class-B autoclave and strict 5-stage bio-decontamination", "#1E293B"),
    ("gallery-digital-imaging.svg", "Digital 3D Diagnostics", "Ultra-low radiation imaging for exact treatment planning", "#0B1B2B"),
    ("gallery-smile-transformation.svg", "Aesthetic Transformation", "Natural smile harmony achieved through conservative ceramic bonding", "#0F2438")
]

for fname, title, desc, bg in gallery_items:
    create_svg(fname, treatment_card_svg(title, desc, bg))

print("All image assets created successfully!")
