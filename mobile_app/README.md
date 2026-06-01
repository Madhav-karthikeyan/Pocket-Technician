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
- Farm pages use a tappable pond layout canvas instead of slider-based pond switching. Each pond stores layout coordinates and opens its own details screen from the map.

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

## Desktop preview / database initialization

The app initializes `sqflite_common_ffi` automatically on Linux, macOS, and Windows so CEO dashboard metrics and farmer lists also work during desktop Flutter preview runs. Android and iOS continue to use the normal `sqflite` mobile database factory.

## Original Streamlit feature coverage in Flutter

Use **CEO Command Center → Open technician modules** to access the mobile equivalents of the original app workflows:

- Farm / pond setup with local persistence
- Daily feed entry
- Sampling, ABW, survival, biomass, and feed-percent logic
- Water-quality logging and risk thresholds
- Feed tray decision support
- Profit and carrying-capacity summary
- Virtual farm projection summary
- Report, farm-comparison, Feed Tray AI, larvae-detection, weather, and lunar integration hooks
