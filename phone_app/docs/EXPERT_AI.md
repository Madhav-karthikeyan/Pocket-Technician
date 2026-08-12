# Aquaculture Expert Intelligence

The Expert AI is not a separate product or standalone dashboard. It is an offline-first deterministic intelligence layer inside Pocket Technician.

## Data flow

Existing local farm/pond records feed existing domain calculations first. Expert intelligence then evaluates the calculated and measured outputs:

`Local data → AquacultureCalculator → ExpertContext → rules → findings → risk scores → conflict resolution → explainable actions → existing dashboard/pond UI`.

## No duplicated business logic

The expert engine consumes `AquacultureCalculator` outputs such as feeding plans, sampling metrics, biomass, survival, FCR, DOC, and weather-adjusted feed. It does not implement a second feeding formula.

## Implemented engine components

- Structured `ExpertContext` with farm, pond, growth, feeding, water-quality, weather, feed-tray, disease/health, and historical fields.
- Versioned `ExpertRule` objects with ID, name, version, domain, description, severity, priority, dependencies, effective date, and status.
- `AquacultureExpertEngine` for deterministic evaluation.
- Compound multi-factor rules.
- Rule dependency metadata.
- Risk categories: feeding, water quality, growth, disease, weather, stress, and overall.
- Confidence levels: high, moderate, low, insufficient data.
- Explainable `ExpertFinding` records with evidence, reasoning chains, actions, confidence, and optional feed adjustment factor.
- Conflict handling for environmental feed reduction versus fast tray consumption.
- Input validation for invalid DO, pH, ABW, pond area, stocking count, and survival values.
- Assessment persistence through the local database.
- Event-driven re-evaluation after new feed, sampling, and water-quality entries.

## Initial rule knowledge base

- `WQ_DO_001` — Low dissolved oxygen risk.
- `STRESS_TEMP_DO_BIOMASS_FEED_001` — Compound high temperature + low DO + high biomass + high feed/tray stress.
- `FEED_TRAY_LEFTOVER_001` — Tray leftover / weaker feeding response.
- `WEATHER_RAIN_001` — Heavy rainfall forecast stress risk.
- `GROWTH_FCR_001` — Weak growth with elevated FCR.
- `CONFLICT_FEED_ENV_001` — Conflicting fast tray consumption and environmental caution.

## UI integration

- Dashboard: `Expert Insights` card prioritizes pond assessments.
- Pond detail: `Expert Pond Assessment` shows summary, confidence, final suggested feed, fired rules, evidence, reasoning, and recommended actions.

## Safety rules

- The expert engine never silently modifies operational records.
- Consequential actions remain recommendations requiring farmer review.
- Missing or invalid data returns an insufficient-data assessment instead of invented reasoning.
- Future LLM/AI layers may explain deterministic results but must not override versioned rules.
