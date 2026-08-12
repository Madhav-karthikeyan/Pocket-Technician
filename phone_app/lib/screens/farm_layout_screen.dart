import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../models/app_models.dart';
import '../services/providers.dart';

class FarmLayoutScreen extends ConsumerWidget {
  const FarmLayoutScreen({super.key, required this.farmId});

  final String farmId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final farm = ref.watch(farmProvider(farmId));
    final snapshots = ref.watch(pondSnapshotsProvider(farmId));
    return Scaffold(
      appBar: AppBar(title: const Text('Farm layout')),
      body: farm.when(
        data: (farmData) => snapshots.when(
          data: (items) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(farmData.name, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900)),
              Text(farmData.location, style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 16),
              Text('Tap any pond in your layout to open live pond data.', style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 16),
              AspectRatio(
                aspectRatio: farmData.layoutWidth / farmData.layoutHeight,
                child: _PondLayoutCanvas(snapshots: items),
              ),
              const SizedBox(height: 18),
              Text('Pond health', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              ...items.map((snapshot) => _PondSummary(snapshot: snapshot)),
            ],
          ),
          error: (error, _) => Center(child: Text('Unable to load ponds: $error')),
          loading: () => const Center(child: CircularProgressIndicator()),
        ),
        error: (error, _) => Center(child: Text('Unable to load farm: $error')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showLayoutHelp(context),
        icon: const Icon(Icons.edit_location_alt_rounded),
        label: const Text('Layout mode'),
      ),
    );
  }

  void _showLayoutHelp(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => const Padding(
        padding: EdgeInsets.all(20),
        child: Text(
          'This mobile conversion stores each pond with normalized x/y/width/height coordinates. '
          'Drag a pond card to adjust its position. Tap any pond to open details. Coordinates are saved in the phone database, so the farm layout remains available offline without Supabase.',
        ),
      ),
    );
  }
}

class _PondLayoutCanvas extends StatelessWidget {
  const _PondLayoutCanvas({required this.snapshots});

  final List<PondSnapshot> snapshots;

  @override
  Widget build(BuildContext context) {
    return InteractiveViewer(
      minScale: 0.8,
      maxScale: 3,
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Container(
            decoration: BoxDecoration(
              color: const Color(0xFFEAF5EF),
              borderRadius: BorderRadius.circular(28),
              border: Border.all(color: const Color(0xFFB8DCD7), width: 2),
            ),
            child: Stack(
              children: [
                Positioned.fill(
                  child: CustomPaint(painter: _RoadPainter()),
                ),
                for (final snapshot in snapshots)
                  _PondTile(
                    snapshot: snapshot,
                    canvasWidth: constraints.maxWidth,
                    canvasHeight: constraints.maxHeight,
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _PondTile extends ConsumerWidget {
  const _PondTile({required this.snapshot, required this.canvasWidth, required this.canvasHeight});

  final PondSnapshot snapshot;
  final double canvasWidth;
  final double canvasHeight;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pond = snapshot.pond;
    final healthy = snapshot.riskLabel == 'Healthy';
    return Positioned(
      left: pond.x * canvasWidth,
      top: pond.y * canvasHeight,
      width: pond.width * canvasWidth,
      height: pond.height * canvasHeight,
      child: GestureDetector(
        onTap: () => context.push('/ponds/${pond.id}'),
        onPanUpdate: (details) async {
          final newX = (pond.x + details.delta.dx / canvasWidth).clamp(0.0, 1.0 - pond.width).toDouble();
          final newY = (pond.y + details.delta.dy / canvasHeight).clamp(0.0, 1.0 - pond.height).toDouble();
          await ref.read(databaseProvider).updatePondLayout(pondId: pond.id, x: newX, y: newY, width: pond.width, height: pond.height);
          ref.invalidate(pondSnapshotsProvider(pond.farmId));
          ref.invalidate(allPondSnapshotsProvider);
        },
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: LinearGradient(
              colors: healthy ? const [Color(0xFF00B4D8), Color(0xFF0077B6)] : const [Color(0xFFFFB703), Color(0xFFFB8500)],
            ),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(.16), blurRadius: 12, offset: const Offset(0, 6))],
          ),
          padding: const EdgeInsets.all(10),
          child: FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(pond.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 18)),
                Text('${snapshot.biomassKg.toStringAsFixed(0)} kg biomass', style: const TextStyle(color: Colors.white)),
                Text(snapshot.riskLabel, style: const TextStyle(color: Colors.white70)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PondSummary extends StatelessWidget {
  const _PondSummary({required this.snapshot});

  final PondSnapshot snapshot;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        onTap: () => context.push('/ponds/${snapshot.pond.id}'),
        leading: Icon(snapshot.riskLabel == 'Healthy' ? Icons.check_circle_rounded : Icons.warning_rounded),
        title: Text(snapshot.pond.name, style: const TextStyle(fontWeight: FontWeight.w800)),
        subtitle: Text('ABW ${snapshot.latestAbw.toStringAsFixed(1)}g • Survival ${snapshot.latestSurvival.toStringAsFixed(1)}%'),
        trailing: const Icon(Icons.chevron_right_rounded),
      ),
    );
  }
}

class _RoadPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF8BAA9B).withOpacity(.25)
      ..strokeWidth = 16
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(Offset(size.width * .08, size.height * .46), Offset(size.width * .92, size.height * .46), paint);
    canvas.drawLine(Offset(size.width * .50, size.height * .05), Offset(size.width * .50, size.height * .92), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
