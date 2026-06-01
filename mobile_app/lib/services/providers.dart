import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/app_models.dart';
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

final pondSnapshotsProvider = FutureProvider.family<List<PondSnapshot>, String>((ref, farmId) {
  return ref.watch(databaseProvider).pondSnapshots(farmId);
});

final pondSnapshotProvider = FutureProvider.family<PondSnapshot, String>((ref, pondId) {
  return ref.watch(databaseProvider).pondSnapshot(pondId);
});
