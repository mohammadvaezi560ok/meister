#!/usr/bin/env python3
"""Meta-Werbebibliothek: Kniekissen-Ads der Konkurrenz laden (Video in HD, Bilder in Originalgröße).

Ablauf
  1. Jede Suche/Seite aus quellen.json ("meta_ads") wird ohne Login geöffnet. Ohne Login
     liefert die Bibliothek pro Abfrage nur 30 Ads und lädt beim Scrollen nichts nach –
     deshalb wird jede Abfrage in Varianten zerlegt (Bild/Video × aktiv/inaktiv ×
     Sortierung), das ergibt deutlich mehr verschiedene Ads.
  2. Nur Ads, deren Text zum Kniekissen passt (Knie, Hüfte, Seitenschläfer …), werden
     behalten – andere Produkte derselben Advertiser (128-Hz-Stimmgabel, Tinnitus,
     Schnarchkissen …) fliegen raus.
  3. Medien landen nach Format sortiert in 04_Ads/video/ (mp4 + Vorschaubild) bzw.
     04_Ads/bild/ als <shop>__<library-id>[_n].<endung>; Texte, Links und Laufzeiten
     in 04_Ads/ads.csv.

Start: python3 Research/tools/meta_ads.py
"""
import csv
import hashlib
import json
import re
import sys
import io
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ZIEL = ROOT / "04_Ads"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
PASST = re.compile(r"knee|knie|kolan|hip pain|hüft|side sleep|seitenschl|leg pillow|beinkissen|alignment pillow|ischias|sciatica", re.I)
FREMD = re.compile(r"128 ?hz|tinnitus|ringing|hearing|sinus|snor|chrap|stimmgabel|tuning fork|nacken|neck|sitzkissen|seat cushion|sittkudde|sittdyna", re.I)
# Advertiser-Seite -> Shop-Kürzel im Dateinamen (Nourial schaltet über mehrere "Journal"-Seiten)
SHOP = {"nourial.com": "nourial", "try.nourial.com": "nourial", "nordyckikomfort.com": "nordyckikomfort",
        "cellsius-germany.com": "cellsius"}


def varianten(url: str) -> list[str]:
    teile = urlsplit(url)
    basis = {k: v for k, v in parse_qsl(teile.query) if not k.startswith("sort_data")}
    out = []
    for medium in ("image", "video"):
        for status in ("active", "inactive"):
            for sortierung in ({}, {"sort_data[mode]": "relevancy_monthly_grouped", "sort_data[direction]": "desc"}):
                q = dict(basis, media_type=medium, active_status=status, **sortierung)
                out.append(urlunsplit(teile._replace(query=urlencode(q))))
    return out


def seite_laden(url: str, scrolls: int) -> list[str]:
    from playwright.sync_api import sync_playwright
    bodies = []
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:  # Cloud-Container: vorinstalliertes Chromium
            b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_context(user_agent=UA, locale="en-US", viewport={"width": 1440, "height": 900}).new_page()

        def on_resp(r):
            if "graphql" in r.url:
                try:
                    bodies.append(r.text())
                except Exception:
                    pass
        pg.on("response", on_resp)
        pg.goto(url, wait_until="domcontentloaded", timeout=90_000)
        pg.wait_for_timeout(8000)
        bodies.append(pg.content())
        for _ in range(scrolls):
            pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pg.wait_for_timeout(1500)
        b.close()
    return bodies


def ads_finden(bodies: list[str], gefunden: dict):
    def walk(o):
        if isinstance(o, dict):
            if "ad_archive_id" in o and "snapshot" in o:
                gefunden[o["ad_archive_id"]] = o
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for t in bodies:
        chunks = re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', t, re.S) or t.splitlines()
        for c in chunks:
            c = c.strip()
            if c.startswith("{"):
                try:
                    walk(json.loads(c))
                except Exception:
                    pass


