# Modava – Shopify-Theme-Anpassungen (Sense)

## Vergleichstabelle (Kniekissen / „Bein Kissen“)

Nachbau der Vergleichstabelle von histrips.com („Built for real recovery.“) als Shopify-Section.

- `sections/comparison-table.liquid` – die Section (alle Texte, Bilder, Farben im Theme-Editor änderbar)
- `templates/product.bein-kissen.json` – Produktvorlage des Kniekissens, mit der Tabelle ganz unten

### Manuell einbauen
1. Shopify-Admin → Onlineshop → Themes → Sense → „…“ → **Code bearbeiten**
2. Unter `sections` → **Neue Section hinzufügen** → Name `comparison-table` → Inhalt aus `sections/comparison-table.liquid` einfügen → Speichern
3. `templates/product.bein-kissen.json` öffnen und durch die Datei aus diesem Repo ersetzen → Speichern
