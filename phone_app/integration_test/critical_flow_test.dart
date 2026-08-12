import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:pocket_technician_phone_app/core/services/aquaculture_calculator.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('offline calculation flow survives service recreation', (tester) async {
    final calc = AquacultureCalculator();
    final sample = calc.sampling(countInput: 500, dailyFeedKg: 20, initialStock: 100000, stockingDate: DateTime(2026, 1, 1), samplingDate: DateTime(2026, 2, 15));
    final reopenedCalc = AquacultureCalculator();
    final feed = reopenedCalc.feedingPlan(doc: sample.doc, initialStock: 100000, survivalPct: sample.survivalPct, biomassKg: sample.biomass);
    expect(feed.weatherAdjustedFeedKgDay, greaterThan(0));
  });
}
