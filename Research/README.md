# Research – Kniekissen (Leg Alignment Pillow)

Konkurrenz-Material zum Kniekissen von modava.de: das Sanduhr-Kissen aus Memory-Schaum mit Gurt für Seitenschläfer.
Referenzprodukt: [Nourial Leg Alignment Pillow](https://nourial.com/products/nourial-leg-alignment-pillow), AliExpress-Quelle [1005008280256176](https://de.aliexpress.com/item/1005008280256176.html).

## Ordner

| Ordner | Inhalt |
|---|---|
| `01_Produktbilder/<Shop>/` | Alle Produktbilder in Originalgröße, je Shop |
| `02_Bewertungen/<Shop>/` | Kundenfotos aus den Bewertungen (Judge.me, Loox, Okendo, Yotpo, AliExpress …) |
| `03_Ads/<Suchbegriff>/` | Videos und Bilder aus der Meta-Werbebibliothek (Facebook/Instagram-Ads) |
| `04_TikTok/` | TikTok-Videos (mp4) + Infos (Likes, Beschreibung) als `.info.json` |
| `05_Instagram/` | Instagram-Reels und -Posts |
| `06_Screenshots/<Shop>/` | Ganzseiten-Screenshots der Produktseiten (oben + komplett) |
| `07_Texte/` | Produkttexte der Konkurrenz + AliExpress-Bewertungen als CSV |
| `08_Sortiert/` | Zweiter Schritt: alles nach Verwendung sortiert, egal aus welchem Shop |

`08_Sortiert/` ist unterteilt in: Freisteller (weißer Hintergrund), Lifestyle im Bett, Infografiken/Vorteile,
Details/Nahaufnahmen, Vorher/Nachher (Haltung), Kundenfotos (UGC), Videos UGC, Videos Ads.

## Automatisch befüllen

Das Skript `tools/download_research.py` holt alles aus den Quellen in `tools/quellen.json`:

```bash
pip install playwright requests yt-dlp gallery-dl
playwright install chromium
python3 Research/tools/download_research.py                 # alles
python3 Research/tools/download_research.py shops ads       # nur Teile
# Teile: shops, seiten, aliexpress, ads, tiktok, instagram
# Instagram (und manchmal TikTok) braucht einen Login im Browser:
python3 Research/tools/download_research.py instagram --cookies-from-browser chrome
```

- **Shopify-Shops**: Bilder kommen über `<produkt-url>.json` direkt in Originalauflösung, ohne Shopify-Verkleinerung.
- **Bewertungsbilder**: Das Skript scrollt die Seite durch und klickt „Mehr Bewertungen“, auch im Loox-Iframe. Dann lädt es die Kundenfotos in voller Größe (ohne `?w=`-Verkleinerung).
- **AliExpress**: Produktbilder ohne `_640x640`-Endung, also in Originalgröße. Bewertungsfotos und Texte kommen über die Feedback-Schnittstelle (bis zu 1.500 Bewertungen).
- **Ads**: Die Meta-Werbebibliothek wird pro Suchbegriff durchgescrollt. Alle Videos (mp4) und großen Bilder werden geladen.
- **TikTok/Instagram**: yt-dlp lädt bis zu 60 Videos pro Hashtag oder Profil, in bester Qualität und ohne Wasserzeichen, soweit verfügbar.
- Doppelte Dateien werden automatisch übersprungen (Vergleich per Hash).

Neue Quellen einfach in `tools/quellen.json` eintragen: weitere Shops, konkrete TikTok-Video-Links oder Profile wie `https://www.tiktok.com/@nourial`.

## Konkurrenten (gleiches oder sehr ähnliches Produkt)

| Anbieter | Link | Notiz |
|---|---|---|
| Nourial | https://nourial.com/products/nourial-leg-alignment-pillow | Top-Konkurrent, Sanduhrform + Gurt |
| AliExpress-Lieferant | https://de.aliexpress.com/item/1005008280256176.html | gleiches Produkt, Bewertungsfotos |
| Revoget | https://shopitor.onshopbase.com/products/revoget-alignment-pillows-relieve-hip-pain-sciatica-leg-alignment-pillow-for-side-sleepers-sleep-pain-free-from-hip-back-aches | „Alignment Pillow“, gleiche Positionierung |
| „The Sciatica Pillow“ | (Direct-Response-Marke, viele Advertorials) | gleiche Story: Bein fällt nach vorn → Hüfte verdreht |
| GDSAFS (Amazon) | https://www.amazon.com/GDSAFS-Leg-Alignment-Pillow-Sciatica/dp/B0D4QWVS1C | „Leg Alignment Pillow“ mit Gurt |
| Hip Alignment Pillow (Amazon) | https://www.amazon.com/Hip-Alignment-Pillow-Side-Sleepers/dp/B0F8J9F3HT | |
| KOKIXEOT (Amazon) | https://www.amazon.com/clp/B0F99HXB8L | Gurt + Ersatzbezug |
| Cushion Lab | https://thecushionlab.com/products/cushion-lab-extra-dense-knee-pillow | Premium-Shopify-Shop, gute Lifestyle-Bilder |
| Husband Pillow | https://www.husbandpillow.com/products/leg-and-knee-spacer-memory-foam-pillow-with-strap-eye-mask | Shopify, Kissen mit Gurt |
| Kaufland DE (EBRAN, MediSleep, Retoo, WohnEleganz) | kaufland.de/product/569568111, /368020070, /499464361 | deutsche Bewertungen |
| eBay DE / Nexusectar / NASSMOSSE / Restform | Markennamen aus der DE-Suche | deutsche Wettbewerber |
