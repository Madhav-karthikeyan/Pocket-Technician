import 'package:flutter_test/flutter_test.dart';
import 'package:pocket_technician_phone_app/core/services/aquaculture_calculator.dart';

void main() {
  final calc = AquacultureCalculator();
  test('DOC, ABW, biomass, survival, ADG, FCR match Streamlit formulas', () {
    expect(calc.doc(DateTime(2026, 1, 1), DateTime(2026, 1, 10)), 10);
    expect(calc.abwFromCount(500), 2.0);
    expect(calc.biomass(85000, 12), 1020);
    expect(calc.survival(85000, 100000), 85);
    expect(calc.adg(10, 8, 7).toStringAsFixed(3), '0.286');
    expect(calc.fcr(210, 140), 1.5);
  });

  test('sampling calculates weekly metrics', () {
    final first = calc.sampling(countInput: 500, dailyFeedKg: 20, initialStock: 100000, stockingDate: DateTime(2026, 1, 1), samplingDate: DateTime(2026, 1, 50));
    final second = calc.sampling(countInput: 400, dailyFeedKg: 25, initialStock: 100000, stockingDate: DateTime(2026, 1, 1), samplingDate: DateTime(2026, 1, 57), previous: first, intervalFeedUsed: 175);
    expect(first.doc, 50);
    expect(first.count, 500);
    expect(first.abw, 2.0);
    expect(first.presentNumbers, 100000);
    expect(second.weeklyAdg, isNotNull);
    expect(second.weeklyFcr, isNotNull);
  });

  test('feed calculations and tray logic', () {
    final plan = calc.feedingPlan(doc: 10, initialStock: 100000, survivalPct: 80, weatherFactor: .85);
    expect(plan.preSamplingFeedKgDay, 12.25);
    expect(plan.weatherAdjustedFeedKgDay, 8.33);
    expect(calc.feedTray(4, 10, 0, 25).decision, contains('Increase 2'));
    expect(calc.feedTray(26, 10, 12, 90).nextFeedKg, 9);
  });

  test('weather, lunar, virtual farm, ranking and grade', () {
    expect(calc.weatherFeedFactor(temperatureC: 35, rainMm: 0), .85);
    expect(calc.weatherFeedFactor(temperatureC: 25, rainMm: 0), .75);
    expect(calc.weatherFeedFactor(temperatureC: 30, rainMm: 21), .80);
    expect(calc.lunarPhase(DateTime(2026, 8, 12)), isA<LunarPhase>());
    final vf = calc.virtualFarm(pondArea: 1000, abw: 10, stockingDensity: 100, doc: 60, survival: 80, feedPrice: 90, shrimpPrice: 320);
    expect(vf.biomassKg, 800);
    expect(vf.profit, greaterThan(0));
    final score = calc.rankingScore(survival: 90, fcr: 1.5, biomass: 800);
    expect(score, 80);
    expect(calc.grade(86), 'A');
    expect(calc.grade(71), 'B');
    expect(calc.grade(70), 'C');
  });
}
