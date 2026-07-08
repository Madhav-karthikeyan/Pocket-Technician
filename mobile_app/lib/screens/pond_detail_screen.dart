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
    final detail = ref.watch(pondDetailProvider(pondId));
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pond data'),
        actions: [
          IconButton(
            tooltip: 'Generate local report',
            onPressed: () async {
              await ref.read(databaseProvider).createLocalReport(pondId);
              ref.invalidate(pondDetailProvider(pondId));
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Report saved locally on this phone.')));
              }
            },
            icon: const Icon(Icons.picture_as_pdf_rounded),
          ),
        ],
      ),
      body: detail.when(
        data: (data) => _PondDetail(bundle: data),
        error: (error, _) => Center(child: Text('Unable to load pond: $error')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _PondDetail extends StatelessWidget {
  const _PondDetail({required this.bundle});

  final PondDetailBundle bundle;

  @override
  Widget build(BuildContext context) {
    final snapshot = bundle.snapshot;
    final pond = snapshot.pond;
    final formatter = NumberFormat.compact();
    final doc = DateTime.now().difference(pond.stockingDate).inDays + 1;
    final water = snapshot.latestWater;
    final sample = snapshot.latestSampling;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(22),
          decoration: BoxDecoration(borderRadius: BorderRadius.circular(28), gradient: const LinearGradient(colors: [Color(0xFF023E8A), Color(0xFF00B4D8)])),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(pond.name, style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white, fontWeight: FontWeight.w900)),
              const SizedBox(height: 6),
              Text('DOC $doc • ${pond.areaSqm.toStringAsFixed(0)} m² • ${pond.depthM.toStringAsFixed(1)} m depth • ${formatter.format(pond.initialStock)} stocked', style: const TextStyle(color: Colors.white70)),
              const SizedBox(height: 18),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  _Pill(label: 'Biomass', value: '${snapshot.biomassKg.toStringAsFixed(0)} kg'),
                  _Pill(label: 'ABW', value: '${snapshot.latestAbw.toStringAsFixed(1)} g'),
                  _Pill(label: 'Survival', value: '${snapshot.latestSurvival.toStringAsFixed(1)}%'),
                  _Pill(label: 'Feed', value: '${snapshot.feedKg.toStringAsFixed(1)} kg'),
                  _Pill(label: 'Density', value: '${snapshot.biomassDensityKgM3.toStringAsFixed(3)} kg/m³'),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Growth trend', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 16),
              SizedBox(height: 220, child: _GrowthChart(sampling: bundle.sampling)),
            ]),
          ),
        ),
        const SizedBox(height: 12),
        _DataCard(
          title: 'Weekly analytics',
          rows: {
            'Weekly growth': '${(sample?.weeklyGrowthG ?? 0).toStringAsFixed(2)} g',
            'ADG': '${(sample?.adgG ?? 0).toStringAsFixed(2)} g/day',
            'Biomass gain': '${(sample?.weeklyBiomassGainKg ?? 0).toStringAsFixed(1)} kg',
            'Weekly FCR': (sample?.weeklyFcr ?? 0).toStringAsFixed(2),
          },
        ),
        const SizedBox(height: 12),
        _DataCard(
          title: 'Water quality',
          rows: {
            'Temperature': '${(water?.temperature ?? 0).toStringAsFixed(1)} °C',
            'Dissolved oxygen': '${(water?.dissolvedOxygen ?? 0).toStringAsFixed(1)} mg/L',
            'pH': (water?.ph ?? 0).toStringAsFixed(1),
            'Ammonia': (water?.ammonia ?? 0).toStringAsFixed(2),
            'Nitrite': (water?.nitrite ?? 0).toStringAsFixed(2),
          },
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Decision support', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 10),
              _Recommendation(snapshot: snapshot),
            ]),
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Expanded(child: Text('Local reports', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800))),
                Text('${bundle.reports.length} saved'),
              ]),
              const SizedBox(height: 8),
              if (bundle.reports.isEmpty)
                const Text('Tap the report icon to generate an offline technician report stored only on this phone.'),
              for (final report in bundle.reports.take(3))
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.description_rounded),
                  title: Text(report.title),
                  subtitle: Text('${DateFormat.yMMMd().add_jm().format(report.createdAt)}\n${report.body}', maxLines: 4, overflow: TextOverflow.ellipsis),
                ),
            ]),
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
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: const TextStyle(color: Colors.white70)),
          Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900)),
        ]),
      ),
    );
  }
}

class _GrowthChart extends StatelessWidget {
  const _GrowthChart({required this.sampling});

  final List<SamplingLog> sampling;

  @override
  Widget build(BuildContext context) {
    final spots = sampling.isEmpty
        ? const [FlSpot(0, 0)]
        : sampling.asMap().entries.map((entry) => FlSpot(entry.key.toDouble(), entry.value.abwG)).toList();
    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(rightTitles: AxisTitles(), topTitles: AxisTitles()),
        borderData: FlBorderData(show: false),
        lineBarsData: [LineChartBarData(spots: spots, isCurved: true, color: const Color(0xFF00A3A3), barWidth: 4, belowBarData: BarAreaData(show: true, color: const Color(0xFF00A3A3).withOpacity(.16)))],
      ),
    );
  }
}

class _DataCard extends StatelessWidget {
  const _DataCard({required this.title, required this.rows});

  final String title;
  final Map<String, String> rows;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          for (final row in rows.entries)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(children: [Expanded(child: Text(row.key)), Text(row.value, style: const TextStyle(fontWeight: FontWeight.w800))]),
            ),
        ]),
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
    return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Icon(attention ? Icons.priority_high_rounded : Icons.check_circle_rounded, color: attention ? Colors.orange : Colors.green),
      const SizedBox(width: 12),
      Expanded(
        child: Text(attention
            ? 'Prioritize this pond for technician review. Check dissolved oxygen, ammonia/nitrite, carrying density, feed tray leftovers, and survival trend before increasing feed.'
            : 'Pond is within the current safe band. Continue regular sampling, feed tray checks, and water-quality logging.'),
      ),
    ]);
  }
}
