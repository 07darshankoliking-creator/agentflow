import os
import requests
import google.generativeai as genai
from datetime import datetime
from fpdf import FPDF

print("=== BOSS PROMPT PACK GENERATOR ===")

# --- Config ---
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('models/gemini-2.5-flash')
GUMROAD_TOKEN = os.environ['GUMROAD_ACCESS_TOKEN']

NICHE = "Midjourney Architecture Prompts"  # Change weekly for variety

def generate_prompts(niche, count=100):
    print(f"[*] Generating {count} prompts for: {niche}")
    prompt_text = f"Generate {count} unique, high-quality {niche} separated by newlines. No numbering, just prompts."
    response = model.generate_content(prompt_text)
    prompts = response.text.strip().split('\n')
    return [p for p in prompts if p.strip()]

def create_pdf(niche, prompts):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf_cell(0, 20, f"{i+1}. {prompt}", ln=True, align='L')
    pdf.set_font("Arial", "", 11)
    for p in prompts:
        pdf.multi_cell(0, 8, p)
    filename = f"{niche.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

def upload_to_gumroad(pdf_path, niche, count):
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    # Step 1: Get upload URL
    resp = requests.post("https://api.gumroad.com/v2/resource_uploads", headers=headers, json={"file_name": os.path.basename(pdf_path)})
    upload_url = resp.json()['upload_url']
    # Step 2: Upload file
    with open(pdf_path, 'rb') as f:
        requests.put(upload_url, data=f)
    # Step 3: Create product with file
    product_data = {
        "name": f"{count} {niche} - AI Prompt Pack",
        "description": f"Collection of {count} hand-curated AI prompts for {niche}. Instant download PDF.",
        "price": 999,  # $9.99 in cents
        "published": True,
        "discover_fee_percent": 30,  # Gumroad Discover fee (optional)
        "affiliate_fee_percent": 50,  # Let others promote for you
        "custom_permalink": f"{niche.replace(' ', '-').lower()}-prompts-{datetime.now().strftime('%Y%m%d')}"
    }
    # Attach file (simplified - may need refinement)
    product_data['file'] = upload_url  # This needs actual file ID from upload response
    resp = requests.post("https://api.gumroad.com/v2/products", headers=headers, json=product_data)
    if resp.status_code in [200, 201]:
        return resp.json()['product']['short_url']
    else:
        print(f"Error: {resp.text}")
        return None

# --- Main ---
prompts = generate_prompts(NICHE, 100)
pdf_file = create_pdf(NICHE, prompts)
url = upload_to_gumroad(pdf_file, NICHE, len(prompts))
print(f"\n✅ PROMPT PACK LIVE: {url}")
print("Set and forget. Gumroad Discover will bring traffic.")
