import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

import '../models/app_models.dart';

class LocalDatabase {
  LocalDatabase._();

  static final LocalDatabase instance = LocalDatabase._();
  static const _uuid = Uuid();
  Database? _db;

  Future<Database> get database async {
    final existing = _db;
    if (existing != null) return existing;
    final dbPath = await getDatabasesPath();
    final db = await openDatabase(
      p.join(dbPath, 'pocket_technician.db'),
      version: 1,
      onCreate: _createSchema,
    );
    _db = db;
    await _seedIfEmpty(db);
    return db;
  }

  Future<void> _createSchema(Database db, int version) async {
    await db.execute('''
      CREATE TABLE users(
        phone TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        last_login_at TEXT
      )
    ''');
    await db.execute('''
      CREATE TABLE farmers(
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        village TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE farms(
        id TEXT PRIMARY KEY,
        farmer_id TEXT NOT NULL,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        layout_width REAL NOT NULL,
        layout_height REAL NOT NULL,
        FOREIGN KEY(farmer_id) REFERENCES farmers(id) ON DELETE CASCADE
      )
    ''');
    await db.execute('''
      CREATE TABLE ponds(
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        name TEXT NOT NULL,
        area_sqm REAL NOT NULL,
        initial_stock INTEGER NOT NULL,
        stocking_date TEXT NOT NULL,
        layout_x REAL NOT NULL,
        layout_y REAL NOT NULL,
        layout_w REAL NOT NULL,
        layout_h REAL NOT NULL,
        FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
      )
    ''');
    await db.execute('''
      CREATE TABLE sampling_logs(
        id TEXT PRIMARY KEY,
        pond_id TEXT NOT NULL,
        sampled_at TEXT NOT NULL,
        abw_g REAL NOT NULL,
        survival_pct REAL NOT NULL,
        biomass_kg REAL NOT NULL,
        feed_pct REAL NOT NULL,
        FOREIGN KEY(pond_id) REFERENCES ponds(id) ON DELETE CASCADE
      )
    ''');
    await db.execute('''
      CREATE TABLE feed_logs(
        id TEXT PRIMARY KEY,
        pond_id TEXT NOT NULL,
        fed_at TEXT NOT NULL,
        feed_kg REAL NOT NULL,
        FOREIGN KEY(pond_id) REFERENCES ponds(id) ON DELETE CASCADE
      )
    ''');
    await db.execute('''
      CREATE TABLE water_logs(
        id TEXT PRIMARY KEY,
        pond_id TEXT NOT NULL,
        checked_at TEXT NOT NULL,
        temperature REAL NOT NULL,
        dissolved_oxygen REAL NOT NULL,
        ph REAL NOT NULL,
        ammonia REAL NOT NULL,
        nitrite REAL NOT NULL,
        FOREIGN KEY(pond_id) REFERENCES ponds(id) ON DELETE CASCADE
      )
    ''');
  }

  Future<void> _seedIfEmpty(Database db) async {
    final count = Sqflite.firstIntValue(
          await db.rawQuery('SELECT COUNT(*) FROM farmers'),
        ) ??
        0;
    if (count > 0) return;

    final farmer = Farmer(
      id: _uuid.v4(),
      name: 'Demo Farmer',
      phone: '+919999999999',
      village: 'Coastal Village',
      createdAt: DateTime.now(),
    );
    final farm = Farm(
      id: _uuid.v4(),
      farmerId: farmer.id,
      name: 'Demo Farm',
      location: 'East Block',
      layoutWidth: 360,
      layoutHeight: 520,
    );
    final ponds = [
      Pond(
        id: _uuid.v4(),
        farmId: farm.id,
        name: 'Nursery A',
        areaSqm: 4200,
        initialStock: 125000,
        stockingDate: DateTime(2026, 1, 8),
        x: 0.08,
        y: 0.08,
        width: 0.38,
        height: 0.28,
      ),
      Pond(
        id: _uuid.v4(),
        farmId: farm.id,
        name: 'Grow-out B',
        areaSqm: 6200,
        initialStock: 210000,
        stockingDate: DateTime(2026, 1, 14),
        x: 0.54,
        y: 0.10,
        width: 0.38,
        height: 0.34,
      ),
      Pond(
        id: _uuid.v4(),
        farmId: farm.id,
        name: 'Harvest C',
        areaSqm: 5800,
        initialStock: 190000,
        stockingDate: DateTime(2026, 1, 1),
        x: 0.16,
        y: 0.52,
        width: 0.70,
        height: 0.32,
      ),
    ];

    await db.transaction((txn) async {
      await txn.insert('farmers', farmer.toMap());
      await txn.insert('farms', farm.toMap());
      for (final pond in ponds) {
        await txn.insert('ponds', pond.toMap());
        await txn.insert('sampling_logs', {
          'id': _uuid.v4(),
          'pond_id': pond.id,
          'sampled_at': DateTime.now().subtract(const Duration(days: 3)).toIso8601String(),
          'abw_g': pond.name == 'Harvest C' ? 31.5 : 14.2,
          'survival_pct': pond.name == 'Grow-out B' ? 71.4 : 84.6,
          'biomass_kg': pond.name == 'Harvest C' ? 5065.0 : 1510.0,
          'feed_pct': pond.name == 'Harvest C' ? 2.2 : 3.8,
        });
        await txn.insert('feed_logs', {
          'id': _uuid.v4(),
          'pond_id': pond.id,
          'fed_at': DateTime.now().toIso8601String(),
          'feed_kg': pond.name == 'Harvest C' ? 118.0 : 58.0,
        });
        await txn.insert('water_logs', {
          'id': _uuid.v4(),
          'pond_id': pond.id,
          'checked_at': DateTime.now().toIso8601String(),
          'temperature': 30.4,
          'dissolved_oxygen': pond.name == 'Grow-out B' ? 3.8 : 5.2,
          'ph': 7.8,
          'ammonia': pond.name == 'Grow-out B' ? 0.7 : 0.2,
          'nitrite': 0.3,
        });
      }
    });
  }

