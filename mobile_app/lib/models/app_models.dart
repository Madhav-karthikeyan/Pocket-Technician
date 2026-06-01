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
