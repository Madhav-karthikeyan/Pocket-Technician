import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/app_models.dart';
import '../services/providers.dart';

class TechnicianModulesScreen extends ConsumerStatefulWidget {
  const TechnicianModulesScreen({super.key});

  @override
  ConsumerState<TechnicianModulesScreen> createState() => _TechnicianModulesScreenState();
}

class _TechnicianModulesScreenState extends ConsumerState<TechnicianModulesScreen> {
  final _farmerName = TextEditingController(text: 'New Farmer');
  final _farmerPhone = TextEditingController(text: '+91');
  final _village = TextEditingController(text: 'Village');
  final _farmName = TextEditingController(text: 'New Farm');
  final _location = TextEditingController(text: 'Location');
  final _pondName = TextEditingController(text: 'Pond 1');
  final _area = TextEditingController(text: '4000');
  final _depth = TextEditingController(text: '1.2');
  final _stock = TextEditingController(text: '100000');
  final _feed = TextEditingController(text: '25');
  final _count = TextEditingController(text: '80');
  final _temperature = TextEditingController(text: '30');
  final _do = TextEditingController(text: '5');
  final _ph = TextEditingController(text: '7.8');
  final _ammonia = TextEditingController(text: '0.2');
  final _nitrite = TextEditingController(text: '0.2');
  final _trayLeft = TextEditingController(text: '5');
  final _consumedMinutes = TextEditingController(text: '60');
  final _feedPrice = TextEditingController(text: '45');
  final _shrimpPrice = TextEditingController(text: '260');
  String? _selectedPondId;
  String _lastMessage = '';

