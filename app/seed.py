import hashlib
import os
import json
from .database import get_db_connection, init_db

def hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return pw_hash.hex(), salt.hex()

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if doctors exist
    if cursor.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
        doctors_data = [
            (
                "dr-h-s-shreyas",
                "Dr. H S Shreyas",
                "Chief Microscopic Dentist | Root Canal & Restorative Specialist",
                "BDS (JSS Dental College & Hospital, Mysuru) • Style Italiano Trained • Member, Microscopic Dental Club",
                11,
                "Microscopic Endodontics, Biomimetic Restorative Dentistry, Aesthetic Smile Design",
                "Dr. H S Shreyas is a pioneering microscopic dentist in Mysuru dedicated to saving natural teeth through high-magnification dentistry. Utilizing surgical operating microscopes with up to 25x magnification, he achieves unprecedented precision in root canal therapy, conservative tooth preparations, and composite artistry. His practice philosophy centers on bio-mimetic preservation, patient comfort, and zero guesswork.",
                "/static/images/dr-shreyas.jpg",
                1
            ),
            (
                "dr-rohit",
                "Dr. Rohit",
                "Consultant Orthodontist | Certified Invisalign Specialist",
                "BDS, MDS (Orthodontics & Dentofacial Orthopedics) • Certified Invisalign Provider",
                9,
                "Invisalign Clear Aligners, Self-Ligating Braces, Dentofacial Orthopedics, Adult Orthodontics",
                "Dr. Rohit specializes in comprehensive orthodontic correction for adolescents and adults. As an experienced Invisalign specialist, he combines 3D digital treatment planning with gentle, aesthetic tooth movement to correct misalignments, crowding, and bite irregularities with minimal visual intrusion and optimal comfort.",
                "/static/images/dr-rohit.jpg",
                1
            ),
            (
                "dr-jithin",
                "Dr. Jithin",
                "Consultant Periodontist | Dental Implant Specialist",
                "BDS, MDS (Periodontics & Oral Implantology) • Advanced Piezosurgery Fellow",
                10,
                "Dental Implants, Bone Grafting, Periodontal Plastic Surgery, Laser Gum Therapy",
                "Dr. Jithin leads the implantology and periodontal division at Enamel. With extensive expertise in surgical precision and hard/soft tissue management, he delivers long-lasting dental implant restorations and advanced gum therapies designed to restore both foundation and function seamlessly.",
                "/static/images/dr-jithin.jpg",
                1
            )
        ]
        cursor.executemany("""
        INSERT INTO doctors (slug, name, title, qualifications, experience_years, specialization, bio, photo_url, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, doctors_data)
        conn.commit()

    # Fetch doctor IDs
    doc_ids = {row["slug"]: row["id"] for row in cursor.execute("SELECT id, slug FROM doctors").fetchall()}

    # Check if treatments exist
    if cursor.execute("SELECT COUNT(*) FROM treatments").fetchone()[0] == 0:
        treatments_data = [
            {
                "slug": "microscopic-root-canal",
                "name": "Microscopic Root Canal Treatment",
                "category": "Endodontics",
                "short_description": "Advanced root canal therapy performed under surgical operating microscopes with up to 25x magnification for unparalleled precision and tooth preservation.",
                "full_description": "Root canal treatment at Enamel Microscopic Dentistry represents the pinnacle of modern endodontics. By employing high-powered surgical operating microscopes and coaxial shadowless LED illumination, our specialists visualize microscopic anatomy, locate hidden accessory canals, and treat complex root curves that are impossible to discern with the naked eye. This biomimetic approach ensures thorough disinfection while conserving maximum natural tooth structure.",
                "involves": json.dumps([
                    "High-magnification visualization (up to 25x) under a surgical dental microscope",
                    "Complete isolation using dental dam for absolute sterility and patient airway protection",
                    "Digital apex locator measurement for micrometer canal accuracy",
                    "Rotary titanium instrumentation and sonic canal irrigation",
                    "Three-dimensional warm gutta-percha obturation for hermetic apical sealing"
                ]),
                "benefits": json.dumps([
                    "Significantly higher success rate compared to conventional unmagnified treatments",
                    "Preservation of healthy peri-cervical dentin, reducing post-treatment fracture risks",
                    "Detection of micro-cracks, missed canals, and anatomical variations",
                    "Minimally invasive access cavities ensuring tooth longevity",
                    "Gentle, virtually comfortable procedure with computerized local anesthesia techniques"
                ]),
                "candidates": json.dumps([
                    "Patients experiencing persistent toothache, sensitivity to hot/cold, or swelling",
                    "Deep dental decay that has reached the internal dental pulp",
                    "Teeth with cracked tooth syndrome or traumatic dental injuries",
                    "Failed previous root canal treatments requiring microscopic retreatment"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Comprehensive Examination & 3D Imaging", "desc": "Detailed clinical evaluation, vitality testing, and digital radiography to map the root morphology."},
                    {"step": 2, "title": "Sterile Isolation & Micro-Access", "desc": "Rubber dam application and ultra-conservative access preparation guided under the operating microscope."},
                    {"step": 3, "title": "Microscopic Canal Debridement", "desc": "Locating all main and accessory canals, thorough biological cleaning, and ultrasonic irrigation."},
                    {"step": 4, "title": "3D Hermetic Sealing & Restoration", "desc": "Bio-ceramic sealing and immediate adhesive coronal seal to safeguard against reinfection."}
                ]),
                "faqs": json.dumps([
                    {"q": "How does microscopic root canal differ from traditional treatment?", "a": "A conventional root canal relies primarily on tactile feel and basic vision. The dental microscope magnifies the internal tooth structure up to 25 times and illuminates fine canal branches, ensuring complete disinfection and minimal removal of healthy tooth structure."},
                    {"q": "Is the treatment painful?", "a": "Modern microscopic endodontics is performed under profound, gentle local anesthesia. Most patients report feeling entirely comfortable during the procedure and can even relax or watch shows on our ceiling screens."},
                    {"q": "How many appointments are required?", "a": "Most straightforward cases can be completed in a single meticulous appointment of 60–90 minutes. Complex infections or retreatments may require two appointments with intermediate antibacterial medication."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 60,
                "consultation_fee": 600,
                "image_url": "/static/images/microscopic-rct.jpg"
            },
            {
                "slug": "cosmetic-dentistry",
                "name": "Cosmetic Dentistry",
                "category": "Aesthetics",
                "short_description": "Customized aesthetic dental enhancements blending art, science, and facial harmony for radiant, natural smiles.",
                "full_description": "Our cosmetic dentistry approach focuses on creating naturally beautiful smiles that enhance facial harmony rather than artificial-looking perfection. We employ biomimetic materials, shade analysis under standardized daylight conditions, and ultra-conservative techniques that respect your natural enamel.",
                "involves": json.dumps([
                    "Digital photographic smile analysis and facial symmetry evaluation",
                    "Direct composite resin bonding and artistic tooth contouring",
                    "Enamel micro-abrasion and stain removal",
                    "Professional in-office laser teeth whitening",
                    "Porcelain aesthetic enhancements and tooth reshaping"
                ]),
                "benefits": json.dumps([
                    "Correction of chips, gaps, discolouration, and irregular tooth lengths",
                    "Subtle, natural-looking results tailored to your facial features",
                    "Minimally invasive techniques requiring little to no tooth structure removal",
                    "Immediate enhancement in smile confidence and personal aesthetics"
                ]),
                "candidates": json.dumps([
                    "Individuals with discoloured, chipped, worn, or slightly spaced front teeth",
                    "Patients preparing for milestone life events (weddings, public speaking, career steps)",
                    "Anyone seeking to rejuvenate the youthfulness of their natural smile"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Aesthetic Consultation & Photography", "desc": "High-resolution portrait photography and discussion of your aesthetic goals."},
                    {"step": 2, "title": "Digital Smile Simulation", "desc": "Previewing anticipated smile changes digitally and through physical mock-ups."},
                    {"step": 3, "title": "Aesthetic Treatment Delivery", "desc": "Artistic bonding, whitening, or restorative placement under optimal illumination."},
                    {"step": 4, "title": "Finishing & Polish", "desc": "Multi-step microscopic polishing ensuring high-gloss lustre and stain resistance."}
                ]),
                "faqs": json.dumps([
                    {"q": "Will cosmetic dentistry look unnatural or too white?", "a": "Never. Our philosophy is natural aesthetics. We match translucency, surface texture, and optical hue to blend imperceptibly with your natural teeth."},
                    {"q": "How long does cosmetic bonding last?", "a": "With proper oral hygiene and regular dental checkups, high-end composite bonding typically lasts 5 to 8 years before requiring minor repolishing."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 45,
                "consultation_fee": 500,
                "image_url": "/static/images/cosmetic-dentistry.jpg"
            },
            {
                "slug": "smile-makeovers",
                "name": "Smile Makeovers",
                "category": "Aesthetics",
                "short_description": "Comprehensive full-arch aesthetic and functional smile transformations planned with precision digital protocols.",
                "full_description": "A smile makeover at Enamel Microscopic Dentistry is a customized, multi-disciplinary treatment plan that addresses multiple dental concerns simultaneously. We harmonize tooth proportions, gum contours, lip dynamics, and bite alignment to create a balanced smile that looks effortless and revitalizes your entire facial profile.",
                "involves": json.dumps([
                    "3D intraoral digital scanning and photographic smile design",
                    "Diagnostic wax-up and physical smile test-drive in your mouth",
                    "Combined veneers, crowns, alignment, and laser gum contouring",
                    "Functional occlusal balancing to ensure long-term mechanical stability"
                ]),
                "benefits": json.dumps([
                    "Holistic resolution of aesthetic imperfections, worn bites, and tooth asymmetry",
                    "Ability to preview and approve your new smile before any irreversible work begins",
                    "Dramatically revitalized youthful facial aesthetics",
                    "Long-term functional stability and ease of chewing"
                ]),
                "candidates": json.dumps([
                    "Patients with multiple aesthetic concerns: severe wear, uneven spacing, discolouration, or old restorations",
                    "Individuals with collapsed bites or asymmetrical smile lines",
                    "Patients seeking a unified, harmonious dental transformation"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Comprehensive Smile Analysis", "desc": "3D facial photos, intraoral scans, and dynamic video smile recording."},
                    {"step": 2, "title": "The 'Test Drive' Mock-Up", "desc": "Direct trial of temporary aesthetic shells in your mouth to evaluate speech and aesthetics."},
                    {"step": 3, "title": "Micro-Precision Tooth Preparation", "desc": "Microscope-guided enamel shaping conserving maximal natural tooth structure."},
                    {"step": 4, "title": "Final Ceramic Bonding", "desc": "Adhesive cementation under dental dam isolation for supreme bond strength."}
                ]),
                "faqs": json.dumps([
                    {"q": "Can I see what my smile will look like before starting?", "a": "Yes! We create a physical intraoral mock-up that you can wear in your mouth, look in the mirror, and review before any tooth preparation begins."},
                    {"q": "How long does a smile makeover take?", "a": "Typically 2 to 3 visits across 2–3 weeks, depending on whether orthodontic pre-alignment or laser gum contouring is required."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 60,
                "consultation_fee": 700,
                "image_url": "/static/images/smile-makeover.jpg"
            },
            {
                "slug": "dental-veneers-and-laminates",
                "name": "Dental Veneers and Laminates",
                "category": "Aesthetics",
                "short_description": "Ultra-thin, custom-crafted lithium disilicate ceramic veneers bonded with microscopic precision to transform front teeth.",
                "full_description": "Dental veneers are custom-engineered wafer-thin porcelain shells designed to cover the front surface of teeth. Under the operating microscope, our preparations are ultra-conservative—often requiring only 0.3mm to 0.5mm of enamel reduction, and in select cases, no preparation at all. We utilize premium glass-ceramics (E.max and feldspathic porcelain) to replicate the natural light transmission of real tooth enamel.",
                "involves": json.dumps([
                    "Microscope-controlled micro-depth tooth preparation (0.3mm - 0.5mm)",
                    "Digital intraoral impression mapping with sub-millimeter accuracy",
                    "Individually hand-layered aesthetic porcelain laminates",
                    "Adhesive bonding with light-cured resin cements under rubber dam"
                ]),
                "benefits": json.dumps([
                    "Highly stain-resistant surface that retains gloss and colour permanently",
                    "Natural translucency mimicking genuine human tooth enamel",
                    "Exceptional bond strength to native enamel for outstanding longevity",
                    "Closes stubborn diastemas (gaps) and corrects intrinsic antibiotic staining"
                ]),
                "candidates": json.dumps([
                    "Teeth with severe intrinsic staining (tetracycline or fluorosis) unresponsive to bleaching",
                    "Teeth that are chipped, uneven, worn, or irregularly shaped",
                    "Patients wanting to close gaps between teeth without lengthy orthodontics"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Design & Shade Consultation", "desc": "Evaluating facial characteristics and selecting exact porcelain shade and optical opacity."},
                    {"step": 2, "title": "Microscopic Enamel Preparation", "desc": "Minimal shaping within enamel followed by high-precision digital scanning."},
                    {"step": 3, "title": "Artisan Ceramic Fabrication", "desc": "Master laboratory crafting of individual ceramic laminates."},
                    {"step": 4, "title": "Microscopic Bonding", "desc": "Permanent adhesive bonding under rubber dam isolation."}
                ]),
                "faqs": json.dumps([
                    {"q": "Do veneers ruin your natural teeth?", "a": "Not with microscopic dentistry. Because we work under 10x-20x magnification, we remove only the bare minimum of outer enamel, preserving the structural integrity of your tooth."},
                    {"q": "How long do porcelain veneers last?", "a": "Clinical studies show porcelain veneers have a 95%+ survival rate over 10 to 15 years when bonded strictly to enamel and properly maintained."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 60,
                "consultation_fee": 600,
                "image_url": "/static/images/dental-veneers.jpg"
            },
            {
                "slug": "dental-crowns-and-restorations",
                "name": "Dental Crowns and Restorations",
                "category": "Restorative",
                "short_description": "Biomimetic onlays, inlays, and metal-free zirconia/ceramic crowns engineered for strength, fit, and natural beauty.",
                "full_description": "When a tooth has suffered significant damage from decay, trauma, or a previous large restoration, a precision dental crown or partial overlay restores structural integrity. At Enamel, we prioritize biomimetic partial restorations (onlays and endocrowns) over aggressive traditional crown preparations whenever possible, preserving maximum healthy tooth structure.",
                "involves": json.dumps([
                    "Microscopic removal of defective restorations and recurrent decay",
                    "Biomimetic immediate dentin sealing (IDS) to eliminate post-op sensitivity",
                    "Computer-aided CAD/CAM milling of high-strength zirconia or lithium disilicate",
                    "Micro-gap marginal verification under the surgical microscope"
                ]),
                "benefits": json.dumps([
                    "Restores full chewing capacity and structural strength to fractured teeth",
                    "100% metal-free biocompatible materials with zero grey lines at gum margins",
                    "Precise marginal fit that prevents bacterial leakage and secondary decay",
                    "Seamless color and texture match to adjacent natural teeth"
                ]),
                "candidates": json.dumps([
                    "Teeth following root canal treatment requiring protective coverage",
                    "Teeth with large fractured fillings or compromised cusps",
                    "Severely worn down teeth requiring occlusal rehabilitation"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Tooth Preparation & Core Foundation", "desc": "Removing old restorative material and reinforcing core structure."},
                    {"step": 2, "title": "Digital Impression & Temporary Crown", "desc": "Capturing 3D optical scan and placing an aesthetic temporary restoration."},
                    {"step": 3, "title": "Precision CAD/CAM Milling", "desc": "Fabricating high-strength crown with exact micron margin fit."},
                    {"step": 4, "title": "Microscopic Verification & Cementation", "desc": "Checking fit under magnification and permanently bonding."}
                ]),
                "faqs": json.dumps([
                    {"q": "Why metal-free ceramic or zirconia?", "a": "Metal-free restorations offer supreme biocompatibility, eliminate grey discoloration around gums, and reflect light exactly like natural teeth."},
                    {"q": "Is a crown always necessary after a root canal?", "a": "For posterior back teeth that endure heavy biting forces, a crown or onlay is crucial to prevent tooth fracture. For front teeth, a conservative composite restoration is often sufficient if enough tooth structure remains."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 45,
                "consultation_fee": 500,
                "image_url": "/static/images/dental-crowns.jpg"
            },
            {
                "slug": "braces-and-orthodontics",
                "name": "Braces and Orthodontics",
                "category": "Orthodontics",
                "short_description": "Advanced fixed orthodontic solutions including self-ligating ceramic and metallic braces for patients of all ages.",
                "full_description": "Orthodontic treatment at Enamel goes beyond straightening teeth—it optimizes facial harmony, airway function, and jaw joint health. Dr. Rohit utilizes modern low-friction self-ligating brackets and customized archwires to deliver efficient tooth movement with gentle forces, minimizing treatment time and appointments.",
                "involves": json.dumps([
                    "Comprehensive cephalometric and digital photographic analysis",
                    "Low-profile ceramic (tooth-coloured) or precision metallic brackets",
                    "Advanced nickel-titanium shape memory archwires",
                    "Inter-arch functional correction and bite alignment mechanics"
                ]),
                "benefits": json.dumps([
                    "Straightens crowded, crooked, or rotated teeth",
                    "Corrects overbites, underbites, crossbites, and open bites",
                    "Improves oral hygiene accessibility, reducing long-term gum disease risk",
                    "Enhances facial aesthetics and lip support"
                ]),
                "candidates": json.dumps([
                    "Adolescents and adults seeking permanent correction of malaligned teeth",
                    "Patients with difficult bite problems requiring complex torque control",
                    "Individuals preparing for restorative or implant work needing tooth uprighting"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Orthodontic Assessment & Records", "desc": "Comprehensive clinical exam, lateral cephalogram, and digital study models."},
                    {"step": 2, "title": "Treatment Plan Discussion", "desc": "Reviewing treatment timeline, bracket choices, and tooth movement trajectory."},
                    {"step": 3, "title": "Direct Bonding Placement", "desc": "Careful placement of orthodontic brackets with precision positioning."},
                    {"step": 4, "title": "Periodic Adjustments & Retention", "desc": "Routine adjustments every 4–6 weeks followed by custom retainers upon completion."}
                ]),
                "faqs": json.dumps([
                    {"q": "Can adults get braces?", "a": "Absolutely. Approximately 35% of our orthodontic patients are adults. Healthy teeth can be moved at virtually any age with excellent results."},
                    {"q": "How long will orthodontic treatment take?", "a": "Average treatment times range from 12 to 18 months, depending on the severity of the malocclusion and patient compliance."}
                ]),
                "default_doctor_id": doc_ids.get("dr-rohit"),
                "duration_minutes": 45,
                "consultation_fee": 500,
                "image_url": "/static/images/braces-orthodontics.jpg"
            },
            {
                "slug": "invisalign",
                "name": "Invisalign Clear Aligners",
                "category": "Orthodontics",
                "short_description": "Discreet, removable clear aligner orthodontic therapy planned with 3D digital simulation for lifestyle comfort.",
                "full_description": "Invisalign represents the modern gold standard in aesthetic orthodontic care. As a certified Invisalign provider, Dr. Rohit utilizes proprietary ClinCheck 3D software to plan the precise movement of every individual tooth from the very first aligner to the final smile. Clear, removable, and custom-molded, Invisalign fits seamlessly into professional and social lifestyles.",
                "involves": json.dumps([
                    "High-resolution 3D intraoral digital scan (no messy impression trays)",
                    "ClinCheck 3D digital treatment plan showing stage-by-stage movement",
                    "Custom series of SmartTrack medical-grade polyurethane aligners",
                    "Discreet aesthetic SmartForce attachments for precise torque control"
                ]),
                "benefits": json.dumps([
                    "Nearly invisible in normal conversation and photos",
                    "Completely removable for meals, brushing, flossing, and special occasions",
                    "No metal wires or sharp brackets to irritate lips and cheeks",
                    "Fewer emergency visits and predictable digital milestones"
                ]),
                "candidates": json.dumps([
                    "Working professionals, students, and adults desiring subtle tooth straightening",
                    "Mild to severe crowding, spacing, deep bites, or relapsed orthodontic cases",
                    "Patients who want to maintain optimal hygiene without dietary restrictions"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "3D Digital Scan & Smile Simulation", "desc": "Digitizing your teeth in 5 minutes with our intraoral scanner and previewing your projected smile."},
                    {"step": 2, "title": "Custom ClinCheck Plan", "desc": "Dr. Rohit meticulously calculates each tooth movement cycle."},
                    {"step": 3, "title": "Aligner Delivery & Guidance", "desc": "Fitting your first sets of aligners and guiding wear routines (20–22 hours daily)."},
                    {"step": 4, "title": "Milestone Monitoring & Retainers", "desc": "Periodic progress checks every 6–8 weeks and Vivera retainers to preserve your result."}
                ]),
                "faqs": json.dumps([
                    {"q": "How many hours a day do I need to wear Invisalign?", "a": "For predictable results, aligners should be worn 20 to 22 hours per day, removing them only for meals, drinking hot beverages, and brushing."},
                    {"q": "Does Invisalign hurt?", "a": "Most patients feel gentle pressure for the first 24–48 hours of starting a new aligner set, which is a sign that teeth are moving safely."}
                ]),
                "default_doctor_id": doc_ids.get("dr-rohit"),
                "duration_minutes": 45,
                "consultation_fee": 600,
                "image_url": "/static/images/invisalign.jpg"
            },
            {
                "slug": "dental-implants",
                "name": "Dental Implants",
                "category": "Implantology",
                "short_description": "Permanent titanium and ceramic tooth replacements that restore natural biting strength, bone health, and aesthetic confidence.",
                "full_description": "Dental implants are the premier solution for replacing missing teeth. Functioning as artificial tooth roots, high-grade biocompatible titanium fixtures integrate naturally with your jawbone (osseointegration), preventing bone resorption and supporting lifelike ceramic crowns without compromising adjacent teeth.",
                "involves": json.dumps([
                    "High-resolution 3D CBCT bone density mapping",
                    "Computer-guided digital implant planning and surgical stents",
                    "Medical-grade titanium or zirconia implant fixtures",
                    "Custom screw-retained ceramic crowns with natural emergence profiles"
                ]),
                "benefits": json.dumps([
                    "Permanent tooth replacement with 98%+ long-term success rates",
                    "Preserves surrounding jawbone and facial structure from shrinkage",
                    "Zero damage or shaving required on neighbouring natural teeth",
                    "Restores 100% natural chewing force and dietary freedom"
                ]),
                "candidates": json.dumps([
                    "Patients with single or multiple missing teeth",
                    "Individuals struggling with loose or uncomfortable removable dentures",
                    "Patients requiring extraction of unrestorable teeth"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "3D CBCT Evaluation", "desc": "Evaluating bone volume, nerve pathways, and sinus positions with 3D radiography."},
                    {"step": 2, "title": "Guided Implant Placement", "desc": "Gentle, computer-guided placement under sterile surgical protocol."},
                    {"step": 3, "title": "Osseointegration Healing", "desc": "Biological integration period of 8–12 weeks ensuring solid bone foundation."},
                    {"step": 4, "title": "Custom Crown Attachment", "desc": "Fixing the custom porcelain crown with exact gingival contouring."}
                ]),
                "faqs": json.dumps([
                    {"q": "How long do dental implants last?", "a": "With good oral hygiene and routine maintenance, dental implants are engineered to last a lifetime."},
                    {"q": "Is dental implant surgery painful?", "a": "The procedure is done under profound local anesthesia. Most patients report that having an implant placed causes less discomfort than having a tooth extracted."}
                ]),
                "default_doctor_id": doc_ids.get("dr-jithin"),
                "duration_minutes": 60,
                "consultation_fee": 700,
                "image_url": "/static/images/dental-implants.jpg"
            },
            {
                "slug": "laser-dentistry",
                "name": "Laser Dentistry",
                "category": "General",
                "short_description": "Minimally invasive soft-tissue laser treatments for aesthetic gum recontouring, pocket disinfection, and rapid healing.",
                "full_description": "Laser dentistry harnesses concentrated light energy to perform soft-tissue treatments with exceptional precision, virtually no bleeding, and minimal postoperative discomfort. We utilize specialized dental lasers for cosmetic gum depigmentation, crown lengthening, frenectomy, and deep periodontal pocket decontamination.",
                "involves": json.dumps([
                    "Targeted diode laser energy for soft-tissue sculpting",
                    "Laser gum depigmentation to eliminate dark melanin spots",
                    "Subgingival laser bacterial decontamination in periodontal pockets",
                    "Minimally invasive frenectomy and aphthous ulcer biostimulation"
                ]),
                "benefits": json.dumps([
                    "Virtually bloodless procedures due to instant coagulation",
                    "Significantly reduced need for traditional surgical sutures",
                    "Decreased postoperative swelling and accelerated tissue regeneration",
                    "Sterilizes the operative field, minimizing bacterial infection risks"
                ]),
                "candidates": json.dumps([
                    "Patients with 'gummy smiles' seeking symmetrical gum line reshaping",
                    "Individuals with dark or patchy gum pigmentation wanting pink, healthy gums",
                    "Patients with chronic gum disease requiring deep bacterial sterilization"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Periodontal & Aesthetic Assessment", "desc": "Evaluating biological width, gum health, and smile symmetry."},
                    {"step": 2, "title": "Laser Calibration", "desc": "Customizing laser wavelength and power settings for specific tissue requirements."},
                    {"step": 3, "title": "Gentle Laser Procedure", "desc": "Pinpoint ablation and biostimulation with topical or mild local numbing."},
                    {"step": 4, "title": "Post-Care Review", "desc": "Rapid healing checkup within 7–10 days with minimal dietary restrictions."}
                ]),
                "faqs": json.dumps([
                    {"q": "Is laser dentistry safe?", "a": "Yes, dental lasers are clinically proven and FDA-approved. Both patient and clinician wear protective optical eyewear during treatment."},
                    {"q": "How quickly do gums heal after laser contouring?", "a": "Because the laser seals blood vessels and nerve endings instantly, most patients heal within 3 to 5 days with very little soreness."}
                ]),
                "default_doctor_id": doc_ids.get("dr-jithin"),
                "duration_minutes": 30,
                "consultation_fee": 500,
                "image_url": "/static/images/laser-dentistry.jpg"
            },
            {
                "slug": "pediatric-dentistry",
                "name": "Pediatric Dentistry",
                "category": "General",
                "short_description": "Gentle, stress-free preventative and therapeutic dental care tailored specifically for children and young teens.",
                "full_description": "We believe early dental experiences shape a child's relationship with oral health for life. Our clinic provides a welcoming, calm environment designed to alleviate anxiety. We prioritize preventative measures—such as dental sealants, fluoride therapy, and dietary counseling—alongside gentle restorative care for primary teeth.",
                "involves": json.dumps([
                    "Gentle pediatric checkups and developmental bite evaluations",
                    "Preventative pit-and-fissure sealants and fluoride varnishes",
                    "Conservative restorations for childhood dental caries",
                    "Space maintainers for prematurely lost baby teeth",
                    "Child-friendly oral hygiene instruction and habit counseling"
                ]),
                "benefits": json.dumps([
                    "Builds positive, fear-free attitudes towards dental health early in life",
                    "Prevents painful childhood toothaches and premature primary tooth loss",
                    "Guides proper eruption and alignment of permanent teeth",
                    "Empowers parents with science-based homecare and nutrition guidance"
                ]),
                "candidates": json.dumps([
                    "Infants reaching their first birthday or with their first erupted tooth",
                    "Children and teens needing routine cavity screening and cleanings",
                    "Children with dental habits like thumb sucking, mouth breathing, or tooth grinding"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Warm Welcome & Acclimatization", "desc": "Familiarizing the child with the clinic environment and friendly team."},
                    {"step": 2, "title": "Gentle Examination", "desc": "Checking developing teeth, gums, and bite alignment with child-friendly terminology."},
                    {"step": 3, "title": "Preventative Care", "desc": "Gentle cleaning, protective fluoride application, or protective sealants."},
                    {"step": 4, "title": "Praise & Home Care Coaching", "desc": "Positive reinforcement, rewards, and fun home brushing guidance."}
                ]),
                "faqs": json.dumps([
                    {"q": "At what age should my child first visit the dentist?", "a": "Dental associations recommend scheduling the first visit within six months of the first tooth appearing, or by the child's first birthday."},
                    {"q": "Why do baby teeth matter if they will fall out anyway?", "a": "Baby teeth hold vital space for permanent teeth, aid in speech development, and allow proper nutrition. Neglected cavities can cause severe pain and damage underlying permanent tooth buds."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 30,
                "consultation_fee": 400,
                "image_url": "/static/images/pediatric-dentistry.jpg"
            },
            {
                "slug": "scaling-and-polishing",
                "name": "Scaling and Polishing (Dental Cleaning)",
                "category": "General",
                "short_description": "Ultrasonic plaque and calculus removal combined with micro-polishing to maintain immaculate gums and fresh breath.",
                "full_description": "Professional dental prophylaxis is the cornerstone of lifelong oral health. Even with diligent brushing, mineralized tartar (calculus) accumulates in hard-to-reach areas below the gumline. Our dental hygiene protocol uses gentle ultrasonic scaling followed by fine paste polishing to remove bacterial biofilm and surface stains without scratching enamel.",
                "involves": json.dumps([
                    "Ultrasonic piezo scaling to dislodge hardened calculus",
                    "Subgingival irrigation to flush out anaerobic bacteria",
                    "Diamond paste micro-polishing to smooth enamel surfaces",
                    "Gingival pocket depth assessment and personalised oral hygiene coaching"
                ]),
                "benefits": json.dumps([
                    "Reverses early gingivitis and prevents chronic periodontitis",
                    "Eliminates bad breath (halitosis) caused by trapped bacterial colonies",
                    "Removes stubborn coffee, tea, and tobacco surface stains",
                    "Leaves teeth feeling extraordinarily smooth, clean, and refreshed"
                ]),
                "candidates": json.dumps([
                    "All adults and teenagers every 6 months for preventative maintenance",
                    "Patients noticing bleeding gums during brushing or flossing",
                    "Individuals with persistent bad breath or visible yellow tartar deposits"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Gingival Assessment", "desc": "Screening gum margins and identifying tartar accumulation zones."},
                    {"step": 2, "title": "Piezo Ultrasonic Scaling", "desc": "Gentle sonic vibration with warm water spray to detach calculus deposits."},
                    {"step": 3, "title": "Interdental Flossing & Polishing", "desc": "Smoothing tooth surfaces with fine prophylaxis paste to inhibit stain reattachment."},
                    {"step": 4, "title": "Preventative Counseling", "desc": "Reviewing ideal brushing techniques and interdental brush sizing."}
                ]),
                "faqs": json.dumps([
                    {"q": "Does scaling loosen teeth or remove enamel?", "a": "No, this is a common myth. Scaling uses gentle sound vibrations to break away tartar; it cannot cut or weaken healthy enamel. If teeth feel slightly loose after cleaning, it is because heavy tartar was artificially bridging them while hiding underlying bone loss."},
                    {"q": "How often should I get my teeth cleaned?", "a": "Most patients benefit from a professional cleaning every 6 months. Patients with active periodontal disease may need maintenance every 3 to 4 months."}
                ]),
                "default_doctor_id": doc_ids.get("dr-jithin"),
                "duration_minutes": 30,
                "consultation_fee": 500,
                "image_url": "/static/images/scaling-polishing.jpg"
            },
            {
                "slug": "digital-dental-x-rays",
                "name": "Digital Dental X-rays & Diagnostics",
                "category": "General",
                "short_description": "Ultra-low-radiation digital radiography providing instant, high-definition visualization for accurate diagnosis.",
                "full_description": "Accurate treatment starts with accurate diagnosis. We utilize advanced digital intraoral radiography sensors that reduce patient radiation exposure by up to 80% compared to traditional dental films. High-resolution images appear on chairside HD monitors within seconds, enabling collaborative review between dentist and patient.",
                "involves": json.dumps([
                    "Direct digital sensor imaging with instant chairside display",
                    "High-resolution contrast optimization for early interproximal decay",
                    "Apical pathology and bone level evaluation",
                    "Safe lead aprons with thyroid collars for comprehensive patient protection"
                ]),
                "benefits": json.dumps([
                    "Up to 80% reduction in radiation exposure compared to conventional film",
                    "Instantaneous display with no chemical processing waste",
                    "Enhanced digital contrast to spot incipient micro-cavities early",
                    "Clear visual education: you see exactly what the doctor sees"
                ]),
                "candidates": json.dumps([
                    "New patients during comprehensive baseline examinations",
                    "Patients experiencing unexplained toothache or facial pain",
                    "Follow-up monitoring of healing bone after root canals or implant surgeries"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Sensor Positioning", "desc": "Comfortable placement of rounded digital sensors with specialized alignment holders."},
                    {"step": 2, "title": "Low-Dose Exposure", "desc": "Fraction-of-a-second exposure using high-frequency DC generator."},
                    {"step": 3, "title": "Instant Chairside Analysis", "desc": "High-definition image rendered immediately on the clinical monitor."},
                    {"step": 4, "title": "Patient Consultation", "desc": "Reviewing findings together and archiving images securely in your digital health record."}
                ]),
                "faqs": json.dumps([
                    {"q": "Are digital dental X-rays safe?", "a": "Yes. Digital dental X-rays emit an extremely low radiation dose—equivalent to the background radiation you receive during a 1-hour commercial flight. We strictly adhere to the ALARA (As Low As Reasonably Achievable) radiation safety standard."},
                    {"q": "Can I have an X-ray if I am pregnant?", "a": "Routine elective dental X-rays are typically postponed during pregnancy, but if urgent diagnostic care is required for pain or infection, digital X-rays can be performed safely with full abdominal and thyroid lead shielding."}
                ]),
                "default_doctor_id": doc_ids.get("dr-h-s-shreyas"),
                "duration_minutes": 15,
                "consultation_fee": 300,
                "image_url": "/static/images/digital-xray.jpg"
            },
            {
                "slug": "tooth-extraction",
                "name": "Tooth Extraction",
                "category": "Surgery",
                "short_description": "Gentle, atraumatic extractions designed to preserve surrounding bone and soft tissue for future restoration.",
                "full_description": "While our foremost mission is saving natural teeth, situations arise where a tooth is non-restorable due to severe trauma, unrestorable fracture, or advanced periodontal bone loss. We practice atraumatic extraction techniques using delicate micro-instruments to gently dislodge the tooth while preserving the surrounding alveolar bone socket.",
                "involves": json.dumps([
                    "Micro-luxation techniques preserving the delicate buccal bone wall",
                    "Profound local anesthesia ensuring complete comfort throughout",
                    "Thorough socket debridement and socket preservation grafting when indicated",
                    "Clear postoperative instructions and emergency contact support"
                ]),
                "benefits": json.dumps([
                    "Fast relief from severe pain and eradication of stubborn dental infections",
                    "Preservation of alveolar ridge architecture for future dental implants",
                    "Gentle, comfortable procedure with rapid tissue healing",
                    "Detailed postoperative guidance and medication to prevent dry sockets"
                ]),
                "candidates": json.dumps([
                    "Severely decayed or fractured teeth that cannot be restored biomimetically",
                    "Teeth with advanced periodontal disease and severe mobility",
                    "Compacted or problematic teeth interfering with orthodontic alignment"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "Radiographic Evaluation & Anesthesia", "desc": "Evaluating root curvature and achieving complete profound local anesthesia."},
                    {"step": 2, "title": "Atraumatic Luxation", "desc": "Gentle sectional release of periodontal ligament fibers without damaging bone."},
                    {"step": 3, "title": "Socket Cleansing", "desc": "Debridement of granulation tissue and socket irrigation with sterile saline."},
                    {"step": 4, "title": "Hemostasis & Recovery Care", "desc": "Application of sterile gauze pressure and delivery of recovery medication."}
                ]),
                "faqs": json.dumps([
                    {"q": "Will I feel pain during the tooth extraction?", "a": "You will feel pressure, but no pain. We ensure the tooth and surrounding tissues are entirely numb before starting. If you feel any sharp sensation at any point, we pause immediately to administer additional numbing."},
                    {"q": "How long does healing take?", "a": "Initial soft tissue closure occurs within 7 to 10 days. Bone remodeling inside the socket continues over 8 to 12 weeks."}
                ]),
                "default_doctor_id": doc_ids.get("dr-jithin"),
                "duration_minutes": 45,
                "consultation_fee": 500,
                "image_url": "/static/images/tooth-extraction.jpg"
            },
            {
                "slug": "oral-surgery",
                "name": "Oral Surgery & Wisdom Tooth Removal",
                "category": "Surgery",
                "short_description": "Specialized surgical procedures including impacted wisdom teeth removal, apicoectomy, and pre-prosthetic bone surgery.",
                "full_description": "Our oral surgery division provides specialized surgical interventions in a calm, sterile, hospital-grade outpatient setting. From surgical extraction of impacted mandibular third molars (wisdom teeth) to microscopic apicoectomies (root-end resections) and bone augmentation, procedures are performed with microsurgical precision.",
                "involves": json.dumps([
                    "Pre-surgical 3D imaging for inferior alveolar nerve mapping",
                    "Piezosurgical bone cutting that selectively cuts hard tissue while sparing delicate nerves",
                    "Impacted third molar sectioning and atraumatic removal",
                    "Microsurgical root-end resection (apicoectomy) and retrograde filling"
                ]),
                "benefits": json.dumps([
                    "Prevents damage to adjacent second molars, cysts, and jaw infections",
                    "Micro-piezosurgery minimizes postoperative facial swelling and pain",
                    "Preserves adjacent anatomical nerves and maxillary sinus integrity",
                    "Expert post-surgical follow-up protocol ensuring uncomplicated healing"
                ]),
                "candidates": json.dumps([
                    "Patients with impacted, painful, or partially erupted wisdom teeth (pericoronitis)",
                    "Persistent endodontic infections requiring root-end surgery (apicoectomy)",
                    "Patients needing pre-implant ridge augmentation or sinus lifts"
                ]),
                "process_steps": json.dumps([
                    {"step": 1, "title": "3D CBCT Surgical Planning", "desc": "Precise mapping of root anatomy relative to the mandibular nerve canal."},
                    {"step": 2, "title": "Profound Regional Anesthesia", "desc": "Ensuring complete numbness with targeted nerve blocks."},
                    {"step": 3, "title": "Microsurgical Removal", "desc": "Conservative bone removal and tooth sectioning for gentle retrieval."},
                    {"step": 4, "title": "Micro-Suturing & Recovery Protocol", "desc": "Careful closure with fine resorbable sutures and cold-pack application."}
                ]),
                "faqs": json.dumps([
                    {"q": "Do all wisdom teeth have to be removed?", "a": "No. If wisdom teeth erupt completely, are fully functional, painless, free of cavities, and can be cleaned effectively, they do not need removal. However, partially erupted or impacted wisdom teeth that trap bacteria or press against adjacent roots should be removed proactively."},
                    {"q": "What should I eat after oral surgery?", "a": "Stick to cool, soft foods for the first 48 hours—such as yogurt, smoothies (eaten with a spoon, not a straw), mashed potatoes, and cooled soups. Avoid crunchy, hot, or spicy foods."}
                ]),
                "default_doctor_id": doc_ids.get("dr-jithin"),
                "duration_minutes": 60,
                "consultation_fee": 700,
                "image_url": "/static/images/oral-surgery.jpg"
            }
        ]

        for t in treatments_data:
            cursor.execute("""
            INSERT INTO treatments (
                slug, name, category, short_description, full_description, 
                involves, benefits, candidates, process_steps, faqs, 
                default_doctor_id, duration_minutes, consultation_fee, image_url, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t["slug"], t["name"], t["category"], t["short_description"], t["full_description"],
                t["involves"], t["benefits"], t["candidates"], t["process_steps"], t["faqs"],
                t["default_doctor_id"], t["duration_minutes"], t["consultation_fee"], t["image_url"], 1
            ))
        conn.commit()

    # Seed clinic schedule (Mon-Sat 10:00-14:00 & 16:00-18:30, Sun Closed)
    if cursor.execute("SELECT COUNT(*) FROM clinic_schedule").fetchone()[0] == 0:
        for day in range(7):
            if day == 6: # Sunday
                cursor.execute("""
                INSERT INTO clinic_schedule (day_of_week, is_open, morning_start, morning_end, evening_start, evening_end, slot_duration_minutes)
                VALUES (?, 0, NULL, NULL, NULL, NULL, 30)
                """, (day,))
            else: # Monday through Saturday
                cursor.execute("""
                INSERT INTO clinic_schedule (day_of_week, is_open, morning_start, morning_end, evening_start, evening_end, slot_duration_minutes)
                VALUES (?, 1, '10:00', '14:00', '16:00', '18:30', 30)
                """, (day,))
        conn.commit()

    # Seed doctor availability
    if cursor.execute("SELECT COUNT(*) FROM doctor_availability").fetchone()[0] == 0:
        all_docs = cursor.execute("SELECT id FROM doctors").fetchall()
        for doc in all_docs:
            for day in range(7):
                if day == 6: # Sunday
                    cursor.execute("""
                    INSERT INTO doctor_availability (doctor_id, day_of_week, is_available, morning_available, evening_available)
                    VALUES (?, ?, 0, 0, 0)
                    """, (doc["id"], day))
                else:
                    cursor.execute("""
                    INSERT INTO doctor_availability (doctor_id, day_of_week, is_available, morning_available, evening_available)
                    VALUES (?, ?, 1, 1, 1)
                    """, (doc["id"], day))
        conn.commit()

    # Seed admin user
    if cursor.execute("SELECT COUNT(*) FROM admin_users").fetchone()[0] == 0:
        pw_hash, salt = hash_password("EnamelAdmin2026!")
        cursor.execute("""
        INSERT INTO admin_users (username, password_hash, salt, name, role)
        VALUES (?, ?, ?, ?, ?)
        """, ("admin", pw_hash, salt, "Clinic Director", "admin"))
        conn.commit()

    # Seed a few realistic appointments for testing the admin overview
    if cursor.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] == 0:
        sample_appointments = [
            (
                "EMD-2026-A101",
                "Arjun Rao",
                "+91 98450 12345",
                "arjun.rao@example.com",
                1, # RCT
                doc_ids.get("dr-h-s-shreyas"),
                "2026-11-10",
                "10:30",
                "Confirmed",
                "Mild sensitivity in upper right molar.",
                "Confirmed via WhatsApp."
            ),
            (
                "EMD-2026-B202",
                "Priya Natarajan",
                "+91 94801 56789",
                "priya.n@example.com",
                7, # Invisalign
                doc_ids.get("dr-rohit"),
                "2026-11-10",
                "11:30",
                "Confirmed",
                "Interested in clear aligners for front spacing.",
                "Scan scheduled."
            ),
            (
                "EMD-2026-C303",
                "Vikram Gowda",
                "+91 97412 89012",
                "vikram.g@example.com",
                8, # Dental Implants
                doc_ids.get("dr-jithin"),
                "2026-11-11",
                "16:30",
                "Pending",
                "Consultation for lower left missing molar.",
                None
            )
        ]
        cursor.executemany("""
        INSERT INTO appointments (
            booking_ref, patient_name, patient_phone, patient_email, 
            treatment_id, doctor_id, appointment_date, appointment_time, 
            status, patient_notes, admin_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_appointments)
        conn.commit()

    conn.close()
    print("Database initialization and seed complete!")

if __name__ == "__main__":
    seed_database()
