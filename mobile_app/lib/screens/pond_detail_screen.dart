import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/app_models.dart';
import '../services/providers.dart';

class PondDetailScreen extends ConsumerWidget {
  const PondDetailScreen({super.key, required this.pondId});

  final String pondId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final snapshot = ref.watch(pondSnapshotProvider(pondId));
    return Scaffold(
      appBar: AppBar(title: const Text('Pond data')),
      body: snapshot.when(
        data: (data) => _PondDetail(snapshot: data),
        error: (error, _) => Center(child: Text('Unable to load pond: $error')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _PondDetail extends StatelessWidget {
  const _PondDetail({required this.snapshot});

  final PondSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final pond = snapshot.pond;
    final formatter = NumberFormat.compact();
    final doc = DateTime.now().difference(pond.stockingDate).inDays + 1;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(22),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            gradient: const LinearGradient(colors: [Color(0xFF023E8A), Color(0xFF00B4D8)]),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(pond.name, style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white, fontWeight: FontWeight.w900)),
              const SizedBox(height: 6),
              Text('DOC $doc • ${pond.areaSqm.toStringAsFixed(0)} m² • ${formatter.format(pond.initialStock)} stocked', style: const TextStyle(color: Colors.white70)),
              const SizedBox(height: 18),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  _Pill(label: 'Biomass', value: '${snapshot.biomassKg.toStringAsFixed(0)} kg'),
                  _Pill(label: 'ABW', value: '${snapshot.latestAbw.toStringAsFixed(1)} g'),
                  _Pill(label: 'Survival', value: '${snapshot.latestSurvival.toStringAsFixed(1)}%'),
                  _Pill(label: 'Feed', value: '${snapshot.feedKg.toStringAsFixed(1)} kg'),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Growth trend', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 16),
                SizedBox(height: 220, child: _GrowthChart(snapshot: snapshot)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('CEO decision support', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 10),
                _Recommendation(snapshot: snapshot),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(color: Colors.white.withOpacity(.16), borderRadius: BorderRadius.circular(18)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(color: Colors.white70)),
            Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900)),
          ],
        ),
      ),
    );
  }
}

class _GrowthChart extends StatelessWidget {
  const _GrowthChart({required this.snapshot});

  final PondSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final base = snapshot.latestAbw <= 0 ? 1.0 : snapshot.latestAbw;
    final spots = List.generate(6, (index) => FlSpot(index.toDouble(), base + index * 1.8));
    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(rightTitles: AxisTitles(), topTitles: AxisTitles()),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: const Color(0xFF00A3A3),
            barWidth: 4,
            belowBarData: BarAreaData(show: true, color: const Color(0xFF00A3A3).withOpacity(.16)),
          ),
        ],
      ),
    );
  }
}

class _Recommendation extends StatelessWidget {
  const _Recommendation({required this.snapshot});

  final PondSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    final attention = snapshot.riskLabel != 'Healthy';
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(attention ? Icons.priority_high_rounded : Icons.check_circle_rounded, color: attention ? Colors.orange : Colors.green),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            attention
                ? 'Prioritize this pond for technician review. Check dissolved oxygen, ammonia, feed tray leftovers, and survival trend before increasing feed.'
                : 'Pond is within the current safe band. Continue regular sampling, feed tray checks, and water-quality logging.',
          ),
        ),
      ],
    );
  }
}