  @override
  void dispose() {
    for (final controller in [
      _farmerName,
      _farmerPhone,
      _village,
      _farmName,
      _location,
      _pondName,
      _area,
      _depth,
      _stock,
      _feed,
      _count,
      _temperature,
      _do,
      _ph,
      _ammonia,
      _nitrite,
      _trayLeft,
      _consumedMinutes,
      _feedPrice,
      _shrimpPrice,
    ]) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ponds = ref.watch(allPondSnapshotsProvider);
    return DefaultTabController(
      length: 8,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Technician Modules'),
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'Setup'),
              Tab(text: 'Feed'),
              Tab(text: 'Sampling'),
              Tab(text: 'Water'),
              Tab(text: 'Feed Tray'),
              Tab(text: 'Profit'),
              Tab(text: 'Virtual'),
              Tab(text: 'Reports'),
            ],
          ),
        ),
        body: ponds.when(
          data: (items) {
            _selectedPondId ??= items.isEmpty ? null : items.first.pond.id;
            final selected = items.where((item) => item.pond.id == _selectedPondId).firstOrNull;
            return Column(
              children: [
                if (_lastMessage.isNotEmpty)
                  MaterialBanner(
                    content: Text(_lastMessage),
                    actions: [TextButton(onPressed: () => setState(() => _lastMessage = ''), child: const Text('Dismiss'))],
                  ),
                Expanded(
                  child: TabBarView(
                    children: [
                      _setupTab(),
                      _feedTab(items),
                      _samplingTab(items),
                      _waterTab(items),
                      _feedTrayTab(selected),
                      _profitTab(selected),
                      _virtualFarmTab(items),
                      _reportsTab(items),
                    ],
                  ),
                ),
              ],
            );
          },
          error: (error, _) => Center(child: Text('Unable to load local farm database: $error')),
          loading: () => const Center(child: CircularProgressIndicator()),
        ),
      ),
    );
  }

  Widget _setupTab() {
    return _ModuleList(
      children: [
        _sectionTitle('Farm / Pond setup'),
        _field(_farmerName, 'Farmer name'),
        _field(_farmerPhone, 'Farmer mobile'),
        _field(_village, 'Village'),
        _field(_farmName, 'Farm name'),
        _field(_location, 'Location'),
        _field(_pondName, 'Pond name'),
        Row(children: [Expanded(child: _field(_area, 'Area m²', number: true)), const SizedBox(width: 12), Expanded(child: _field(_depth, 'Depth m', number: true))]),
        _field(_stock, 'Initial stock', number: true),
        FilledButton.icon(
          onPressed: _createFarm,
          icon: const Icon(Icons.add_location_alt_rounded),
          label: const Text('Create farm, pond, and layout'),
        ),
      ],
    );
  }

  Widget _feedTab(List<PondSnapshot> ponds) {
    return _ModuleList(
      children: [
        _sectionTitle('Daily feed entry'),
        _pondSelector(ponds),
        _field(_feed, 'Feed given today (kg)', number: true),
        FilledButton.icon(onPressed: _saveFeed, icon: const Icon(Icons.save_rounded), label: const Text('Save feed')),
      ],
    );
  }

  Widget _samplingTab(List<PondSnapshot> ponds) {
    final count = int.tryParse(_count.text) ?? 1;
    final abw = 1000 / count;
    return _ModuleList(
      children: [
        _sectionTitle('Sampling & growth analytics'),
        _pondSelector(ponds),
        _field(_count, 'Count per kg', number: true),
        _field(_feed, 'Daily feed used for survival estimate (kg)', number: true),
        _infoTile('ABW formula', 'ABW = 1000 / count = ${abw.toStringAsFixed(2)} g'),
        FilledButton.icon(onPressed: _saveSampling, icon: const Icon(Icons.science_rounded), label: const Text('Run and save sampling')),
      ],
    );
  }

  Widget _waterTab(List<PondSnapshot> ponds) {
    return _ModuleList(
      children: [
        _sectionTitle('Water quality monitoring'),
        _pondSelector(ponds),
        Row(children: [Expanded(child: _field(_temperature, 'Temperature °C', number: true)), const SizedBox(width: 12), Expanded(child: _field(_do, 'DO mg/L', number: true))]),
        Row(children: [Expanded(child: _field(_ph, 'pH', number: true)), const SizedBox(width: 12), Expanded(child: _field(_ammonia, 'Ammonia', number: true))]),
        _field(_nitrite, 'Nitrite', number: true),
        _infoTile('Safe thresholds', 'DO ≥ 4 mg/L, ammonia ≤ 0.5, nitrite ≤ 0.5, pH around 7.5–8.5.'),
        FilledButton.icon(onPressed: _saveWater, icon: const Icon(Icons.water_drop_rounded), label: const Text('Save water check')),
      ],
    );
  }

  Widget _feedTrayTab(PondSnapshot? selected) {
    final lastFeed = double.tryParse(_feed.text) ?? 0;
    final trayLeft = double.tryParse(_trayLeft.text) ?? 0;
    final minutes = double.tryParse(_consumedMinutes.text) ?? 0;
    final decision = _feedTrayDecision(selected?.latestAbw ?? 0, lastFeed, trayLeft, minutes);
    return _ModuleList(
      children: [
        _sectionTitle('Feed tray calculation'),
        _field(_feed, 'Last feed given (kg)', number: true),
        _field(_trayLeft, 'Feed left on tray (g)', number: true),
        _field(_consumedMinutes, 'Consumed time (minutes)', number: true),
        _infoTile('Recommendation', decision),
      ],
    );
  }

  Widget _profitTab(PondSnapshot? selected) {
    final feedPrice = double.tryParse(_feedPrice.text) ?? 0;
    final shrimpPrice = double.tryParse(_shrimpPrice.text) ?? 0;
    final biomass = selected?.biomassKg ?? 0;
    final feed = selected?.feedKg ?? 0;
    final revenue = biomass * shrimpPrice;
    final feedCost = feed * feedPrice;
    return _ModuleList(
      children: [
        _sectionTitle('Profit & carrying capacity'),
        _field(_feedPrice, 'Feed price / kg', number: true),
        _field(_shrimpPrice, 'Shrimp price / kg', number: true),
        _infoTile('Revenue', '₹${revenue.toStringAsFixed(0)}'),
        _infoTile('Feed cost', '₹${feedCost.toStringAsFixed(0)}'),
        _infoTile('Projected profit', '₹${(revenue - feedCost).toStringAsFixed(0)}'),
        _infoTile('Biomass density', '${biomass.toStringAsFixed(1)} kg across selected pond area'),
      ],
    );
  }

  Widget _virtualFarmTab(List<PondSnapshot> ponds) {
    final totalBiomass = ponds.fold<double>(0, (sum, pond) => sum + pond.biomassKg);
    final totalFeed = ponds.fold<double>(0, (sum, pond) => sum + pond.feedKg);
    return _ModuleList(
      children: [
        _sectionTitle('Virtual farm projection'),
        _infoTile('Current biomass', '${totalBiomass.toStringAsFixed(1)} kg'),
        _infoTile('Accumulated feed', '${totalFeed.toStringAsFixed(1)} kg'),
        _infoTile('45-day what-if', 'At steady growth, use pond details and feed tray records to project biomass, survival, FCR, and profit before harvest.'),
      ],
    );
  }

  Widget _reportsTab(List<PondSnapshot> ponds) {
    return _ModuleList(
      children: [
        _sectionTitle('Reports, AI, and original modules'),
        _infoTile('Advanced technician PDF', 'Mobile export hooks can use this local database to generate the same sampling, growth, mortality, FCR, economy, and carrying-capacity report.'),
        _infoTile('Farm comparison', '${ponds.length} ponds available for multi-pond comparison.'),
        _infoTile('Feed Tray AI', 'Reference-chart feed projection is represented by feed tray and virtual farm modules.'),
        _infoTile('Shrimp larvae detection', 'Camera/AI integration can be connected as a native mobile camera flow while keeping the farm records local.'),
        _infoTile('Weather & lunar logic', 'Ready as a mobile module hook; it can use phone location and weather APIs while preserving offline farm data.'),
      ],
    );
  }

  Widget _pondSelector(List<PondSnapshot> ponds) {
    return DropdownButtonFormField<String>(
      value: _selectedPondId,
      items: ponds.map((item) => DropdownMenuItem(value: item.pond.id, child: Text(item.pond.name))).toList(),
      onChanged: (value) => setState(() => _selectedPondId = value),
      decoration: const InputDecoration(labelText: 'Pond', border: OutlineInputBorder()),
    );
  }

  Widget _field(TextEditingController controller, String label, {bool number = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextField(
        controller: controller,
        keyboardType: number ? const TextInputType.numberWithOptions(decimal: true) : TextInputType.text,
        decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
        onChanged: (_) => setState(() {}),
      ),
    );
  }

  Widget _sectionTitle(String title) => Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900)),
      );

  Widget _infoTile(String title, String subtitle) => Card(
        child: ListTile(title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)), subtitle: Text(subtitle)),
      );

  Future<void> _createFarm() async {
    final farmId = await ref.read(databaseProvider).createFarmWithFirstPond(
          farmerName: _farmerName.text,
          farmerPhone: _farmerPhone.text,
          village: _village.text,
          farmName: _farmName.text,
          location: _location.text,
          pondName: _pondName.text,
          areaSqm: _toDouble(_area),
          depthM: _toDouble(_depth),
          initialStock: int.tryParse(_stock.text) ?? 0,
          stockingDate: DateTime.now(),
        );
    _invalidateData();
    setState(() => _lastMessage = 'Farm created. Open the farm layout from the CEO dashboard. Farm ID: $farmId');
  }

  Future<void> _saveFeed() async {
    final pondId = _selectedPondId;
    if (pondId == null) return;
    await ref.read(databaseProvider).addFeedLog(pondId: pondId, feedKg: _toDouble(_feed), fedAt: DateTime.now());
    _invalidateData();
    setState(() => _lastMessage = 'Feed saved for ${DateFormat.yMMMd().format(DateTime.now())}.');
  }

  Future<void> _saveSampling() async {
    final pondId = _selectedPondId;
    if (pondId == null) return;
    await ref.read(databaseProvider).addSamplingLog(
          pondId: pondId,
          countPerKg: int.tryParse(_count.text) ?? 1,
          dailyFeedKg: _toDouble(_feed),
          sampledAt: DateTime.now(),
        );
    _invalidateData();
    setState(() => _lastMessage = 'Sampling record saved with ABW, survival, biomass, and feed percentage.');
  }

  Future<void> _saveWater() async {
    final pondId = _selectedPondId;
    if (pondId == null) return;
    await ref.read(databaseProvider).addWaterLog(
          pondId: pondId,
          checkedAt: DateTime.now(),
          temperature: _toDouble(_temperature),
          dissolvedOxygen: _toDouble(_do),
          ph: _toDouble(_ph),
          ammonia: _toDouble(_ammonia),
          nitrite: _toDouble(_nitrite),
        );
    _invalidateData();
    setState(() => _lastMessage = 'Water quality record saved and risk metrics refreshed.');
  }

  void _invalidateData() {
    ref.invalidate(allPondSnapshotsProvider);
    ref.invalidate(ceoMetricsProvider);
    ref.invalidate(farmersProvider);
  }

  double _toDouble(TextEditingController controller) => double.tryParse(controller.text) ?? 0;

  String _feedTrayDecision(double abw, double lastFeed, double trayLeft, double consumedMinutes) {
    if (lastFeed <= 0) return 'Enter the last feed quantity to calculate a decision.';
    final leftoverPct = trayLeft / (lastFeed * 1000) * 100;
    if (leftoverPct > 5 || consumedMinutes > 120) return 'Reduce feed by 10–15% and check water quality before the next meal.';
    if (leftoverPct <= 1 && consumedMinutes < 60 && abw > 0) return 'Increase feed cautiously by 5–10% and re-check tray response.';
    return 'Maintain current feed and continue regular tray checks.';
  }
}

class _ModuleList extends StatelessWidget {
  const _ModuleList({required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: children,
    );
  }
}
