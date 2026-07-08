import 'dart:math' as math;

class Farmer {
  const Farmer({
    required this.id,
    required this.name,
    required this.phone,
    required this.village,
    required this.createdAt,
  });

  final String id;
  final String name;
  final String phone;
  final String village;
  final DateTime createdAt;

  factory Farmer.fromMap(Map<String, Object?> map) => Farmer(
        id: map['id'] as String,
        name: map['name'] as String,
        phone: map['phone'] as String,
        village: map['village'] as String,
        createdAt: DateTime.parse(map['created_at'] as String),
      );

  Map<String, Object?> toMap() => {
        'id': id,
        'name': name,
        'phone': phone,
        'village': village,
        'created_at': createdAt.toIso8601String(),
      };
}

class Farm {
  const Farm({
    required this.id,
    required this.farmerId,
    required this.name,
    required this.location,
    required this.layoutWidth,
    required this.layoutHeight,
  });

  final String id;
  final String farmerId;
  final String name;
  final String location;
  final double layoutWidth;
  final double layoutHeight;

  factory Farm.fromMap(Map<String, Object?> map) => Farm(
        id: map['id'] as String,
        farmerId: map['farmer_id'] as String,
        name: map['name'] as String,
        location: map['location'] as String,
        layoutWidth: (map['layout_width'] as num).toDouble(),
        layoutHeight: (map['layout_height'] as num).toDouble(),
      );

  Map<String, Object?> toMap() => {
        'id': id,
        'farmer_id': farmerId,
        'name': name,
        'location': location,
        'layout_width': layoutWidth,
        'layout_height': layoutHeight,
      };
}

class Pond {
  const Pond({
    required this.id,
    required this.farmId,
    required this.name,
    required this.areaSqm,
    required this.depthM,
    required this.initialStock,
    required this.stockingDate,
    required this.x,
    required this.y,
    required this.width,
    required this.height,
  });

  final String id;
  final String farmId;
  final String name;
  final double areaSqm;
  final double depthM;
  final int initialStock;
  final DateTime stockingDate;
  final double x;
  final double y;
  final double width;
  final double height;

  factory Pond.fromMap(Map<String, Object?> map) => Pond(
        id: map['id'] as String,
        farmId: map['farm_id'] as String,
        name: map['name'] as String,
        areaSqm: (map['area_sqm'] as num).toDouble(),
        depthM: (map['depth_m'] as num?)?.toDouble() ?? 1,
        initialStock: map['initial_stock'] as int,
        stockingDate: DateTime.parse(map['stocking_date'] as String),
        x: (map['layout_x'] as num).toDouble(),
        y: (map['layout_y'] as num).toDouble(),
        width: (map['layout_w'] as num).toDouble(),
        height: (map['layout_h'] as num).toDouble(),
      );

  Map<String, Object?> toMap() => {
        'id': id,
        'farm_id': farmId,
        'name': name,
        'area_sqm': areaSqm,
        'depth_m': depthM,
        'initial_stock': initialStock,
        'stocking_date': stockingDate.toIso8601String(),
        'layout_x': x,
        'layout_y': y,
        'layout_w': width,
        'layout_h': height,
      };
}

class SamplingLog {
  const SamplingLog({
    required this.id,
    required this.pondId,
    required this.sampledAt,
    required this.abwG,
    required this.survivalPct,
    required this.biomassKg,
    required this.feedPct,
    required this.weeklyGrowthG,
    required this.adgG,
    required this.weeklyBiomassGainKg,
    required this.weeklyFcr,
  });

  final String id;
  final String pondId;
  final DateTime sampledAt;
  final double abwG;
  final double survivalPct;
  final double biomassKg;
  final double feedPct;
  final double weeklyGrowthG;
  final double adgG;
  final double weeklyBiomassGainKg;
  final double weeklyFcr;

