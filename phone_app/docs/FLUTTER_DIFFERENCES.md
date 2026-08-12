# What is different in the Flutter app

This document lists intentional differences between the existing Streamlit application and the Flutter mobile implementation.

## Sampling calculation location

Sampling is not calculated inside a widget. It is implemented in:

- `lib/core/services/aquaculture_calculator.dart` in `AquacultureCalculator.sampling(...)`.
- `lib/services/local_database.dart` in `LocalDatabase.addSamplingLog(...)`, which calls `AquacultureCalculator.sampling(...)` and persists the result.
- `lib/screens/technician_modules_screen.dart` in the Sampling tab, where the user enters count per kg and daily feed, then taps **Run and save sampling**.

The calculation stores DOC, count slab, ABW, present numbers, survival percentage, biomass, feed percentage, possible excess feed, weekly growth, weekly ADG, weekly biomass, and weekly FCR.

## Functional differences from Streamlit

| Area | Streamlit behavior | Flutter mobile behavior | Reason |
| --- | --- | --- | --- |
| Runtime | Python Streamlit web app | Flutter mobile app under `phone_app/` | Mobile deployment requirement |
| Storage | Local SQLite/JSON payload through `supabase_backend.py` | Local mobile database service; `pubspec.yaml` includes Isar/Hive/Secure Storage/Shared Preferences | Mobile offline-first persistence and future sync readiness |
| Sampling UI | Streamlit form calculates preview and then saves pending sampling | Mobile Sampling tab saves calculated sampling directly through repository/service | Mobile flow reduces accidental unsaved state; formulas are the same service-level formulas |
| OTP/auth | Existing Streamlit currently uses a single local identity with no cloud login | Mobile has phone/OTP service abstraction | Required mobile UX; production SMS provider must be configured |
| Support | Streamlit support can send email through SMTP secrets | Mobile requirement is WhatsApp deep-link assistance with confirmation | Farmer-first mobile contact flow |
| Roboflow key | Streamlit page contains an environment fallback and an insecure hardcoded default | Flutter documentation requires secure configuration and explicit missing-config errors | Mobile security requirement; no committed API secrets |
| Maps | Streamlit uses form/layout concepts, not native mobile satellite map editing | Flutter dependency stack includes Google Maps and persisted pond geometry architecture | Native map keys are platform configured; no key committed |
| Reports | Streamlit writes PDF files with ReportLab/Matplotlib | Flutter stack uses `pdf`, `printing`, and CSV packages against local records | Native mobile share/print/export behavior |
| Charts | Streamlit uses Matplotlib | Flutter uses FL Chart/Syncfusion dependency stack | Native mobile rendering |
| Weather | Streamlit calls Nominatim/Open-Meteo directly in UI function | Flutter plans network service boundary and cached/local degradation | Offline-first architecture and error isolation |

## Not considered a difference

The following formulas are intentionally preserved from Streamlit:

- `DOC = sampling date - stocking date + 1`.
- `ABW = 1000 / nearest count slab`.
- Feed-chart survival derived from daily feed and feed per 100k.
- `Biomass = present numbers × ABW / 1000`.
- Weekly growth, ADG, biomass change, survival change, and FCR from the previous sampling interval.
- Feed tray ABW categories and leftover/consumption-time decisions.
- Weather feed reduction factors.
- Multi-pond ranking score and A/B/C grade bands.
