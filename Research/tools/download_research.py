#!/usr/bin/env python3
"""Laedt Konkurrenz-Material fuer das Kniekissen in den Research-Ordner.

Was es holt (Quellen stehen in quellen.json):
  - Shopify-Shops: alle Produktbilder in Originalgroesse (ueber <produkt>.json),
    Bewertungsbilder (Judge.me, Loox, Okendo, Yotpo, Stamped, ...), Ganzseiten-Screenshot,
    Produkttext
  - Andere Produktseiten (Amazon, Kaufland, ...): Bilder, Screenshot
  - AliExpress: Produktbilder in Originalgroesse + Bewertungsfotos + Bewertungstexte (CSV)
  - Meta-Werbebibliothek: Anzeigen-Videos und -Bilder pro Suchbegriff + Screenshot
  - TikTok / Instagram: Videos ueber yt-dlp (Hashtags, Profile, einzelne Videos)

Installation (einmalig):
  pip install playwright requests yt-dlp gallery-dl
  playwright install chromium

Aufruf (aus dem Repo-Ordner):
  python3 Research/tools/download_research.py              # alles
  python3 Research/tools/download_research.py shops ads    # nur Teile
  Teile: shops, seiten, aliexpress, ads, tiktok, instagram
  Fuer Instagram/TikTok mit Login: --cookies-from-browser chrome
"""

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

import requests
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
QUELLEN = json.loads((Path(__file__).parent / "quellen.json").read_text(encoding="utf-8"))
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
SESSION = requests.Session()
SESSION.headers["User-Agent"] = UA

# Bild-CDNs der gaengigen Bewertungs-Apps
REVIEW_HOSTS = re.compile(
    r"judgeme|judge\.me|loox|okendo|d3hw6dc1ow8pp2\.cloudfront|yotpo|stamped|"
    r"alireviews|ryviu|trustoo|rivyo|reviews\.io|kudobuzz|opinew|fera\.ai|vitals|air-reviews|growave",
    re.I,
)
IMG_EXT = re.compile(r"\.(jpe?g|png|webp|avif|gif)(\?|$)", re.I)
_seen_hashes: set[str] = set()


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")[:80] or "x"


def full_res(url: str) -> str:
    """Wandelt Vorschau-URLs in die Originalgroesse um."""
    if url.startswith("//"):
        url = "https:" + url
    host = urlsplit(url).netloc
    if "alicdn.com" in host:
        # ..._640x640q75.jpg_.avif -> .jpg
        return re.sub(r"(\.(?:jpe?g|png|webp))_.*$", r"\1", url, flags=re.I)
    if "shopify" in host or "/cdn/shop/" in url:
        url = re.sub(r"_(\d+x\d*|x\d+|pico|icon|thumb|small|compact|medium|large|grande|master)(?=\.)", "", url)
        parts = urlsplit(url)
        query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k not in ("width", "height", "crop")])
        return urlunsplit((parts.scheme or "https", parts.netloc, parts.path, query, ""))
    if REVIEW_HOSTS.search(host) or "imgix" in host or "cloudfront" in host:
        # Groessen-Parameter (w=, h=, fit=) entfernen -> Original
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    if "media-amazon.com" in host or "ssl-images-amazon" in host:
        return re.sub(r"\._[^/]*_\.", ".", url)
    return url


def download(url: str, folder: Path, name: str | None = None) -> Path | None:
    folder.mkdir(parents=True, exist_ok=True)
    url = full_res(url)
    try:
        r = SESSION.get(url, timeout=60)
        if r.status_code != 200 or len(r.content) < 3000:  # Icons/Platzhalter ignorieren
            return None
    except requests.RequestException as e:
        print("   !", url, e)
        return None
    digest = hashlib.sha1(r.content).hexdigest()
    if digest in _seen_hashes:
        return None
    _seen_hashes.add(digest)
    ctype = r.headers.get("content-type", "")
    ext = {
        "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/avif": ".avif",
        "image/gif": ".gif", "video/mp4": ".mp4",
    }.get(ctype.split(";")[0], Path(urlsplit(url).path).suffix or ".bin")
    path = folder / f"{name or digest[:12]}{ext}"
    path.write_bytes(r.content)
    print("   +", path.relative_to(ROOT))
    return path


# ---------- Browser-Hilfen ----------

def new_page(browser):
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900}, locale="de-DE")
    return ctx.new_page()


def accept_cookies(page):
    for label in ["Alle akzeptieren", "Alle Cookies erlauben", "Akzeptieren", "Accept all",
                  "Allow all cookies", "Accept", "Zustimmen", "OK"]:
        try:
            btn = page.get_by_role("button", name=re.compile(f"^{label}", re.I)).first
            if btn.is_visible(timeout=500):
                btn.click()
                time.sleep(1)
                return
        except Exception:
            pass


