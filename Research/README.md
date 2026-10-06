# Research – Kniekissen / Leg Alignment Pillow (Modava)

Content-Sammlung zu genau diesem Produkt: das Kniekissen in Sanduhr-Form für Seitenschläfer, mit Memory-Foam und Klettriemen am Bein. Die Bilder und Videos stammen von Konkurrenten, Ads und Social Media.

## Ordner (nach Inhalt sortiert, nicht nach Shop)

| Ordner | Inhalt |
|---|---|
| `01_Produktbilder/` | Galerie- und Detailbilder in Originalauflösung |
| `02_Bewertungen/` | Kundenfotos aus den Bewertungs-Widgets (Loox, Judge.me, AliExpress, …) |
| `03_Videos/` | TikTok-, Instagram- und YouTube-Videos sowie Shop-Videos (mp4) |
| `04_Ads/` | Werbemittel aus der Meta-Werbebibliothek (Bild und Video) |
| `05_Screenshots/` | Full-Page-Screenshots der Konkurrenz-Seiten |
| `06_Landingpages/` | Bilder aus Advertorials und Landingpages (z. B. nourial `adv-alignment-pillow-v4`) |

Der Dateiname beginnt immer mit dem Shop, z. B. `nourial__004.jpg`. So bleibt die Herkunft auch nach dem Sortieren sichtbar.

## Konkurrenten und Quellen

| Shop | Link | Hinweis |
|---|---|---|
| **Nourial** (Hauptkonkurrent) | [Produktseite](https://nourial.com/products/nourial-leg-alignment-pillow) | 4,92 ★ aus 787 Bewertungen, ca. 36 $, 60 Tage Geld-zurück |
| Nourial Advertorial | [adv-alignment-pillow-v4](https://nourial.com/pages/adv-alignment-pillow-v4) | Landingpage für die Ads |
| Nourial Bewertungsseite | [nourialpillow.com/customer-reviews](https://nourialpillow.com/customer-reviews/) | |
| AliExpress (Lieferant) | [Artikel 1005008280256176](https://de.aliexpress.com/item/1005008280256176.html) | Lieferant mit Kundenfotos |
| Aflorest | [Produktseite](https://aflorest.com/products/nourial-leg-alignment-pillow-feel-the-deep-relief-from-your-first-night) | verkauft dasselbe Produkt |
| Husband Pillow | [Leg & Knee Spacer mit Riemen](https://www.husbandpillow.com/products/leg-and-knee-spacer-memory-foam-pillow-with-strap-eye-mask) | |
| Walmart | [Listing](https://www.walmart.com/ip/19299555264) · [Bewertungen](https://www.walmart.com/reviews/product/3104489985) | |
| Amazon | [UJPFEO](https://www.amazon.com/clp/B0DQP19KN2) · [DailyCuddles](https://www.amazon.com/clp/B0G5ZGPB65) · [LVOPO](https://www.amazon.com/clp/B08P6N3DKJ) | Varianten mit Riemen |
| YouTube-Reviews | [Nourial EXPOSED](https://www.youtube.com/watch?v=fZWqiDSL2AA) · [Worth $36?](https://www.youtube.com/watch?v=5uWVm4kKriA) | |
| Meta-Werbebibliothek | [Suche „nourial“](https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&q=nourial&search_type=keyword_unordered) · [„kniekissen“ DE](https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DE&q=kniekissen&search_type=keyword_unordered) | |

## Automatisch befüllen

`tools/download.py` geht jede Seite aus `tools/quellen.json` durch. Es macht einen Screenshot, scrollt die Bewertungen nach, lädt alle Bilder in Originalgröße und sortiert sie in die Ordner oben. Duplikate und Icons werden aussortiert. Videos lädt es mit yt-dlp in bester Qualität.

```bash
pip install playwright yt-dlp pillow
playwright install chromium
python3 Research/tools/download.py
```

Für neue Shops, TikTok- oder Instagram-Links ergänzt man einfach `tools/quellen.json` (`seiten` bzw. `videos`) und startet das Skript erneut. Bereits geladene Dateien werden nicht doppelt gespeichert.
