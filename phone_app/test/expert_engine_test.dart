import 'package:flutter_test/flutter_test.dart';
import 'package:pocket_technician_phone_app/core/expert/expert_engine.dart';
import 'package:pocket_technician_phone_app/core/services/aquaculture_calculator.dart';

void main() {
  const engine = AquacultureExpertEngine();
  final basePlan = AquacultureCalculator().feedingPlan(doc: 60, initialStock: 100000, survivalPct: 85, biomassKg: 900, areaM2: 1000, depthM: 1.2);

  ExpertContext context({
    double? temperature = 33,
    double? dissolvedOxygen = 3.6,
    double? biomass = 900,
    double? trayLeftover = 12,
    double? feedToday = 90,
    double? feedAverage = 70,
    double? rain = 0,
    double? weeklyFcr = 1.4,
    double? abw = 12,
    double? previousAbw = 11,
    int? consumptionMinutes = 80,
  }) => ExpertContext(
        farmName: 'Blue Ocean Farm',
        pondName: 'Pond A',
        doc: 60,
        pondAreaM2: 1000,
        depthM: 1.2,
        initialStock: 100000,
        abwG: abw,
        previousAbwG: previousAbw,
        biomassKg: biomass,
        survivalPct: 85,
        weeklyFcr: weeklyFcr,
        feedTodayKg: feedToday,
        feed7DayAverageKg: feedAverage,
        baseFeedingPlan: basePlan,
        temperatureC: temperature,
        dissolvedOxygenMgL: dissolvedOxygen,
        previousDissolvedOxygen: 4.2,
        ph: 7.8,
        ammoniaMgL: 0.2,
        rainForecastMm: rain,
        trayLeftoverPct: trayLeftover,
        consumptionMinutes: consumptionMinutes,
      );

  test('positive compound rule fires only when all stress conditions are satisfied', () {
    final assessment = engine.assess(context());
    expect(assessment.findings.map((f) => f.rule.id), contains('STRESS_TEMP_DO_BIOMASS_FEED_001'));
    expect(assessment.finalSuggestedFeedKg, lessThan(basePlan.weatherAdjustedFeedKgDay));
  });

  test('negative compound rule does not fire without low DO', () {
    final assessment = engine.assess(context(dissolvedOxygen: 5.4));
    expect(assessment.findings.map((f) => f.rule.id), isNot(contains('STRESS_TEMP_DO_BIOMASS_FEED_001')));
  });

  test('boundary low DO rule uses below threshold, not equal threshold', () {
    expect(engine.assess(context(dissolvedOxygen: 4.0)).findings.map((f) => f.rule.id), isNot(contains('WQ_DO_001')));
    expect(engine.assess(context(dissolvedOxygen: 3.99)).findings.map((f) => f.rule.id), contains('WQ_DO_001'));
  });

  test('conflict rule explains fast tray response versus environmental caution', () {
    final assessment = engine.assess(context(trayLeftover: 0, consumptionMinutes: 25));
    final conflict = assessment.findings.where((f) => f.rule.id == 'CONFLICT_FEED_ENV_001').single;
    expect(conflict.reasoningChain.join(' '), contains('higher safety priority'));
  });

  test('missing and invalid data returns safe insufficient-data assessment', () {
    final assessment = engine.assess(context(biomass: 100, dissolvedOxygen: -5));
    expect(assessment.confidence, ExpertConfidence.insufficientData);
    expect(assessment.findings, isEmpty);
  });

  test('historical growth comparison rule fires when ABW stalls and FCR is high', () {
    final assessment = engine.assess(context(abw: 11, previousAbw: 11, weeklyFcr: 2.0, dissolvedOxygen: 5.5, temperature: 29, trayLeftover: 3));
    expect(assessment.findings.map((f) => f.rule.id), contains('GROWTH_FCR_001'));
  });
}
