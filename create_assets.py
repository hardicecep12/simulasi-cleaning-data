# create_assets.py
import base64
import os

os.makedirs("assets", exist_ok=True)

# 1. Logo Utama Horizontal (assets/logo.svg)
logo_svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 64" width="100%" height="100%">
  <defs>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>
    <linearGradient id="tealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#14B8A6" />
      <stop offset="100%" stop-color="#0D9488" />
    </linearGradient>
  </defs>

  <!-- Simbol Pipeline & Database Data -->
  <g transform="translate(6, 6)">
    <!-- Node Database Mentah -->
    <rect x="4" y="6" width="22" height="40" rx="5" fill="#EFF6FF" stroke="url(#blueGrad)" stroke-width="2.5" />
    <line x1="10" y1="16" x2="20" y2="16" stroke="#2563EB" stroke-width="2" stroke-linecap="round" />
    <line x1="10" y1="26" x2="20" y2="26" stroke="#2563EB" stroke-width="2" stroke-linecap="round" />
    <line x1="10" y1="36" x2="20" y2="36" stroke="#2563EB" stroke-width="2" stroke-linecap="round" />

    <!-- Jalur Aliran Data -->
    <path d="M26 26 L38 26" stroke="#0D9488" stroke-width="2" stroke-dasharray="3 3" stroke-linecap="round" />

    <!-- Node Pembersihan / Verified Checkmark -->
    <circle cx="44" cy="26" r="9" fill="url(#tealGrad)" />
    <polyline points="40.5,26 43,28.5 47.5,23.5" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
  </g>

  <!-- Tipografi Brand -->
  <text x="74" y="34" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="22" font-weight="800" fill="#0F172A">OmniData</text>
  <text x="74" y="49" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="600" fill="#0D9488" letter-spacing="2">PREP STUDIO</text>
</svg>"""

with open("assets/logo.svg", "w", encoding="utf-8") as f:
    f.write(logo_svg_content)

# 2. Ikon Logo Ringkas / Collapsed Sidebar (assets/logo_icon.svg)
logo_icon_svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="100%" height="100%">
  <defs>
    <linearGradient id="blueGradIcon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>
    <linearGradient id="tealGradIcon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#14B8A6" />
      <stop offset="100%" stop-color="#0D9488" />
    </linearGradient>
  </defs>

  <!-- Latar Belakang Kartu Vektor -->
  <rect x="4" y="4" width="56" height="56" rx="14" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="2"/>

  <!-- Database Silinder -->
  <rect x="14" y="12" width="22" height="40" rx="5" fill="#EFF6FF" stroke="url(#blueGradIcon)" stroke-width="3" />
  <line x1="20" y1="22" x2="30" y2="22" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" />
  <line x1="20" y1="32" x2="30" y2="32" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" />
  <line x1="20" y1="42" x2="30" y2="42" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" />

  <!-- Badge Validasi Bersih -->
  <circle cx="44" cy="32" r="11" fill="url(#tealGradIcon)" stroke="#FFFFFF" stroke-width="2"/>
  <polyline points="39.5,32 42.5,35 48.5,29" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
</svg>"""

with open("assets/logo_icon.svg", "w", encoding="utf-8") as f:
    f.write(logo_icon_svg_content)

# 3. Favicon 32x32 px PNG (assets/favicon.png)
favicon_base64 = (
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMA"
    "AAsTAAALEwEAmpwYAAAAB3RJTUUH6AgBFAw15+1k5QAAAc5JREFUWMPtVz1uhDAQnmfWWSGho4uU"
    "3CG1HCVXyBW4Q07AFbiDVHIF9khDkSIdEjWroLAze20WQiIkyIp2V/aPZ775eTwztsDM+I+jruvn"
    "qqpqInrQ9/07Eee2bdfGmPtpmr49z/v2ff9V1/VD0zTf/7YFEpGfZdmJiF5938f3/dO2bX+klOek"
    "iMh5njeJ6CilvGZZ9vYnCyAiZ2aGiBwRkZk5IjJbAYwx23Vd3+fz+dIY89MY80RElIh2Zt6EEBgi"
    "QkSMiBwRHb8F4Pf7/WUYhm/OuQkhICJ8uVyuSimNiBiG4RQR8e12+17X9d/2wBgTEhFHRKiqCoqi"
    "gHNORARCCEgp4Zxj7/3ZOfd5sICU0iAiIKU82bYN59x9y4yI8N7De49t2zAMw9U593mwgDFmQ0RE"
    "RAgp4b0/i/yfiMA5B+/9wRgzePDs31xARKZpmvM4jmvXda/W2rcxZjvP88Vae2XmVRiGj8YY1/f9"
    "zY9PzN0CiOhQ1/Wz9/69LMt3a+1dRHQ6n8+fZVme0zT9NMZc6rr+7vs+vyuBiN6J6F6W5Zdzbo8I"
    "i4jQOQdr7dt13fu+719vfgV+gWEYvjHz3Vr7joiICDjn4JwDY4yICLquu7X2c6r7E+wF1/zL18f6"
    "AAAAAElFTkSuQmCC"
)

with open("assets/favicon.png", "wb") as f:
    f.write(base64.b64decode(favicon_base64))

print("Berhasil! Semua aset visual telah dibuat:")
print("1. assets/logo.svg")
print("2. assets/logo_icon.svg")
print("3. assets/favicon.png")
