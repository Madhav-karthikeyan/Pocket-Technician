import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../models/app_models.dart';
import '../services/providers.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metrics = ref.watch(ceoMetricsProvider);
    final farmers = ref.watch(farmersProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('CEO Command Center'),
        actions: [
          IconButton(
            tooltip: 'Technician modules',
            onPressed: () => context.push('/modules'),
            icon: const Icon(Icons.apps_rounded),
          ),
          IconButton(
            onPressed: () => ref.invalidate(ceoMetricsProvider),
            icon: const Icon(Icons.refresh_rounded),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(ceoMetricsProvider);
          ref.invalidate(farmersProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            metrics.when(
              data: (value) => _MetricsGrid(metrics: value),
              error: (error, _) => Text('Unable to load metrics: $error'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
            const SizedBox(height: 20),
            Card(
              child: ListTile(
                leading: const Icon(Icons.engineering_rounded),
                title: const Text('Open technician modules', style: TextStyle(fontWeight: FontWeight.w800)),
                subtitle: const Text('Setup, feed, sampling, water quality, feed tray, profit, virtual farm, reports, AI hooks'),
                trailing: const Icon(Icons.chevron_right_rounded),
                onTap: () => context.push('/modules'),
              ),
            ),
            const SizedBox(height: 20),
            Text('Farmer database', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 12),
            farmers.when(
              data: (items) => Column(children: items.map((farmer) => _FarmerCard(farmer: farmer)).toList()),
              error: (error, _) => Text('Unable to load farmers: $error'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricsGrid extends StatelessWidget {
  const _MetricsGrid({required this.metrics});

  final CeoMetrics metrics;

  @override
  Widget build(BuildContext context) {
    final biomass = NumberFormat.compact().format(metrics.totalBiomassKg);
    final cards = [
      _MetricCard(label: 'Farmers', value: '${metrics.farmerCount}', icon: Icons.groups_rounded),
      _MetricCard(label: 'Farms', value: '${metrics.farmCount}', icon: Icons.landscape_rounded),
      _MetricCard(label: 'Ponds', value: '${metrics.pondCount}', icon: Icons.water_rounded),
      _MetricCard(label: 'Biomass kg', value: biomass, icon: Icons.scale_rounded),
      _MetricCard(label: 'Avg survival', value: '${metrics.averageSurvival.toStringAsFixed(1)}%', icon: Icons.health_and_safety_rounded),
      _MetricCard(label: 'Risk ponds', value: '${metrics.riskPondCount}', icon: Icons.warning_amber_rounded),
    ];
    return GridView.count(
      crossAxisCount: MediaQuery.sizeOf(context).width > 700 ? 3 : 2,
      childAspectRatio: 1.35,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      children: cards,
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({required this.label, required this.value, required this.icon});

  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(colors: [Color(0xFF003C43), Color(0xFF00A3A3)]),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(.08), blurRadius: 18, offset: const Offset(0, 8))],
      ),
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Icon(icon, color: Colors.white, size: 30),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(value, style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white, fontWeight: FontWeight.w900)),
              Text(label, style: const TextStyle(color: Colors.white70)),
            ],
          ),
        ],
      ),
    );
  }
}

class _FarmerCard extends ConsumerWidget {
  const _FarmerCard({required this.farmer});

  final Farmer farmer;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final farms = ref.watch(farmsForFarmerProvider(farmer.id));
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: CircleAvatar(
                backgroundColor: const Color(0xFFE1F7F5),
                child: Text(farmer.name.characters.first),
              ),
              title: Text(farmer.name, style: const TextStyle(fontWeight: FontWeight.w800)),
              subtitle: Text('${farmer.phone} • ${farmer.village}'),
            ),
            farms.when(
              data: (items) => Wrap(
                spacing: 8,
                children: items
                    .map(
                      (farm) => ActionChip(
                        avatar: const Icon(Icons.map_rounded, size: 18),
                        label: Text(farm.name),
                        onPressed: () => context.push('/farms/${farm.id}'),
                      ),
                    )
                    .toList(),
              ),
              error: (error, _) => Text('Farm load error: $error'),
              loading: () => const LinearProgressIndicator(),
            ),
          ],
        ),
      ),
    );
  }
}