  Future<void> upsertUserLogin(String phone, String role) async {
    final db = await database;
    await db.insert(
      'users',
      {
        'phone': phone,
        'role': role,
        'last_login_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }



  Future<String> createFarmWithFirstPond({
    required String farmerName,
    required String farmerPhone,
    required String village,
    required String farmName,
    required String location,
    required String pondName,
    required double areaSqm,
    required double depthM,
    required int initialStock,
    required DateTime stockingDate,
  }) async {
    final db = await database;
    final farmer = Farmer(
      id: _uuid.v4(),
      name: farmerName.trim(),
      phone: farmerPhone.trim(),
      village: village.trim(),
      createdAt: DateTime.now(),
    );
    final farm = Farm(
      id: _uuid.v4(),
      farmerId: farmer.id,
      name: farmName.trim(),
      location: location.trim(),
      layoutWidth: 360,
      layoutHeight: 520,
    );
    final pond = Pond(
      id: _uuid.v4(),
      farmId: farm.id,
      name: pondName.trim(),
      areaSqm: areaSqm,
      initialStock: initialStock,
      stockingDate: stockingDate,
      x: 0.12,
      y: 0.12,
      width: 0.76,
      height: 0.32,
    );

    await db.transaction((txn) async {
      await txn.insert('farmers', farmer.toMap());
      await txn.insert('farms', farm.toMap());
      await txn.insert('ponds', pond.toMap());
      await txn.insert('water_logs', {
        'id': _uuid.v4(),
        'pond_id': pond.id,
        'checked_at': DateTime.now().toIso8601String(),
        'temperature': 30.0,
        'dissolved_oxygen': 5.0,
        'ph': 7.8,
        'ammonia': 0.2,
        'nitrite': 0.2,
      });
    });
    return farm.id;
  }

  Future<void> addFeedLog({
    required String pondId,
    required double feedKg,
    required DateTime fedAt,
  }) async {
    final db = await database;
    await db.insert('feed_logs', {
      'id': _uuid.v4(),
      'pond_id': pondId,
      'fed_at': fedAt.toIso8601String(),
      'feed_kg': feedKg,
    });
  }

  Future<void> addSamplingLog({
    required String pondId,
    required int countPerKg,
    required double dailyFeedKg,
    required DateTime sampledAt,
  }) async {
    final db = await database;
    final pondRows = await db.query('ponds', where: 'id = ?', whereArgs: [pondId], limit: 1);
    final pond = Pond.fromMap(pondRows.single);
    final abw = 1000 / countPerKg;
    final feedPercent = _feedPercentForAbw(abw);
    final estimatedBiomass = dailyFeedKg > 0 ? dailyFeedKg / (feedPercent / 100) : pond.initialStock * abw / 1000;
    final presentSurvival = estimatedBiomass * 1000 / abw;
    final survivalPct = pond.initialStock <= 0 ? 0.0 : presentSurvival / pond.initialStock * 100;
    final biomass = presentSurvival * abw / 1000;
    await db.insert('sampling_logs', {
      'id': _uuid.v4(),
      'pond_id': pondId,
      'sampled_at': sampledAt.toIso8601String(),
      'abw_g': abw,
      'survival_pct': survivalPct,
      'biomass_kg': biomass,
      'feed_pct': feedPercent,
    });
  }

  Future<void> addWaterLog({
    required String pondId,
    required DateTime checkedAt,
    required double temperature,
    required double dissolvedOxygen,
    required double ph,
    required double ammonia,
    required double nitrite,
  }) async {
    final db = await database;
    await db.insert('water_logs', {
      'id': _uuid.v4(),
      'pond_id': pondId,
      'checked_at': checkedAt.toIso8601String(),
      'temperature': temperature,
      'dissolved_oxygen': dissolvedOxygen,
      'ph': ph,
      'ammonia': ammonia,
      'nitrite': nitrite,
    });
  }

  double _feedPercentForAbw(double abw) {
    if (abw < 2) return 6.5;
    if (abw < 5) return 5.2;
    if (abw < 10) return 4.2;
    if (abw < 20) return 3.2;
    if (abw < 30) return 2.5;
    return 2.0;
  }


  Future<List<Farmer>> farmers() async {
    final db = await database;
    final rows = await db.query('farmers', orderBy: 'created_at DESC');
    return rows.map(Farmer.fromMap).toList();
  }

  Future<List<Farm>> farmsForFarmer(String farmerId) async {
    final db = await database;
    final rows = await db.query('farms', where: 'farmer_id = ?', whereArgs: [farmerId]);
    return rows.map(Farm.fromMap).toList();
  }

  Future<Farm> farm(String id) async {
    final db = await database;
    final rows = await db.query('farms', where: 'id = ?', whereArgs: [id], limit: 1);
    return Farm.fromMap(rows.single);
  }

  Future<List<PondSnapshot>> pondSnapshots(String farmId) async {
    final db = await database;
    final ponds = (await db.query('ponds', where: 'farm_id = ?', whereArgs: [farmId]))
        .map(Pond.fromMap)
        .toList();
    final snapshots = <PondSnapshot>[];
    for (final pond in ponds) {
      final sampling = await db.query(
        'sampling_logs',
        where: 'pond_id = ?',
        whereArgs: [pond.id],
        orderBy: 'sampled_at DESC',
        limit: 1,
      );
      final feed = await db.rawQuery(
        'SELECT COALESCE(SUM(feed_kg), 0) AS total FROM feed_logs WHERE pond_id = ?',
        [pond.id],
      );
      final water = await db.query(
        'water_logs',
        where: 'pond_id = ?',
        whereArgs: [pond.id],
        orderBy: 'checked_at DESC',
        limit: 1,
      );
      final sample = sampling.isEmpty ? <String, Object?>{} : sampling.first;
      final waterRow = water.isEmpty ? <String, Object?>{} : water.first;
      final dissolvedOxygen = (waterRow['dissolved_oxygen'] as num?)?.toDouble() ?? 5;
      final ammonia = (waterRow['ammonia'] as num?)?.toDouble() ?? 0;
      final survival = (sample['survival_pct'] as num?)?.toDouble() ?? 0;
      final risk = dissolvedOxygen < 4.0 || ammonia > 0.5 || survival < 75 ? 'Attention' : 'Healthy';
      snapshots.add(PondSnapshot(
        pond: pond,
        latestAbw: (sample['abw_g'] as num?)?.toDouble() ?? 0,
        latestSurvival: survival,
        biomassKg: (sample['biomass_kg'] as num?)?.toDouble() ?? 0,
        feedKg: (feed.first['total'] as num).toDouble(),
        riskLabel: risk,
      ));
    }
    return snapshots;
  }

  Future<List<PondSnapshot>> allPondSnapshots() async {
    final db = await database;
    final farmRows = await db.query('farms', orderBy: 'name');
    final snapshots = <PondSnapshot>[];
    for (final row in farmRows) {
      snapshots.addAll(await pondSnapshots(row['id'] as String));
    }
    return snapshots;
  }

  Future<PondSnapshot> pondSnapshot(String pondId) async {
    final db = await database;
    final pondRows = await db.query('ponds', where: 'id = ?', whereArgs: [pondId], limit: 1);
    final farmId = Pond.fromMap(pondRows.single).farmId;
    return (await pondSnapshots(farmId)).firstWhere((snapshot) => snapshot.pond.id == pondId);
  }

  Future<CeoMetrics> ceoMetrics() async {
    final db = await database;
    final counts = await Future.wait([
      db.rawQuery('SELECT COUNT(*) AS count FROM farmers'),
      db.rawQuery('SELECT COUNT(*) AS count FROM farms'),
      db.rawQuery('SELECT COUNT(*) AS count FROM ponds'),
    ]);
    final latest = await db.rawQuery('''
      SELECT s.* FROM sampling_logs s
      INNER JOIN (
        SELECT pond_id, MAX(sampled_at) AS latest_sample FROM sampling_logs GROUP BY pond_id
      ) x ON x.pond_id = s.pond_id AND x.latest_sample = s.sampled_at
    ''');
    final water = await db.rawQuery('''
      SELECT w.* FROM water_logs w
      INNER JOIN (
        SELECT pond_id, MAX(checked_at) AS latest_check FROM water_logs GROUP BY pond_id
      ) x ON x.pond_id = w.pond_id AND x.latest_check = w.checked_at
    ''');
    final biomass = latest.fold<double>(0, (sum, row) => sum + (row['biomass_kg'] as num).toDouble());
    final survival = latest.isEmpty
        ? 0.0
        : latest.fold<double>(0, (sum, row) => sum + (row['survival_pct'] as num).toDouble()) / latest.length;
    final riskyPonds = water.where((row) {
      return (row['dissolved_oxygen'] as num).toDouble() < 4 || (row['ammonia'] as num).toDouble() > 0.5;
    }).length;
    return CeoMetrics(
      farmerCount: counts[0].first['count'] as int,
      farmCount: counts[1].first['count'] as int,
      pondCount: counts[2].first['count'] as int,
      totalBiomassKg: biomass,
      averageSurvival: survival,
      riskPondCount: riskyPonds,
    );
  }
}
