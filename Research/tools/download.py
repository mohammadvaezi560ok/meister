#!/usr/bin/env python3
"""Konkurrenz-Research: Screenshots, Produktbilder, Bewertungsbilder, Ads und Videos laden.

Ablauf
  1. Jede Seite aus quellen.json wird mit Chromium geöffnet, komplett gescrollt
     (damit Lazy-Load-Bilder und Bewertungs-Widgets nachladen) und als
     Full-Page-Screenshot gespeichert.
  2. Alle Bild-/Video-URLs der Seite werden gesammelt, auf die Originalgröße
     hochgerechnet (Shopify-CDN, AliExpress-CDN) und geladen.
  3. Jede Datei landet direkt im Themen-Ordner (nicht nach Shop getrennt);
     der Shop steht vorn im Dateinamen. Duplikate (gleicher Inhalt) und
     Mini-Grafiken (Icons, Logos, Zahlungsarten) werden aussortiert.
  4. Videos aus der Liste "videos" werden mit yt-dlp in bester Qualität geladen.

Benötigt: pip install playwright yt-dlp pillow
Start:    python3 Research/tools/download.py            (alles)
          python3 Research/tools/download.py --nur-videos
"""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ORDNER = {
    "produkt": ROOT / "01_Produktbilder",
    "bewertung": ROOT / "02_Bewertungen",
    "video": ROOT / "03_Videos",
    "ads": ROOT / "04_Ads",
    "screenshot": ROOT / "05_Screenshots",
    "advertorial": ROOT / "06_Landingpages",
}
MIN_KANTE = 400  # kleinere Bilder sind fast immer Icons/Logos
REVIEW_HINWEISE = ("loox", "judge.me", "judgeme", "okendo", "stamped", "yotpo",
                   "reviews.io", "trustpilot", "review", "ugc", "ae-pic-a1")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Sammelt alle Medien inkl. Herkunft (liegt das Element in einem Bewertungs-Widget?)
SAMMEL_JS = r"""
() => {
  const out = [];
  const inReview = el => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = ((n.id || '') + ' ' + (n.className && n.className.baseVal !== undefined
                 ? n.className.baseVal : n.className || '')).toLowerCase();
      if (/review|loox|jdgm|judge|okendo|stamped|yotpo|testimonial|feedback|evaluation/.test(s)) return true;
    }
    return false;
  };
  const bestFromSrcset = ss => {
    let best = null, bw = 0;
    for (const part of (ss || '').split(',')) {
      const [u, w] = part.trim().split(/\s+/);
      const n = parseInt(w) || 1;
      if (u && n >= bw) { best = u; bw = n; }
    }
    return best;
  };
  document.querySelectorAll('img, source').forEach(el => {
    const cands = [bestFromSrcset(el.getAttribute('srcset')), bestFromSrcset(el.getAttribute('data-srcset')),
                   el.getAttribute('data-src'), el.getAttribute('data-zoom'), el.getAttribute('data-original'),
                   el.currentSrc, el.getAttribute('src')];
    // alle Kandidaten behalten – tote Lazy-Load-Pfade fallen beim Download raus, Duplikate per Hash
    new Set(cands.filter(c => c && !c.startsWith('data:'))).forEach(u =>
      out.push({url: u, typ: el.closest('video') ? 'video' : 'bild', review: inReview(el)}));
  });
  document.querySelectorAll('video').forEach(el => {
    const u = el.currentSrc || el.getAttribute('src');
    if (u && !u.startsWith('blob:')) out.push({url: u, typ: 'video', review: inReview(el)});
    if (el.poster) out.push({url: el.poster, typ: 'bild', review: inReview(el)});
  });
  document.querySelectorAll('*').forEach(el => {
    const m = getComputedStyle(el).backgroundImage.match(/url\(["']?(.*?)["']?\)/);
    if (m && !m[1].startsWith('data:')) out.push({url: m[1], typ: 'bild', review: inReview(el)});
  });
  return out;
}
"""


def original_groesse(url: str) -> str:
    """Rechnet CDN-Vorschaubilder auf die größte verfügbare Version hoch."""
    if "cdn.shopify.com" in url or "/cdn/shop/" in url:
        url = re.sub(r"_(\d+x\d*|\d*x\d+|small|medium|large|grande|compact|thumb)(?=(@\dx)?\.\w+)", "", url)
        url = re.sub(r"([?&])(width|height|crop)=[^&]*&?", r"\1", url).rstrip("?&")
    if "alicdn.com" in url:
        url = re.sub(r"(\.(jpg|jpeg|png|webp))_.*$", r"\1", url, flags=re.I)
    if "m.media-amazon.com" in url or "images-amazon.com" in url:
        url = re.sub(r"\._[^/]*_\.", ".", url)
    return url


def hole(url: str, referer: str) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": referer})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except Exception as e:  # einzelne kaputte Medien sollen den Lauf nicht abbrechen
        print(f"    ! {url[:90]} – {e}")
        return None


