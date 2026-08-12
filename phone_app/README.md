# Pocket Technician Phone App

Production-oriented Flutter mobile implementation of the existing Streamlit Pocket Technician application.

## Architecture

The app is contained entirely in `phone_app/` and follows feature-first organization with shared `core/` services, repositories, models, storage, routing, theme, network, and errors. Business rules are isolated in service classes, especially `lib/core/services/aquaculture_calculator.dart`, so widgets do not own aquaculture formulas.

## Existing Streamlit parity

Source Streamlit entry point: `../Pocket-Technician.py`. Supporting pages: `../pages/Feed_Tray_AI.py`, `../pages/Virtual_Farm.py`, and `../pages/Shrimp_Larvae_Detection.py`. Local persistence source: `../supabase_backend.py` with SQLite/JSON payloads.

Mapped workflows:

- Farm/pond setup, pond area/depth/stocking date and local memory.
- Sampling formulas: DOC, ABW, survival, present numbers, biomass, weekly growth, ADG, biomass gain, survival change, FCR, excess-feed warnings.
- Feeding chart: 1 kg per 10,000 shrimp plus 250 g/day pre-sampling, survival adjustment, weather adjustment, feed size, carrying capacity, profit estimate.
- Feed tray rules: ABW categories, tray leftover reductions/increases, strong response increase.
- Weather/lunar: Nominatim/Open-Meteo boundaries and deterministic lunar phase calculation.
- Reports/exports: PDF/CSV architecture using stored data.
- Larvae detection: Roboflow service boundary; API key must come from secure configuration.
- Virtual farm: DEB-inspired biomass/feed/survival/profit projections.
- Multi-pond ranking formula and grade bands.

## Local database schema

Isar is the primary store; Hive is reserved for secondary API/cache snapshots; secure storage is used for credentials/session tokens; shared preferences are used for lightweight preferences and last-viewed context.

Domain entities: Farmer, Farm, Pond, PondGeometry, SamplingRecord, FeedRecord, FeedRecommendation, FeedTrayRecord, WaterQualityRecord, WeatherRecord, DiseaseRecord, VirtualFarmScenario, Report, LarvaeDetection, UserPreferences, and AppContext.

## Configuration

Do not commit secrets. Configure optional integrations with platform environment/secure storage:

- `ROBOFLOW_API_KEY` for larvae detection.
- SMS/OTP provider credentials for production OTP delivery.
- Google Maps Android/iOS keys in native platform configuration.

When credentials are missing, services return explicit configuration errors rather than fake success.

## Offline behavior

Farm management, ponds, sampling, feed calculations, historical analytics, water quality, disease logs, reports, CSV exports, virtual farm calculations, and app context are local-first. Weather/geocoding, WhatsApp, Roboflow, and future cloud sync require network and degrade gracefully using cached/local state.

## Build and test

```bash
cd phone_app
flutter pub get
flutter analyze
flutter test
flutter build apk
```

The current container used for this migration does not include the Flutter SDK, so validation must be run in a Flutter 3.29+/Dart 3.8+ environment.

## Sampling calculation source

The sampling calculation is implemented in `lib/core/services/aquaculture_calculator.dart` (`AquacultureCalculator.sampling`) and is persisted from `lib/services/local_database.dart` (`LocalDatabase.addSamplingLog`). The Sampling tab in `lib/screens/technician_modules_screen.dart` only collects inputs; it does not own the formula.

For a clear list of mobile-vs-Streamlit differences, see `docs/FLUTTER_DIFFERENCES.md`.

## Aquaculture Expert Intelligence

The condition-rule-based Expert AI is integrated into the existing Pocket Technician Flutter app, not built as a separate application. It uses local farm, pond, feed, sampling, water-quality, weather-ready, and domain-calculated metrics to create explainable assessments. See `docs/EXPERT_AI.md` for the rule engine, context, persistence, UI integration, and safety model.
