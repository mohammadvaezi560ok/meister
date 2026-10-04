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

Bewertungs-Section mit Sternen, automatisch berechnetem Durchschnitt und Bewertungskarten (Desktop: 3 Spalten, Handy: wischbar). Farben passend zur Vergleichstabelle.

- `sections/reviews.liquid` – die Section; jede Bewertung ist ein Block (Sterne, Text, optional Name)
- `templates/product.bein-kissen.json` – enthält die 10 Bewertungen, direkt unter dem Produkt

### Manuell einbauen
1. Unter `sections` → **Neue Section hinzufügen** → Name `reviews` → Inhalt aus `sections/reviews.liquid` einfügen → Speichern
2. `templates/product.bein-kissen.json` durch die Datei aus diesem Repo ersetzen → Speichern

Neue Bewertungen fügst du im Theme-Editor über **Block hinzufügen → Bewertung** hinzu.
