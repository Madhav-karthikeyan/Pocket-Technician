import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/app_models.dart';
import '../core/expert/expert_engine.dart';
import '../core/services/aquaculture_calculator.dart';
import 'local_database.dart';
import 'otp_service.dart';

final databaseProvider = Provider<LocalDatabase>((ref) => LocalDatabase.instance);

final otpServiceProvider = Provider<OtpService>((ref) {
  return OtpService(ref.watch(databaseProvider));
});

final ceoMetricsProvider = FutureProvider<CeoMetrics>((ref) {
  return ref.watch(databaseProvider).ceoMetrics();
});

final farmersProvider = FutureProvider<List<Farmer>>((ref) {
  return ref.watch(databaseProvider).farmers();
});

final farmsForFarmerProvider = FutureProvider.family<List<Farm>, String>((ref, farmerId) {
  return ref.watch(databaseProvider).farmsForFarmer(farmerId);
});

final farmProvider = FutureProvider.family<Farm, String>((ref, farmId) {
  return ref.watch(databaseProvider).farm(farmId);
});

final allPondSnapshotsProvider = FutureProvider<List<PondSnapshot>>((ref) {
  return ref.watch(databaseProvider).allPondSnapshots();
});

final pondSnapshotsProvider = FutureProvider.family<List<PondSnapshot>, String>((ref, farmId) {
  return ref.watch(databaseProvider).pondSnapshots(farmId);
});

final pondSnapshotProvider = FutureProvider.family<PondSnapshot, String>((ref, pondId) {
  return ref.watch(databaseProvider).pondSnapshot(pondId);
});

final pondDetailProvider = FutureProvider.family<PondDetailBundle, String>((ref, pondId) {
  return ref.watch(databaseProvider).pondDetail(pondId);
});


final pondExpertAssessmentProvider = FutureProvider.family<ExpertAssessment, String>((ref, pondId) async {
  final bundle = await ref.watch(pondDetailProvider(pondId).future);
  return _assessmentFromBundle(bundle);
});

final farmExpertAssessmentsProvider = FutureProvider<List<ExpertAssessment>>((ref) async {
  final snapshots = await ref.watch(allPondSnapshotsProvider.future);
  final assessments = <ExpertAssessment>[];
  for (final snapshot in snapshots) {
    final bundle = await ref.watch(pondDetailProvider(snapshot.pond.id).future);
    assessments.add(_assessmentFromBundle(bundle));
  }
  assessments.sort((a, b) => _severityWeight(b.overallSeverity).compareTo(_severityWeight(a.overallSeverity)));

  return assessments;
});

ExpertAssessment _assessmentFromBundle(PondDetailBundle bundle) {
  final snapshot = bundle.snapshot;
  final pond = snapshot.pond;
  final latest = snapshot.latestSampling;
  final water = snapshot.latestWater;
  final previousSampling = bundle.sampling.length >= 2 ? bundle.sampling[bundle.sampling.length - 2] : null;
  final feedToday = bundle.feed.isEmpty ? null : bundle.feed.last.feedKg;
  final feed7DayAverage = bundle.feed.isEmpty ? null : bundle.feed.map((log) => log.feedKg).reduce((a, b) => a + b) / bundle.feed.length;
  final calculator = AquacultureCalculator();
  final doc = calculator.doc(pond.stockingDate, DateTime.now());
  final plan = calculator.feedingPlan(
    doc: doc,
    initialStock: pond.initialStock.toDouble(),
    survivalPct: latest?.survivalPct ?? 100,
    biomassKg: latest?.biomassKg ?? 0,
    areaM2: pond.areaSqm,
    depthM: pond.depthM,
    accumulatedFeedKg: bundle.feed.fold<double>(0, (sum, log) => sum + log.feedKg),
  );
  return const AquacultureExpertEngine().assess(ExpertContext(
    farmName: snapshot.farm.name,
    pondName: pond.name,
    doc: doc,
    pondAreaM2: pond.areaSqm,
    depthM: pond.depthM,
    initialStock: pond.initialStock,
    abwG: latest?.abwG,
    biomassKg: latest?.biomassKg,
    survivalPct: latest?.survivalPct,
    adgG: latest?.adgG,
    weeklyFcr: latest?.weeklyFcr,
    feedTodayKg: feedToday,
    feed7DayAverageKg: feed7DayAverage,
    baseFeedingPlan: plan,
    temperatureC: water?.temperature,
    dissolvedOxygenMgL: water?.dissolvedOxygen,
    ph: water?.ph,
    ammoniaMgL: water?.ammonia,
    previousSurvivalPct: previousSampling?.survivalPct,
    previousAbwG: previousSampling?.abwG,
    recentFeedKg: bundle.feed.map((log) => log.feedKg).toList(),
    recentFcr: bundle.sampling.map((log) => log.weeklyFcr).where((value) => value > 0).toList(),
  ));
}

int _severityWeight(ExpertSeverity severity) => switch (severity) {
      ExpertSeverity.critical => 5,
      ExpertSeverity.high => 4,
      ExpertSeverity.medium => 3,
      ExpertSeverity.low => 2,
      ExpertSeverity.info => 1,
    };