  factory SamplingLog.fromMap(Map<String, Object?> map) => SamplingLog(
        id: map['id'] as String,
        pondId: map['pond_id'] as String,
        sampledAt: DateTime.parse(map['sampled_at'] as String),
        abwG: (map['abw_g'] as num).toDouble(),
        survivalPct: (map['survival_pct'] as num).toDouble(),
        biomassKg: (map['biomass_kg'] as num).toDouble(),
        feedPct: (map['feed_pct'] as num).toDouble(),
        weeklyGrowthG: (map['weekly_growth_g'] as num?)?.toDouble() ?? 0,
        adgG: (map['adg_g'] as num?)?.toDouble() ?? 0,
        weeklyBiomassGainKg: (map['weekly_biomass_gain_kg'] as num?)?.toDouble() ?? 0,
        weeklyFcr: (map['weekly_fcr'] as num?)?.toDouble() ?? 0,
      );
}

class FeedLog {
  const FeedLog({required this.id, required this.pondId, required this.fedAt, required this.feedKg});

  final String id;
  final String pondId;
  final DateTime fedAt;
  final double feedKg;

  factory FeedLog.fromMap(Map<String, Object?> map) => FeedLog(
        id: map['id'] as String,
        pondId: map['pond_id'] as String,
        fedAt: DateTime.parse(map['fed_at'] as String),
        feedKg: (map['feed_kg'] as num).toDouble(),
      );
}

class WaterLog {
  const WaterLog({
    required this.id,
    required this.pondId,
    required this.checkedAt,
    required this.temperature,
    required this.dissolvedOxygen,
    required this.ph,
    required this.ammonia,
    required this.nitrite,
  });

  final String id;
  final String pondId;
  final DateTime checkedAt;
  final double temperature;
  final double dissolvedOxygen;
  final double ph;
  final double ammonia;
  final double nitrite;

  factory WaterLog.fromMap(Map<String, Object?> map) => WaterLog(
        id: map['id'] as String,
        pondId: map['pond_id'] as String,
        checkedAt: DateTime.parse(map['checked_at'] as String),
        temperature: (map['temperature'] as num).toDouble(),
        dissolvedOxygen: (map['dissolved_oxygen'] as num).toDouble(),
        ph: (map['ph'] as num).toDouble(),
        ammonia: (map['ammonia'] as num).toDouble(),
        nitrite: (map['nitrite'] as num).toDouble(),
      );
}

class LocalReport {
  const LocalReport({required this.id, required this.pondId, required this.title, required this.body, required this.createdAt});

  final String id;
  final String pondId;
  final String title;
  final String body;
  final DateTime createdAt;

  factory LocalReport.fromMap(Map<String, Object?> map) => LocalReport(
        id: map['id'] as String,
        pondId: map['pond_id'] as String,
        title: map['title'] as String,
        body: map['body'] as String,
        createdAt: DateTime.parse(map['created_at'] as String),
      );
}

class FeedingChartPlan {
  const FeedingChartPlan({
    required this.doc,
    required this.stockUnits,
    required this.baseFeedKg,
    required this.preSamplingFeedKg,
    required this.survivalAdjustedFeedKg,
    required this.recommendedFeedKg,
    required this.feedSizeLabel,
    required this.samplingSuggestion,
    required this.weatherSuggestion,
    required this.carryingCapacitySuggestion,
    required this.profitToday,
    required this.poTeSuggestion,
  });

  final int doc;
  final double stockUnits;
  final double baseFeedKg;
  final double preSamplingFeedKg;
  final double survivalAdjustedFeedKg;
  final double recommendedFeedKg;
  final String feedSizeLabel;
  final String samplingSuggestion;
  final String weatherSuggestion;
  final String carryingCapacitySuggestion;
  final double profitToday;
  final String poTeSuggestion;
}

class PondSnapshot {
  const PondSnapshot({
    required this.pond,
    required this.latestAbw,
    required this.latestSurvival,
    required this.biomassKg,
    required this.feedKg,
    required this.riskLabel,
    required this.latestWater,
    required this.latestSampling,
  });

  final Pond pond;
  final double latestAbw;
  final double latestSurvival;
  final double biomassKg;
  final double feedKg;
  final String riskLabel;
  final WaterLog? latestWater;
  final SamplingLog? latestSampling;

  double get pondVolumeM3 => pond.areaSqm * pond.depthM;
  double get biomassDensityKgM3 => pondVolumeM3 <= 0 ? 0 : biomassKg / pondVolumeM3;