def medien(s: dict) -> list[tuple[str, str]]:
    out = []
    for q in (s.get("videos") or []) + (s.get("cards") or []):
        if q.get("video_hd_url") or q.get("video_sd_url"):
            out.append(("mp4", q.get("video_hd_url") or q["video_sd_url"]))
            if q.get("video_preview_image_url"):
                out.append(("jpg", q["video_preview_image_url"]))
        elif q.get("original_image_url") or q.get("resized_image_url"):
            out.append(("jpg", q.get("original_image_url") or q["resized_image_url"]))
    for q in s.get("images") or []:
        if q.get("original_image_url") or q.get("resized_image_url"):
            out.append(("jpg", q.get("original_image_url") or q["resized_image_url"]))
    return list(dict.fromkeys(out))


def text_von(s: dict) -> str:
    body = s.get("body")
    body = body.get("text") if isinstance(body, dict) else body
    teile = [body, s.get("title"), s.get("link_description"), s.get("caption")]
    teile += [c.get("body") for c in s.get("cards") or []]
    return " ".join(str(t) for t in teile if t)


def datum(ts) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else ""


def main():
    q = json.loads((Path(__file__).with_name("quellen.json")).read_text())
    gefunden = {}
    for e in q["meta_ads"]:
        print(f"== {e.get('_name', e['url'])}")
        for url in varianten(e["url"]):
            try:
                ads_finden(seite_laden(url, e.get("scrolls", 3)), gefunden)
            except Exception as ex:
                print(f"   ! {ex}")
        print(f"   bisher {len(gefunden)} Ads")

    ZIEL.mkdir(parents=True, exist_ok=True)
    gesehen = {hashlib.sha1(f.read_bytes()).hexdigest() for f in ZIEL.rglob("*.*") if f.suffix != ".csv"}
    zeilen = []
    for aid, o in gefunden.items():
        s = o["snapshot"]
        text, link = text_von(s), s.get("link_url") or ""
        host = re.sub(r"^https?://(www\.)?", "", link).split("/")[0]
        if host not in SHOP or not PASST.search(text) or FREMD.search(text + " " + link):
            continue
        dateien = []
        format_ = "video" if any(e == "mp4" for e, _ in medien(s)) else "bild"
        (ZIEL / format_).mkdir(exist_ok=True)
        for n, (endung, url) in enumerate(medien(s)):
            try:
                daten = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120).read()
            except Exception as ex:
                print(f"   ! {aid}: {ex}")
                continue
            h = hashlib.sha1(daten).hexdigest()
            if h in gesehen:
                continue
            gesehen.add(h)
            if endung != "mp4":
                try:
                    endung = Image.open(io.BytesIO(daten)).format.lower().replace("jpeg", "jpg")
                except Exception:
                    continue
            name = f"{format_}/{SHOP[host]}__{aid}{'_' + str(n) if n else ''}.{endung}"
            (ZIEL / name).write_bytes(daten)
            dateien.append(name)
        zeilen.append({"shop": SHOP[host], "library_id": aid, "advertiser": s.get("page_name") or o.get("page_name"),
                       "format": format_, "aktiv": o.get("is_active"), "start": datum(o.get("start_date")), "ende": datum(o.get("end_date")),
                       "link": link.split("?")[0], "dateien": " ".join(dateien),
                       "ad_link": f"https://www.facebook.com/ads/library/?id={aid}", "text": text.replace("\n", " ")})
        print(f"   + {aid} {SHOP[host]} {len(dateien)} Datei(en)")

    csv_pfad = ZIEL / "ads.csv"
    alt = list(csv.DictReader(csv_pfad.open())) if csv_pfad.exists() else []
    neu = {z["library_id"]: z for z in alt + zeilen}
    with csv_pfad.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(zeilen[0] if zeilen else alt[0]))
        w.writeheader()
        w.writerows(sorted(neu.values(), key=lambda z: (z["shop"], z["start"]), reverse=True))
    print(f"\n{len(zeilen)} passende Ads, Übersicht: {csv_pfad}")


if __name__ == "__main__":
    sys.exit(main())
