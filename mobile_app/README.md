# Pocket Technician Mobile

This folder contains a Flutter-first mobile rewrite of the Streamlit Pocket Technician app.

## Stack

- Flutter Material 3 for Android/iOS UI
- Riverpod for app state
- GoRouter for mobile navigation
- Sqflite for fully local on-device data storage
- fl_chart for analytics visuals

## Core changes from Streamlit

- Supabase is removed from the mobile workflow.
- Login uses a phone-number OTP service abstraction. The current local build generates an OTP on device and shows it in debug mode; connect an SMS provider in `OtpService.sendOtp` for production delivery.
- CEO dashboard summarizes farmers, farms, ponds, biomass, survival, and risk status from the local database.
- Technician modules cover farm setup, feed logs, sampling/growth analytics, water quality, feed tray decisions, profit/carrying-capacity checks, virtual farm summaries, and local reports.
- Farm pages use a tappable and draggable pond layout canvas instead of slider-based pond switching. Each pond stores layout coordinates and opens its own details screen from the map.
- Pond reports are generated as local on-device records, keeping farmer reports on the phone rather than in Supabase/cloud storage.

## Run

```bash
cd mobile_app
flutter pub get
flutter run
```

## Production notes

- Replace the debug OTP display with an SMS gateway call in `lib/services/otp_service.dart`.
- Add platform icons/splash screens and platform-specific Android/iOS signing before release.
- Optional sync can be added later without changing the local-first data model.
