# Modava – Shopify-Theme-Anpassungen (Sense)

## Vergleichstabelle (Kniekissen / „Bein Kissen“)

Nachbau der Vergleichstabelle von histrips.com („Built for real recovery.“) als Shopify-Section.

- `sections/comparison-table.liquid` – die Section (alle Texte, Bilder, Farben im Theme-Editor änderbar)
- `templates/product.bein-kissen.json` – Produktvorlage des Kniekissens, mit der Tabelle ganz unten

### Manuell einbauen
1. Shopify-Admin → Onlineshop → Themes → Sense → „…“ → **Code bearbeiten**
2. Unter `sections` → **Neue Section hinzufügen** → Name `comparison-table` → Inhalt aus `sections/comparison-table.liquid` einfügen → Speichern
3. `templates/product.bein-kissen.json` öffnen und durch die Datei aus diesem Repo ersetzen → Speichern

## Kundenbewertungen (Social Proof)

Die Bewertungen nutzen die Shop-eigene Section `mv-reviews` aus dem Live-Theme („Modava – Bewertungen v6“). Sie hat also dieselbe Schrift (Poppins, fette Großbuchstaben-Überschrift), dasselbe Navy `#0d1b4f`, goldene Sterne `#f5b400` und denselben Slider wie die übrigen Modava-Sections.

- `sections/mv-reviews.liquid` – Bewertungs-Section (unverändert aus dem Live-Theme)
- `snippets/mv-slider-script.liquid` – Slider-Logik (unverändert aus dem Live-Theme)
- `templates/product.bein-kissen.json` – Produktvorlage aus dem Live-Theme, mit den 10 Bewertungen (Section eingeschaltet, Ø 4,8 / 5) und der Zeile „4,8 / 5 · 10 Bewertungen“ über dem Produkttitel

### Einbauen
Die Section und das Snippet sind im Live-Theme schon vorhanden. Es reicht:
1. Shopify-Admin → Onlineshop → Themes → aktives Theme duplizieren → beim Duplikat „…“ → **Code bearbeiten**
2. `templates/product.bein-kissen.json` öffnen, Inhalt durch die Datei aus diesem Repo ersetzen → Speichern
3. Vorschau prüfen, dann veröffentlichen

Neue Bewertungen fügst du im Theme-Editor in der Section „Bewertungen (Modava)“ über **Bewertung hinzufügen** hinzu. Die Gesamtnote („4,8 / 5“) und die Zeile über dem Titel bitte dann von Hand anpassen.
