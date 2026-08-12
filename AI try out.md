# AI Try Out — Condition-Based Aquaculture Expert Intelligence

This specification is now represented in the Flutter app as an integrated expert-intelligence layer, not as a separate AI application.

Implementation entry points:

- `phone_app/lib/core/expert/expert_engine.dart` — deterministic condition/rule/risk/recommendation/explanation engine.
- `phone_app/lib/services/providers.dart` — builds expert context from real pond detail records and exposes dashboard/pond providers.
- `phone_app/lib/services/local_database.dart` — persists expert assessments and re-evaluates after feed, sampling, and water-quality changes.
- `phone_app/lib/screens/dashboard_screen.dart` — shows farm-level Expert Insights.
- `phone_app/lib/screens/pond_detail_screen.dart` — shows Expert Pond Assessment with evidence, reasoning, rules, and actions.
- `phone_app/test/expert_engine_test.dart` — tests positive, negative, boundary, compound, conflict, missing/invalid data, historical comparison, and offline deterministic behavior.

The long-form requirements from the prompt are intentionally implemented as code and documented in `phone_app/docs/EXPERT_AI.md` so the app remains the source of truth for behavior.
