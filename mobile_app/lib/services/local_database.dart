import 'dart:math' as math;

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
      version: 2,
      onCreate: _createSchema,
      onUpgrade: (db, oldVersion, newVersion) async {
        await db.execute('DROP TABLE IF EXISTS reports');
        await db.execute('DROP TABLE IF EXISTS water_logs');
        await db.execute('DROP TABLE IF EXISTS feed_logs');
        await db.execute('DROP TABLE IF EXISTS sampling_logs');
        await db.execute('DROP TABLE IF EXISTS ponds');
        await db.execute('DROP TABLE IF EXISTS farms');
        await db.execute('DROP TABLE IF EXISTS farmers');
        await db.execute('DROP TABLE IF EXISTS users');
        await _createSchema(db, newVersion);
      },
    );
    _db = db;
    await _seedIfEmpty(db);
    return db;
  }

  Future<void> _createSchema(Database db, int version) async {
    await db.execute('PRAGMA foreign_keys = ON');
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
        depth_m REAL NOT NULL,
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
        weekly_growth_g REAL NOT NULL DEFAULT 0,
        adg_g REAL NOT NULL DEFAULT 0,
        weekly_biomass_gain_kg REAL NOT NULL DEFAULT 0,
        weekly_fcr REAL NOT NULL DEFAULT 0,
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
    await db.execute('''
      CREATE TABLE reports(
        id TEXT PRIMARY KEY,
        pond_id TEXT NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(pond_id) REFERENCES ponds(id) ON DELETE CASCADE
      )
    ''');
  }

  Future<void> _seedIfEmpty(Database db) async {
    final count = Sqflite.firstIntValue(await db.rawQuery('SELECT COUNT(*) FROM farmers')) ?? 0;
    if (count > 0) return;

    final farmer = Farmer(id: _uuid.v4(), name: 'Demo Farmer', phone: '+919999999999', village: 'Coastal Village', createdAt: DateTime.now());
    final farm = Farm(id: _uuid.v4(), farmerId: farmer.id, name: 'Demo Farm', location: 'East Block', layoutWidth: 360, layoutHeight: 520);
    final ponds = [
      Pond(id: _uuid.v4(), farmId: farm.id, name: 'Nursery A', areaSqm: 4200, depthM: 1.2, initialStock: 125000, stockingDate: DateTime(2026, 1, 8), x: 0.08, y: 0.08, width: 0.38, height: 0.28),
      Pond(id: _uuid.v4(), farmId: farm.id, name: 'Grow-out B', areaSqm: 6200, depthM: 1.3, initialStock: 210000, stockingDate: DateTime(2026, 1, 14), x: 0.54, y: 0.10, width: 0.38, height: 0.34),
      Pond(id: _uuid.v4(), farmId: farm.id, name: 'Harvest C', areaSqm: 5800, depthM: 1.4, initialStock: 190000, stockingDate: DateTime(2026, 1, 1), x: 0.16, y: 0.52, width: 0.70, height: 0.32),
    ];

    await db.transaction((txn) async {
      await txn.insert('farmers', farmer.toMap());
      await txn.insert('farms', farm.toMap());
      for (final pond in ponds) {
        await txn.insert('ponds', pond.toMap());
        final olderAbw = pond.name == 'Harvest C' ? 25.0 : 10.8;
        final latestAbw = pond.name == 'Harvest C' ? 31.5 : 14.2;
        final latestSurvival = pond.name == 'Grow-out B' ? 71.4 : 84.6;
        final latestBiomass = pond.name == 'Harvest C' ? 5065.0 : 1510.0;
        await txn.insert('sampling_logs', _samplingMap(pond.id, DateTime.now().subtract(const Duration(days: 10)), olderAbw, 88, latestBiomass * .78, 3.4, 0, 0, 0, 0));
        await txn.insert('sampling_logs', _samplingMap(pond.id, DateTime.now().subtract(const Duration(days: 3)), latestAbw, latestSurvival, latestBiomass, pond.name == 'Harvest C' ? 2.2 : 3.8, latestAbw - olderAbw, (latestAbw - olderAbw) / 7, latestBiomass * .22, 1.32));
        await txn.insert('feed_logs', {'id': _uuid.v4(), 'pond_id': pond.id, 'fed_at': DateTime.now().toIso8601String(), 'feed_kg': pond.name == 'Harvest C' ? 118.0 : 58.0});
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

  Map<String, Object?> _samplingMap(String pondId, DateTime sampledAt, double abw, double survival, double biomass, double feedPct, double growth, double adg, double biomassGain, double fcr) => {
        'id': _uuid.v4(),
        'pond_id': pondId,
        'sampled_at': sampledAt.toIso8601String(),
        'abw_g': abw,
        'survival_pct': survival,
        'biomass_kg': biomass,
        'feed_pct': feedPct,
        'weekly_growth_g': growth,
        'adg_g': adg,
        'weekly_biomass_gain_kg': biomassGain,
        'weekly_fcr': fcr,
      };

  Future<void> upsertUserLogin(String phone, String role) async {
    final db = await database;
    await db.insert('users', {'phone': phone, 'role': role, 'last_login_at': DateTime.now().toIso8601String()}, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Farmer>> farmers() async {
    final db = await database;
    return (await db.query('farmers', orderBy: 'created_at DESC')).map(Farmer.fromMap).toList();
  }

  Future<List<Farm>> farmsForFarmer(String farmerId) async {
    final db = await database;
    return (await db.query('farms', where: 'farmer_id = ?', whereArgs: [farmerId])).map(Farm.fromMap).toList();
  }

  Future<Farm> farm(String id) async {
    final db = await database;
    final rows = await db.query('farms', where: 'id = ?', whereArgs: [id], limit: 1);
    return Farm.fromMap(rows.single);
  }

  Future<List<PondSnapshot>> allPondSnapshots() async {
    final db = await database;
    final farms = await db.query('farms');
    final snapshots = <PondSnapshot>[];
    for (final farm in farms) {
      snapshots.addAll(await pondSnapshots(farm['id'] as String));
    }
    return snapshots;
  }

  Future<List<PondSnapshot>> pondSnapshots(String farmId) async {
    final db = await database;
    final ponds = (await db.query('ponds', where: 'farm_id = ?', whereArgs: [farmId])).map(Pond.fromMap).toList();
    final snapshots = <PondSnapshot>[];
    for (final pond in ponds) {
      snapshots.add(await _snapshotForPond(db, pond));
    }
    return snapshots;
  }

  Future<PondSnapshot> _snapshotForPond(Database db, Pond pond) async {
    final samplingRows = await db.query('sampling_logs', where: 'pond_id = ?', whereArgs: [pond.id], orderBy: 'sampled_at DESC', limit: 1);
    final feed = await db.rawQuery('SELECT COALESCE(SUM(feed_kg), 0) AS total FROM feed_logs WHERE pond_id = ?', [pond.id]);
    final waterRows = await db.query('water_logs', where: 'pond_id = ?', whereArgs: [pond.id], orderBy: 'checked_at DESC', limit: 1);
    final latestSampling = samplingRows.isEmpty ? null : SamplingLog.fromMap(samplingRows.first);
    final latestWater = waterRows.isEmpty ? null : WaterLog.fromMap(waterRows.first);
    final dissolvedOxygen = latestWater?.dissolvedOxygen ?? 5;
    final ammonia = latestWater?.ammonia ?? 0;
    final nitrite = latestWater?.nitrite ?? 0;
    final survival = latestSampling?.survivalPct ?? 0;
    final density = pond.areaSqm * pond.depthM <= 0 ? 0 : (latestSampling?.biomassKg ?? 0) / (pond.areaSqm * pond.depthM);
    final risk = dissolvedOxygen < 4.0 || ammonia > 0.5 || nitrite > 0.5 || survival < 75 || density > 0.65 ? 'Attention' : 'Healthy';
    return PondSnapshot(
      pond: pond,
      latestAbw: latestSampling?.abwG ?? 0,
      latestSurvival: survival,
      biomassKg: latestSampling?.biomassKg ?? 0,
      feedKg: (feed.first['total'] as num).toDouble(),
      riskLabel: risk,
      latestWater: latestWater,
      latestSampling: latestSampling,
    );
  }

  Future<PondSnapshot> pondSnapshot(String pondId) async {
    final db = await database;
    final pondRows = await db.query('ponds', where: 'id = ?', whereArgs: [pondId], limit: 1);
    return _snapshotForPond(db, Pond.fromMap(pondRows.single));
  }

  Future<PondDetailBundle> pondDetail(String pondId) async {
    final db = await database;
    return PondDetailBundle(
      snapshot: await pondSnapshot(pondId),
      sampling: (await db.query('sampling_logs', where: 'pond_id = ?', whereArgs: [pondId], orderBy: 'sampled_at ASC')).map(SamplingLog.fromMap).toList(),
      feed: (await db.query('feed_logs', where: 'pond_id = ?', whereArgs: [pondId], orderBy: 'fed_at DESC')).map(FeedLog.fromMap).toList(),
      water: (await db.query('water_logs', where: 'pond_id = ?', whereArgs: [pondId], orderBy: 'checked_at DESC')).map(WaterLog.fromMap).toList(),
      reports: (await db.query('reports', where: 'pond_id = ?', whereArgs: [pondId], orderBy: 'created_at DESC')).map(LocalReport.fromMap).toList(),
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
    final farmer = Farmer(id: _uuid.v4(), name: farmerName.trim().isEmpty ? 'Farmer' : farmerName.trim(), phone: farmerPhone.trim(), village: village.trim(), createdAt: DateTime.now());
    final farm = Farm(id: _uuid.v4(), farmerId: farmer.id, name: farmName.trim().isEmpty ? 'Farm' : farmName.trim(), location: location.trim(), layoutWidth: 360, layoutHeight: 520);
    final pond = Pond(id: _uuid.v4(), farmId: farm.id, name: pondName.trim().isEmpty ? 'Pond 1' : pondName.trim(), areaSqm: areaSqm, depthM: depthM <= 0 ? 1 : depthM, initialStock: initialStock, stockingDate: stockingDate, x: .12, y: .12, width: .76, height: .34);
    await db.transaction((txn) async {
      await txn.insert('farmers', farmer.toMap());
      await txn.insert('farms', farm.toMap());
      await txn.insert('ponds', pond.toMap());
    });
    return farm.id;
  }

  Future<void> addFeedLog({required String pondId, required double feedKg, required DateTime fedAt}) async {
    final db = await database;
    await db.insert('feed_logs', {'id': _uuid.v4(), 'pond_id': pondId, 'fed_at': fedAt.toIso8601String(), 'feed_kg': feedKg});
  }

  Future<void> addSamplingLog({required String pondId, required int countPerKg, required double dailyFeedKg, required DateTime sampledAt}) async {
    final db = await database;
    final pond = Pond.fromMap((await db.query('ponds', where: 'id = ?', whereArgs: [pondId], limit: 1)).single);
    final previousRows = await db.query('sampling_logs', where: 'pond_id = ?', whereArgs: [pondId], orderBy: 'sampled_at DESC', limit: 1);
    final previous = previousRows.isEmpty ? null : SamplingLog.fromMap(previousRows.first);
    final safeCount = math.max(1, countPerKg);
    final abw = 1000 / safeCount;
    final estimatedAnimalsFed = dailyFeedKg <= 0 ? pond.initialStock * .8 : (dailyFeedKg * 1000) / math.max(abw * 0.035, 1);
    final survival = (estimatedAnimalsFed / math.max(pond.initialStock, 1) * 100).clamp(1, 100).toDouble();
    final biomass = pond.initialStock * (survival / 100) * abw / 1000;
    final feedPct = biomass <= 0 ? 0 : dailyFeedKg / biomass * 100;
    final days = previous == null ? 0 : math.max(1, sampledAt.difference(previous.sampledAt).inDays);
    final growth = previous == null ? 0 : abw - previous.abwG;
    final biomassGain = previous == null ? 0 : biomass - previous.biomassKg;
    final fcr = biomassGain <= 0 ? 0 : dailyFeedKg * days / biomassGain;
    await db.insert('sampling_logs', _samplingMap(pondId, sampledAt, abw, survival, biomass, feedPct, growth, days == 0 ? 0 : growth / days, biomassGain, fcr));
  }

  Future<void> addWaterLog({required String pondId, required DateTime checkedAt, required double temperature, required double dissolvedOxygen, required double ph, required double ammonia, required double nitrite}) async {
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

  Future<void> updatePondLayout({required String pondId, required double x, required double y, required double width, required double height}) async {
    final db = await database;
    await db.update('ponds', {'layout_x': x, 'layout_y': y, 'layout_w': width, 'layout_h': height}, where: 'id = ?', whereArgs: [pondId]);
  }

  Future<String> createLocalReport(String pondId) async {
    final db = await database;
    final detail = await pondDetail(pondId);
    final snapshot = detail.snapshot;
    final water = snapshot.latestWater;
    final sample = snapshot.latestSampling;
    final title = '${snapshot.pond.name} technician report';
    final body = '''DOC: ${DateTime.now().difference(snapshot.pond.stockingDate).inDays + 1}
ABW: ${snapshot.latestAbw.toStringAsFixed(2)} g
Survival: ${snapshot.latestSurvival.toStringAsFixed(1)}%
Biomass: ${snapshot.biomassKg.toStringAsFixed(1)} kg
Biomass density: ${snapshot.biomassDensityKgM3.toStringAsFixed(3)} kg/m³
Feed total: ${snapshot.feedKg.toStringAsFixed(1)} kg
Weekly growth: ${(sample?.weeklyGrowthG ?? 0).toStringAsFixed(2)} g
Weekly FCR: ${(sample?.weeklyFcr ?? 0).toStringAsFixed(2)}
Water: DO ${(water?.dissolvedOxygen ?? 0).toStringAsFixed(1)}, pH ${(water?.ph ?? 0).toStringAsFixed(1)}, ammonia ${(water?.ammonia ?? 0).toStringAsFixed(2)}, nitrite ${(water?.nitrite ?? 0).toStringAsFixed(2)}
Recommendation: ${snapshot.riskLabel == 'Healthy' ? 'Continue current sampling, feed tray checks, and water monitoring.' : 'Review aeration, ammonia control, feed tray leftovers, and survival before increasing feed.'}

Stored locally on this phone. No Supabase/cloud upload is used.''';
    final id = _uuid.v4();
    await db.insert('reports', {'id': id, 'pond_id': pondId, 'title': title, 'body': body, 'created_at': DateTime.now().toIso8601String()});
    return id;
  }

  Future<CeoMetrics> ceoMetrics() async {
    final db = await database;
    final counts = await Future.wait([
      db.rawQuery('SELECT COUNT(*) AS count FROM farmers'),
      db.rawQuery('SELECT COUNT(*) AS count FROM farms'),
      db.rawQuery('SELECT COUNT(*) AS count FROM ponds'),
    ]);
    final snapshots = await allPondSnapshots();
    final biomass = snapshots.fold<double>(0, (sum, item) => sum + item.biomassKg);
    final survival = snapshots.isEmpty ? 0.0 : snapshots.fold<double>(0, (sum, item) => sum + item.latestSurvival) / snapshots.length;
    final riskyPonds = snapshots.where((item) => item.riskLabel != 'Healthy').length;
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