  FeedingChartPlan feedingChartPlan({
    DateTime? asOf,
    double feedPricePerKg = 45,
    double shrimpPricePerKg = 260,
    double overheadToday = 0,
  }) {
    final date = asOf ?? DateTime.now();
    final doc = math.max(1, date.difference(pond.stockingDate).inDays + 1);
    final stockUnits = pond.initialStock / 10000;
    final baseFeedKg = stockUnits;
    final preSamplingFeedKg = baseFeedKg + math.max(0, doc - 1) * 0.25;
    final survivalFactor = latestSampling == null ? 1.0 : (latestSurvival / 100).clamp(0.01, 1.0).toDouble();
    final survivalAdjustedFeedKg = preSamplingFeedKg * survivalFactor;
    final waterReduction = _waterFeedReductionFactor;
    final recommendedFeedKg = survivalAdjustedFeedKg * waterReduction;
    final revenueToday = biomassKg * shrimpPricePerKg;
    final feedCost = feedKg * feedPricePerKg;
    final profitToday = revenueToday - feedCost - overheadToday;
    final feedSizeLabel = _feedSizeForDoc(doc);
    final samplingSuggestion = latestSampling == null
        ? 'Before first sampling, use the starter chart: 1 kg per 10,000 shrimp plus 250 g/day.'
        : recommendedFeedKg < preSamplingFeedKg * .9
            ? 'Sampling indicates survival-adjusted feed is lower than the starter chart; watch tray leftovers and avoid overfeeding.'
            : 'Sampling supports the current feed path; increase only when tray, growth, and water are stable.';
    final weatherSuggestion = waterReduction < 1
        ? 'Reduce feed 10–20% during low DO, ammonia/nitrite stress, heavy rain, cloudy periods, or poor location-based weather alerts.'
        : 'No water-linked weather reduction is active; keep geolocation weather checks connected before each feeding.';
    final carryingCapacitySuggestion = biomassDensityKgM3 > .65
        ? 'Carrying capacity is tight; increase aeration, exchange water if needed, and do not push feed until density risk drops.'
        : 'Carrying capacity is within the current local threshold; feed, water, survival, and profit modules can keep scaling together.';
    final poTeSuggestion = 'Po-te dummy supervisor: connect feeding chart, sampling survival, feed tray, water, weather, biomass, carrying capacity, and profit before approving today’s feed.';
    return FeedingChartPlan(
      doc: doc,
      stockUnits: stockUnits,
      baseFeedKg: baseFeedKg,
      preSamplingFeedKg: preSamplingFeedKg,
      survivalAdjustedFeedKg: survivalAdjustedFeedKg,
      recommendedFeedKg: recommendedFeedKg,
      feedSizeLabel: feedSizeLabel,
      samplingSuggestion: samplingSuggestion,
      weatherSuggestion: weatherSuggestion,
      carryingCapacitySuggestion: carryingCapacitySuggestion,
      profitToday: profitToday,
      poTeSuggestion: poTeSuggestion,
    );
  }

  double get _waterFeedReductionFactor {
    final water = latestWater;
    if (water == null) return 1;
    if (water.dissolvedOxygen < 3.5 || water.ammonia > .8 || water.nitrite > .8) return .8;
    if (water.dissolvedOxygen < 4 || water.ammonia > .5 || water.nitrite > .5) return .9;
    return 1;
  }

  String _feedSizeForDoc(int doc) {
    if (doc <= 10) return 'Powder / crumble 0.3–0.5 mm';
    if (doc <= 25) return 'Crumble 0.5–0.8 mm';
    if (doc <= 45) return 'Pellet 1.0–1.2 mm';
    if (doc <= 70) return 'Pellet 1.4–1.8 mm';
    return 'Pellet 2.0 mm+';
  }
}

class PondDetailBundle {
  const PondDetailBundle({required this.snapshot, required this.sampling, required this.feed, required this.water, required this.reports});

  final PondSnapshot snapshot;
  final List<SamplingLog> sampling;
  final List<FeedLog> feed;
  final List<WaterLog> water;
  final List<LocalReport> reports;
}

class CeoMetrics {
  const CeoMetrics({
    required this.farmerCount,
    required this.farmCount,
    required this.pondCount,
    required this.totalBiomassKg,
    required this.averageSurvival,
    required this.riskPondCount,
  });

  final int farmerCount;
  final int farmCount;
  final int pondCount;
  final double totalBiomassKg;
  final double averageSurvival;
  final int riskPondCount;
}
