# Modava – Shopify-Theme-Anpassungen (Sense)

## Vergleichstabelle (Kniekissen / „Bein Kissen“)

Nachbau der Vergleichstabelle von histrips.com („Built for real recovery.“) als Shopify-Section.

- `sections/comparison-table.liquid` – die Section (alle Texte, Bilder, Farben im Theme-Editor änderbar)
- `templates/product.bein-kissen.json` – Produktvorlage des Kniekissens, mit der Tabelle ganz unten

### Manuell einbauen
1. Shopify-Admin → Onlineshop → Themes → Sense → „…“ → **Code bearbeiten**
2. Unter `sections` → **Neue Section hinzufügen** → Name `comparison-table` → Inhalt aus `sections/comparison-table.liquid` einfügen → Speichern
3. `templates/product.bein-kissen.json` öffnen und durch die Datei aus diesem Repo ersetzen → Speichern

## Kniekissen-Shop im „Nourial“-Stil (Navy)

Kompletter Neuaufbau von Startseite und Produktseite rund um das ergonomische Kniekissen.

| Datei | Inhalt |
|---|---|
| `sections/mv-image-banner.liquid` | Vollbild-Banner mit Bild, Abdunklung, Text und Button (Hero + „Unsere Mission“) |
| `sections/mv-features.liquid` | „Was uns anders macht“ – Karten-Slider mit Icons, Pfeilen und Punkten |
| `sections/mv-product.liquid` | Produktbereich: Galerie + Thumbnails, Vorteile-Liste, Mengen-Angebote (1/2/3 Kissen) mit Farbwahl pro Kissen |
| `sections/mv-reviews.liquid` | Kundenbewertungen (standardmäßig ausgeblendet – nur mit echten Bewertungen füllen) |
| `sections/mv-faq.liquid` | Häufige Fragen |
| `snippets/mv-icon.liquid` | Linien-Icons für die Sections |
| `templates/index.json` | Startseite |
| `templates/product.bein-kissen.json` | Produktvorlage des Kniekissens |
| `sections/header-group.json`, `sections/footer-group.json`, `config/settings_data.json` | Ankündigungsleiste, Header, Footer, Navy-Farbschema |

### Mengenrabatt
Die Rabatte der Angebote (2 Kissen −20 %, 3 Kissen −30 %) werden nur angezeigt.
Abgezogen werden sie an der Kasse durch zwei automatische Rabatte in Shopify
(Rabatte → „Doppelpack −20 %“ und „Familienpaket −30 %“). Werden Prozentsätze
geändert, müssen Section-Einstellung **und** automatischer Rabatt angepasst werden.

### Update: Handy-Optimierung & neue Produktseiten-Bereiche

| Datei | Inhalt |
|---|---|
| `sections/mv-image-text.liquid` | Abwechselnde Bild/Video-Text-Zeilen („Entlastung ab der ersten Nacht“ …), Videos laufen stumm in Schleife |
| `sections/mv-relief-cards.liquid` + `snippets/mv-illustration.liquid` | „Gezielte Entlastung für Seitenschläfer“ – Karten-Slider mit Anatomie-Zeichnungen |
| `sections/mv-marquee.liquid` | Laufband mit Vorteilen (Startseite, unter dem Hero) |
| `snippets/mv-slider-script.liquid` | Gemeinsame Slider-Logik (Wischen, Pfeile, Punkte) |
| `sections/mv-reviews.liquid` | jetzt als Slider – nur mit echten Bewertungen einschalten |
| `sections/mv-product.liquid` | feste Kaufleiste unten + Handy-Feinschliff (u. a. 16px-Auswahlfelder gegen iPhone-Zoom) |