class Ablage:
    def __init__(self):
        self.gesehen = set()
        for d in ORDNER.values():
            d.mkdir(parents=True, exist_ok=True)
            for f in d.glob("*.*"):
                self.gesehen.add(hashlib.sha1(f.read_bytes()).hexdigest())

    def speichere(self, daten: bytes, ordner: str, shop: str, endung: str) -> Path | None:
        h = hashlib.sha1(daten).hexdigest()
        if h in self.gesehen:
            return None
        self.gesehen.add(h)
        ziel = ORDNER[ordner]
        nr = len(list(ziel.glob(f"{shop}__*"))) + 1
        pfad = ziel / f"{shop}__{nr:03d}.{endung}"
        pfad.write_bytes(daten)
        return pfad


def bild_ok(daten: bytes) -> tuple[bool, str]:
    try:
        im = Image.open(io.BytesIO(daten))
        fmt = (im.format or "jpg").lower().replace("jpeg", "jpg")
        return min(im.size) >= MIN_KANTE, fmt
    except Exception:
        return False, ""


def seite_verarbeiten(page, eintrag: dict, ablage: Ablage):
    shop, art, url = eintrag["shop"], eintrag["art"], eintrag["url"]
    print(f"\n== {shop} ({art}) {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(4000)
    # Langsam scrollen, damit Lazy-Load und Review-Widgets nachladen
    for _ in range(60):
        page.mouse.wheel(0, 1200)
        page.wait_for_timeout(400)
    for knopf in ("Load more", "Mehr anzeigen", "Show more", "See more", "Weitere Bewertungen"):
        for _ in range(5):
            el = page.get_by_text(knopf, exact=False).first
            if not el.count() or not el.is_visible():
                break
            el.click()
            page.wait_for_timeout(1500)

    shot = ORDNER["screenshot"] / f"{shop}__{art}__{len(list(ORDNER['screenshot'].glob(f'{shop}__*'))) + 1:02d}.png"
    page.screenshot(path=str(shot), full_page=True)
    print(f"  Screenshot: {shot.name}")

    # Shopify: Produkt-JSON liefert alle Galeriebilder in Originalauflösung
    medien = page.evaluate(SAMMEL_JS)
    if "/products/" in url:
        js = hole(url.split("?")[0] + ".json", url)
        try:
            for img in json.loads(js)["product"]["images"]:
                medien.append({"url": img["src"], "typ": "bild", "review": False})
        except Exception:
            pass

    zaehler = {}
    for m in {m["url"]: m for m in medien}.values():
        voll = original_groesse(urljoin(url, m["url"]))
        if urlparse(voll).scheme not in ("http", "https") or voll.lower().endswith(".svg"):
            continue
        ist_review = m["review"] or any(k in voll.lower() for k in REVIEW_HINWEISE[:6]) or art == "bewertungen"
        ordner = ("ads" if art == "ads" else "advertorial" if art == "advertorial"
                  else "bewertung" if ist_review else "produkt")
        daten = hole(voll, url)
        if not daten:
            continue
        if m["typ"] == "video":
            endung = Path(urlparse(voll).path).suffix.lstrip(".") or "mp4"
            if ordner == "produkt":
                ordner = "video"
        else:
            ok, endung = bild_ok(daten)
            if not ok:
                continue
        if ablage.speichere(daten, ordner, shop, endung):
            zaehler[ordner] = zaehler.get(ordner, 0) + 1
    print(f"  gespeichert: {zaehler or 'nichts Neues'}")


def videos_laden(urls: list[str]):
    ziel = ORDNER["video"]
    ziel.mkdir(parents=True, exist_ok=True)
    for u in urls:
        print(f"\n== Video {u}")
        subprocess.run([sys.executable, "-m", "yt_dlp", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
                        "--no-playlist", "--write-thumbnail", "--convert-thumbnails", "jpg",
                        "-o", str(ziel / "%(extractor)s__%(uploader)s__%(id)s.%(ext)s"), u])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quellen", default=str(Path(__file__).with_name("quellen.json")))
    ap.add_argument("--nur-videos", action="store_true")
    ap.add_argument("--nur-seiten", action="store_true")
    a = ap.parse_args()
    q = json.loads(Path(a.quellen).read_text())

    if not a.nur_videos:
        from playwright.sync_api import sync_playwright
        ablage = Ablage()
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception:  # Cloud-Container: vorinstalliertes Chromium statt "playwright install"
                browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
            ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900},
                                      locale="de-DE", device_scale_factor=2)
            page = ctx.new_page()
            for e in q["seiten"]:
                try:
                    seite_verarbeiten(page, e, ablage)
                except Exception as ex:
                    print(f"  ! Seite übersprungen: {ex}")
            browser.close()
    if not a.nur_seiten:
        videos_laden(q.get("videos", []))


if __name__ == "__main__":
    main()