def scroll_through(page, rounds=25):
    for _ in range(rounds):
        page.mouse.wheel(0, 1400)
        time.sleep(0.6)


def click_load_more(page, max_clicks=30):
    """Klickt 'Mehr Bewertungen laden' in der Seite und in allen Iframes (z. B. Loox)."""
    pattern = re.compile(r"(mehr|weitere)\s+(bewertungen|laden|anzeigen)|load more|show more|more reviews|see more", re.I)
    for _ in range(max_clicks):
        clicked = False
        for frame in page.frames:
            try:
                btn = frame.get_by_role("button", name=pattern).first
                text = (btn.inner_text(timeout=500) or "").lower()
                if any(w in text for w in ("warenkorb", "cart", "kaufen", "buy")):
                    continue
                if btn.is_visible(timeout=500):
                    btn.click(timeout=2000)
                    clicked = True
                    time.sleep(1.5)
            except Exception:
                pass
        if not clicked:
            break


def collect_image_urls(page) -> set[str]:
    urls = set()
    js = """() => {
      const out = [];
      document.querySelectorAll('img, source, a, [style*="background"]').forEach(el => {
        for (const a of ['src', 'data-src', 'data-original', 'href', 'data-zoom-image']) {
          const v = el.getAttribute && el.getAttribute(a); if (v) out.push(v);
        }
        const ss = el.getAttribute && (el.getAttribute('srcset') || el.getAttribute('data-srcset'));
        if (ss) ss.split(',').forEach(p => out.push(p.trim().split(' ')[0]));
        const m = (el.getAttribute('style') || '').match(/url\\(["']?([^"')]+)/); if (m) out.push(m[1]);
      });
      return out;
    }"""
    for frame in page.frames:
        try:
            for u in frame.evaluate(js):
                if IMG_EXT.search(u) or "imgix" in u or "loox" in u:
                    urls.add(u if not u.startswith("//") else "https:" + u)
        except Exception:
            pass
    return urls


def screenshot(page, folder: Path, name: str):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{slug(name)}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
    except Exception as e:
        print("   ! Screenshot fehlgeschlagen:", e)
        return
    print("   +", path)


# ---------- Quellen ----------

def shopify_shops(browser):
    for shop in QUELLEN["shopify_shops"]:
        if not shop["url"]:
            continue
        name, url = shop["name"], shop["url"].split("?")[0]
        print(f"\n== Shopify: {name}")
        try:
            product = SESSION.get(url + ".json", timeout=30).json()["product"]
            for i, img in enumerate(product.get("images", []), 1):
                download(img["src"], ROOT / "01_Produktbilder" / slug(name), f"{i:02d}")
            text = re.sub(r"<[^>]+>", "\n", product.get("body_html") or "")
            (ROOT / "07_Texte").mkdir(exist_ok=True)
            (ROOT / "07_Texte" / f"{slug(name)}_produkttext.txt").write_text(
                f"{product.get('title')}\n{url}\n\n" + re.sub(r"\n\s*\n+", "\n\n", text), encoding="utf-8")
        except Exception as e:
            print("   ! products.json nicht lesbar:", e)
        try:
            browse_reviews(browser, name, url)
        except Exception as e:
            print("   ! Seite nicht ladbar:", e)


def browse_reviews(browser, name, url):
    page = new_page(browser)
    review_hits: set[str] = set()
    page.on("response", lambda r: review_hits.add(r.url)
            if REVIEW_HOSTS.search(urlsplit(r.url).netloc) and r.request.resource_type == "image" else None)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        time.sleep(3)
        accept_cookies(page)
        screenshot(page, ROOT / "06_Screenshots" / slug(name), "produktseite_oben")
        scroll_through(page)
        click_load_more(page)
        scroll_through(page, 10)
        screenshot(page, ROOT / "06_Screenshots" / slug(name), "produktseite_komplett")
        all_urls = collect_image_urls(page) | review_hits
    finally:
        page.context.close()
    for u in sorted(all_urls):
        if REVIEW_HOSTS.search(u):
            download(u, ROOT / "02_Bewertungen" / slug(name))
        elif "shopify" in u or "/cdn/shop/" in u or "media-amazon" in u or "kaufland" in u:
            download(u, ROOT / "01_Produktbilder" / slug(name))


def andere_seiten(browser):
    for item in QUELLEN["andere_produktseiten"]:
        if item["url"]:
            print(f"\n== Seite: {item['name']}")
            try:
                browse_reviews(browser, item["name"], item["url"])
            except Exception as e:
                print("   !", e)


