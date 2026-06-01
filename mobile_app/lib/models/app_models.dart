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
        'initial_stock': initialStock,
        'stocking_date': stockingDate.toIso8601String(),
        'layout_x': x,
        'layout_y': y,
        'layout_w': width,
        'layout_h': height,
      };
}

class PondSnapshot {
  const PondSnapshot({
    required this.pond,
    required this.latestAbw,
    required this.latestSurvival,
    required this.biomassKg,
    required this.feedKg,
    required this.riskLabel,
  });

  final Pond pond;
  final double latestAbw;
  final double latestSurvival;
  final double biomassKg;
  final double feedKg;
  final String riskLabel;
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
