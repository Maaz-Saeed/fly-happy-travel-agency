"""One-off utility: generates placeholder image assets (logo, favicon, hero image,
and per-item photos for destinations/airlines/packages/hotels/testimonials/team/
news/gallery) so the site never shows a broken image before the client supplies
real photography and their real logo.

Run once with:  python scripts/generate_placeholders.py
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMG_DIR = os.path.join(BASE, "app", "static", "images")

GREEN_DARK = (13, 79, 49)
GREEN = (20, 122, 73)
GREEN_LIGHT = (46, 168, 107)
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)

sys.path.insert(0, BASE)
from app.seed import DESTINATIONS, AIRLINES, TEAM_MEMBERS, TESTIMONIAL_DATA, NEWS_ITEMS  # noqa: E402


def font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def gradient(w, h, c1, c2, vertical=True):
    base = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.new("L", (w, h))
    mask_data = []
    for y in range(h):
        for x in range(w):
            ratio = (y / h) if vertical else (x / w)
            mask_data.append(int(255 * ratio))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def centered_text(draw, box_w, box_h, text, fnt, fill, y_offset=0):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((box_w - tw) / 2, (box_h - th) / 2 + y_offset - bbox[1]), text, font=fnt, fill=fill)


def make_placeholder(path, w, h, title, subtitle=None, seed_key=""):
    random.seed(hash(seed_key) & 0xFFFFFFFF)
    c2 = random.choice([GREEN, GREEN_LIGHT, GREEN_DARK])
    img = gradient(w, h, GREEN_DARK, c2)
    # subtle diagonal texture
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(-h, w, 60):
        odraw.line([(i, 0), (i + h, h)], fill=(255, 255, 255, 12), width=18)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    title_font = font(int(h * 0.11))
    centered_text(draw, w, h, title, title_font, WHITE, y_offset=-h * 0.06 if subtitle else 0)
    if subtitle:
        sub_font = font(int(h * 0.06), bold=False)
        centered_text(draw, w, h, subtitle, sub_font, GOLD, y_offset=h * 0.14)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, quality=85)


def make_logo():
    w, h = 600, 600
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, w - 20, h - 20], fill=GREEN_DARK, outline=GOLD, width=10)
    draw.ellipse([50, 50, w - 50, h - 50], outline=GREEN_LIGHT, width=4)

    # simple airplane glyph using Font Awesome-like unicode fallback: draw a stylised plane shape
    cx, cy = w / 2, h / 2 - 30
    plane = [
        (cx, cy - 130), (cx + 26, cy - 40), (cx + 150, cy + 10), (cx + 150, cy + 45),
        (cx + 26, cy + 25), (cx + 15, cy + 120), (cx + 55, cy + 160), (cx + 55, cy + 185),
        (cx, cy + 150), (cx - 55, cy + 185), (cx - 55, cy + 160), (cx - 15, cy + 120),
        (cx - 26, cy + 25), (cx - 150, cy + 45), (cx - 150, cy + 10), (cx - 26, cy - 40),
    ]
    draw.polygon(plane, fill=WHITE)

    f1 = font(70)
    f2 = font(30, bold=False)
    centered_text(draw, w, h, "FLY HAPPY", f1, WHITE, y_offset=150)
    centered_text(draw, w, h, "INTERNATIONAL TRAVELS", f2, GOLD, y_offset=205)

    os.makedirs(IMG_DIR, exist_ok=True)
    img.save(os.path.join(IMG_DIR, "logo.png"))

    # favicon (multi-size ico)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    img.save(os.path.join(BASE, "app", "static", "favicon.ico"), sizes=icon_sizes)


def make_hero():
    w, h = 1920, 1080
    img = gradient(w, h, (8, 46, 28), (24, 134, 79))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    random.seed(1)
    for _ in range(40):
        x, y = random.randint(0, w), random.randint(0, h)
        r = random.randint(2, 4)
        odraw.ellipse([x, y, x + r, y + r], fill=(255, 255, 255, 180))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(os.path.join(IMG_DIR, "hero-bg.jpg"), quality=88)


def make_default_avatar():
    w, h = 300, 300
    img = Image.new("RGB", (w, h), GREEN)
    draw = ImageDraw.Draw(img)
    draw.ellipse([90, 50, 210, 170], fill=WHITE)
    draw.ellipse([40, 190, 260, 340], fill=WHITE)
    img.save(os.path.join(IMG_DIR, "default_avatar.png"))


def make_partner_logos():
    partners = ["Visa", "MasterCard", "JazzCash", "EasyPaisa", "IATA", "TripAdvisor"]
    for p in partners:
        make_placeholder(os.path.join(IMG_DIR, "partners", f"{p.lower()}.png"), 300, 150, p, seed_key=p)


def main():
    print("Generating logo & favicon...")
    make_logo()
    print("Generating hero background...")
    make_hero()
    print("Generating default avatar...")
    make_default_avatar()
    print("Generating partner logos...")
    make_partner_logos()

    print(f"Generating {len(DESTINATIONS)} destination images...")
    for row in DESTINATIONS:
        country, city, airport, code, *_ = row
        make_placeholder(os.path.join(IMG_DIR, "destinations", f"{code.lower()}.jpg"),
                          800, 550, city, country, seed_key=code)

    print(f"Generating {len(AIRLINES)} airline logos...")
    for name, code, country, *_ in AIRLINES:
        make_placeholder(os.path.join(IMG_DIR, "airlines", f"{code.lower()}.png"),
                          400, 220, code, name, seed_key=code)

    print("Generating package images...")
    package_cities = ["Dubai", "Istanbul", "Madinah", "Jeddah", "Bangkok", "Bali", "Male", "London",
                       "Kuala Lumpur", "Doha", "Johannesburg", "Cairo", "Zurich", "Muscat", "Sydney",
                       "Baku", "Kathmandu", "Madrid"]
    for city in package_cities:
        make_placeholder(os.path.join(IMG_DIR, "packages", f"{city.lower().replace(' ', '_')}.jpg"),
                          800, 550, city, "Travel Package", seed_key="pkg" + city)

    print("Generating hotel images...")
    hotel_names = ["burj_al_arab_jumeirah", "address_downtown", "hilton_istanbul_bosphorus",
                   "anantara_vacation_club_bangkok", "the_ritzcarlton_bali", "conrad_maldives_rangali_island",
                   "the_savoy_london", "grand_hyatt_doha", "steigenberger_al_dau_jeddah",
                   "frontel_al_harithia_madinah", "sheraton_kuala_lumpur", "fairmont_cairo"]
    for h in hotel_names:
        make_placeholder(os.path.join(IMG_DIR, "hotels", f"{h}.jpg"), 800, 550,
                          h.replace("_", " ").title(), "Hotel", seed_key=h)

    print("Generating testimonial photos...")
    for i in range(10):
        make_placeholder(os.path.join(IMG_DIR, "testimonials", f"customer{i + 1}.jpg"),
                          300, 300, f"C{i + 1}", seed_key=f"cust{i}")

    print("Generating team photos...")
    for i in range(6):
        make_placeholder(os.path.join(IMG_DIR, "team", f"team{i + 1}.jpg"), 400, 400,
                          TEAM_MEMBERS[i][0].split()[0], seed_key=f"team{i}")

    print("Generating news images...")
    for title, slug, summary in NEWS_ITEMS:
        make_placeholder(os.path.join(IMG_DIR, "news", f"{slug}.jpg"), 800, 500, "News", seed_key=slug)

    print("Generating gallery images...")
    for i in range(12):
        make_placeholder(os.path.join(IMG_DIR, "gallery", f"gallery{i + 1}.jpg"), 600, 450,
                          "Fly Happy", seed_key=f"gal{i}")

    print("Done. All placeholder images generated in app/static/images/")


if __name__ == "__main__":
    main()