def aliexpress(browser):
    for pid in QUELLEN["aliexpress_ids"]:
        name = f"AliExpress_{pid}"
        print(f"\n== {name}")
        page = new_page(browser)
        try:
            page.goto(f"https://de.aliexpress.com/item/{pid}.html", wait_until="domcontentloaded", timeout=90000)
            time.sleep(4)
            accept_cookies(page)
            screenshot(page, ROOT / "06_Screenshots" / name, "produktseite_oben")
            scroll_through(page, 15)
            screenshot(page, ROOT / "06_Screenshots" / name, "produktseite_komplett")
            for u in sorted(collect_image_urls(page)):
                if "alicdn.com/kf/" in u:
                    download(u, ROOT / "01_Produktbilder" / name)
        except Exception as e:
            print("   ! Seite (evtl. Captcha):", e)
        page.context.close()
        aliexpress_reviews(pid, name)


def aliexpress_reviews(pid, name):
    rows = []
    for p in range(1, 31):
        api = ("https://feedback.aliexpress.com/pc/searchEvaluation.do?"
               f"productId={pid}&lang=de_DE&country=DE&page={p}&pageSize=50&filter=all&sort=complex_default")
        try:
            data = SESSION.get(api, timeout=30, headers={"Referer": "https://de.aliexpress.com/"}).json()
            reviews = data["data"]["evaViewList"]
        except Exception as e:
            print("   ! Bewertungs-API:", e)
            break
        if not reviews:
            break
        for rv in reviews:
            imgs = rv.get("images") or []
            rows.append({
                "datum": rv.get("evalDate"), "land": rv.get("buyerCountry"), "sterne": rv.get("buyerEval"),
                "text": rv.get("buyerTranslationFeedback") or rv.get("buyerFeedback"),
                "variante": rv.get("skuInfo"), "bilder": " ".join(imgs),
            })
            for img in imgs:
                download(img, ROOT / "02_Bewertungen" / name)
    if rows:
        out = ROOT / "07_Texte" / f"{name}_bewertungen.csv"
        out.parent.mkdir(exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"   + {out.relative_to(ROOT)} ({len(rows)} Bewertungen)")


def meta_ads(browser):
    for q in QUELLEN["meta_ad_library_suchbegriffe"]:
        print(f"\n== Meta-Werbebibliothek: {q}")
        folder = ROOT / "03_Ads" / slug(q)
        page = new_page(browser)
        media: set[str] = set()
        page.on("response", lambda r: media.add(r.url) if ".mp4" in r.url else None)
        url = ("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL"
               f"&media_type=all&search_type=keyword_unordered&q={quote(q)}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            time.sleep(5)
            accept_cookies(page)
            scroll_through(page, 40)
            screenshot(page, folder, "uebersicht")
            media |= set(page.evaluate(
                "() => [...document.querySelectorAll('video')].map(v => v.src || v.querySelector('source')?.src).filter(Boolean)"))
            media |= {u for u in page.evaluate(
                "() => [...document.querySelectorAll('img')].filter(i => i.naturalWidth >= 400).map(i => i.src)")}
        except Exception as e:
            print("   !", e)
        for u in sorted(media):
            download(u, folder)
        page.context.close()


def ytdlp(urls, folder: Path, extra):
    folder.mkdir(parents=True, exist_ok=True)
    for u in urls:
        if not u:
            continue
        print(f"\n== yt-dlp: {u}")
        subprocess.run([
            sys.executable, "-m", "yt_dlp", u, *extra,
            "--playlist-end", "60", "--write-info-json", "--write-thumbnail", "--no-overwrites",
            "-f", "bv*+ba/b", "--merge-output-format", "mp4",
            "-o", str(folder / "%(uploader|unbekannt)s_%(id)s.%(ext)s"),
        ])


def main():
    args = sys.argv[1:]
    extra = []
    if "--cookies-from-browser" in args:
        i = args.index("--cookies-from-browser")
        extra = args[i:i + 2]
        del args[i:i + 2]
    parts = set(args) or {"shops", "seiten", "aliexpress", "ads", "tiktok", "instagram"}

    with sync_playwright() as pw:
        # PW_CHROMIUM: optional eigener Chromium-Pfad, falls "playwright install" nicht geht
        browser = pw.chromium.launch(headless=True, executable_path=os.environ.get("PW_CHROMIUM") or None)
        if "shops" in parts:
            shopify_shops(browser)
        if "seiten" in parts:
            andere_seiten(browser)
        if "aliexpress" in parts:
            aliexpress(browser)
        if "ads" in parts:
            meta_ads(browser)
        browser.close()
    if "tiktok" in parts:
        ytdlp(QUELLEN["tiktok"], ROOT / "04_TikTok", extra)
    if "instagram" in parts:
        ytdlp(QUELLEN["instagram"], ROOT / "05_Instagram", extra)
    print("\nFertig. Ergebnisse liegen in", ROOT)


if __name__ == "__main__":
    main()
