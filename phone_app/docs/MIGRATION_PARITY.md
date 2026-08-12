# Migration and parity audit

## Streamlit architecture discovered

- `Pocket-Technician.py` is the Streamlit entry point and contains setup, persistence loading/saving, sampling, feeding, weather/lunar, charts, PDF reporting, and multi-pond comparison.
- `supabase_backend.py` currently provides a single local identity and SQLite/JSON storage; despite its name, active cloud auth is removed.
- `pages/Feed_Tray_AI.py` contains feed-tray projection tables and PDF export.
- `pages/Virtual_Farm.py` contains DEB-style projections, economic summaries, charts, and PDF persistence.
- `pages/Shrimp_Larvae_Detection.py` integrates Roboflow, OpenCV preprocessing, duplicate merging, image/video processing, and learning logs.

## Ported business rules

- DOC = sampling date - stocking date + 1.
- ABW = 1000 / nearest count slab.
- Survival is feed-chart derived from daily feed and reference feed per 100k.
- Biomass = present numbers × ABW / 1000.
- Weekly metrics derive from previous sampling and interval feed records.
- Feed tray ABW/check-time categories and leftover response rules.
- Weather feed factors: >34°C = 0.85, <26°C = 0.75, rain >20 mm = 0.80.
- Feed size by DOC and pre-sampling feed chart progression.
- Carrying capacity/profit estimates.
- Virtual farm biomass/revenue/feed cost/profit/projection outputs.
- Multi-pond ranking score and A/B/C grading.

## Mobile adaptations

- WhatsApp assistance replaces email-first support for the farmer mobile UX and requires confirmation before opening the deep link.
- OTP is abstracted behind a provider interface; no fake production OTP is embedded.
- Roboflow credentials are no longer hardcoded and must be supplied by secure configuration.
- Isar/Hive/Secure Storage/Shared Preferences are the planned storage layers for production Flutter.

## Known validation limitation

The implementation was authored in a container without the `flutter` executable. Dependency resolution, analyzer, tests, and Android build must be run where Flutter 3.29+ is installed.
