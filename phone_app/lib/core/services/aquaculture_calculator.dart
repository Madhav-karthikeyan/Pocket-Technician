import 'dart:math' as math;

enum LunarPhase { newMoon, waxingCrescent, waxingGibbous, fullMoon, waningGibbous, waningCrescent }

class SamplingMetrics {
  const SamplingMetrics({required this.doc, required this.count, required this.abw, required this.biomass, required this.presentNumbers, required this.survivalPct, this.weeklyGrowth, this.weeklyAdg, this.weeklyBiomass, this.weeklySurvival, this.weeklyFcr, this.possibleExcessFeedKg = 0});
  final int doc;
  final int count;
  final double abw, biomass, presentNumbers, survivalPct, possibleExcessFeedKg;
  final double? weeklyGrowth, weeklyAdg, weeklyBiomass, weeklySurvival, weeklyFcr;
}

class FeedTrayDecision {
  const FeedTrayDecision(this.trayFeedGramsPerKg, this.checkTimeMinutes, this.nextFeedKg, this.decision);
  final int trayFeedGramsPerKg, checkTimeMinutes;
  final double nextFeedKg;
  final String decision;
}

class FeedingPlan {
  const FeedingPlan({required this.doc, required this.baseFeedKgDay, required this.preSamplingFeedKgDay, required this.survivalAdjustedFeedKgDay, required this.weatherAdjustedFeedKgDay, required this.feedSize, required this.survivalPctUsed, required this.biomassDensityKgM3, required this.profitTodayEstimate, required this.recommendation});
  final int doc;
  final double baseFeedKgDay, preSamplingFeedKgDay, survivalAdjustedFeedKgDay, weatherAdjustedFeedKgDay, survivalPctUsed, biomassDensityKgM3, profitTodayEstimate;
  final String feedSize, recommendation;
}

class VirtualFarmResult {
  const VirtualFarmResult({required this.biomassKg, required this.revenue, required this.feedCost, required this.profit, required this.growthProjection, required this.survivalProjection, required this.pondHealthScore, required this.stressIndex});
  final double biomassKg, revenue, feedCost, profit, pondHealthScore, stressIndex;
  final List<double> growthProjection, survivalProjection;
}

class AquacultureCalculator {
  static const Map<int, double> feed100kByCount = {1000: 10.0, 900: 11.1, 800: 12.5, 700: 14.3, 600: 16.7, 500: 20.0, 400: 25.0, 300: 33.3, 200: 50.0, 100: 100.0};

  int doc(DateTime stockingDate, DateTime sampleDate) => sampleDate.difference(DateTime(stockingDate.year, stockingDate.month, stockingDate.day)).inDays + 1;
  int nearestCount(int count) => feed100kByCount.keys.reduce((a, b) => (a - count).abs() <= (b - count).abs() ? a : b);
  double abwFromCount(int count) => 1000 / nearestCount(count);
  double biomass(double presentNumbers, double abwGrams) => presentNumbers * abwGrams / 1000;
  double survival(double presentNumbers, double initialStock) => initialStock <= 0 ? 0 : presentNumbers / initialStock * 100;
  double adg(double currentAbw, double previousAbw, int days) => days <= 0 ? 0 : (currentAbw - previousAbw) / days;
  double fcr(double feedUsed, double biomassGain) => biomassGain <= 0 ? double.nan : feedUsed / biomassGain;

  SamplingMetrics sampling({required int countInput, required double dailyFeedKg, required double initialStock, required DateTime stockingDate, required DateTime samplingDate, SamplingMetrics? previous, double? intervalFeedUsed}) {
    final count = nearestCount(countInput);
    final abw = abwFromCount(count);
    final d = doc(stockingDate, samplingDate);
    final currentSurvival = dailyFeedKg / (feed100kByCount[count] ?? 10) * 100000;
    final bio = biomass(currentSurvival, abw);
    final present = bio / abw * 1000;
    final surv = survival(present, initialStock);
    final maxFeedAllowed = (feed100kByCount[count] ?? 10) * (initialStock / 100000);
    if (previous == null) return SamplingMetrics(doc: d, count: count, abw: _r(abw, 2), biomass: _r(bio, 1), presentNumbers: _r(present, 1), survivalPct: _r(surv, 2), possibleExcessFeedKg: surv > 100 ? _r(dailyFeedKg - maxFeedAllowed, 2) : 0);
    final gap = math.max(1, d - previous.doc);
    final wg = abw - previous.abw;
    final bg = bio - previous.biomass;
    return SamplingMetrics(doc: d, count: count, abw: _r(abw, 2), biomass: _r(bio, 1), presentNumbers: _r(present, 1), survivalPct: _r(surv, 2), possibleExcessFeedKg: surv > 100 ? _r(dailyFeedKg - maxFeedAllowed, 2) : 0, weeklyGrowth: _r(wg * 7 / gap, 2), weeklyAdg: _r(wg / gap, 3), weeklyBiomass: _r(bg * 7 / gap, 1), weeklySurvival: _r(surv - previous.survivalPct, 2), weeklyFcr: bg > 0 ? _r((intervalFeedUsed ?? dailyFeedKg * gap) / bg, 2) : null);
  }

  FeedTrayDecision feedTray(double abw, double lastFeed, double trayLeft, int consumedMinutes) {
    final trayFeed = abw < 5 ? 5 : (abw <= 10 ? 10 : (abw > 25 ? 12 : 10));
    final checkTime = abw < 5 ? 120 : 90;
    var nextFeed = lastFeed;
    var decision = 'Maintain feed';
    if (trayLeft >= 10) { nextFeed -= 1; decision = 'Reduce 1 kg'; } else if (trayLeft <= 0) { nextFeed += 1; decision = 'Increase 1 kg'; if (consumedMinutes <= 30) { nextFeed += 1; decision = 'Increase 2 kg (Strong response)'; }}
    return FeedTrayDecision(trayFeed, checkTime, math.max(0, nextFeed).toDouble(), decision);
  }

  double weatherFeedFactor({required double temperatureC, required double rainMm, double windKmh = 0}) => temperatureC > 34 ? 0.85 : (temperatureC < 26 ? 0.75 : (rainMm > 20 ? 0.80 : 1.0));
  String feedSizeForDoc(int doc) => doc <= 10 ? 'Powder / crumble 0.3–0.5 mm' : doc <= 25 ? 'Crumble 0.5–0.8 mm' : doc <= 45 ? 'Pellet 1.0–1.2 mm' : doc <= 70 ? 'Pellet 1.4–1.8 mm' : 'Pellet 2.0 mm+';
  FeedingPlan feedingPlan({required int doc, required double initialStock, double survivalPct = 100, double weatherFactor = 1, double biomassKg = 0, double areaM2 = 0, double depthM = 0, double accumulatedFeedKg = 0, double feedPrice = 90, double shrimpPrice = 320, double overhead = 0}) { final base = initialStock > 0 ? initialStock / 10000 : 0; final pre = base + math.max(0, doc - 1) * 0.25; final surv = (survivalPct / 100).clamp(0.01, 1.0); final sf = pre * surv; final wf = sf * weatherFactor.clamp(0.5, 1.0); final vol = areaM2 * depthM; final density = vol > 0 ? biomassKg / vol : 0.0; return FeedingPlan(doc: doc, baseFeedKgDay: _r(base, 3), preSamplingFeedKgDay: _r(pre, 3), survivalAdjustedFeedKgDay: _r(sf, 3), weatherAdjustedFeedKgDay: _r(wf, 3), feedSize: feedSizeForDoc(doc), survivalPctUsed: _r(survivalPct, 2), biomassDensityKgM3: _r(density, 3), profitTodayEstimate: _r(biomassKg * shrimpPrice - accumulatedFeedKg * feedPrice - overhead, 0), recommendation: density > 0.65 ? 'Carrying capacity is tight; correct aeration/water before pushing feed.' : 'Feed path acceptable; confirm tray, growth, survival, and weather.'); }
  VirtualFarmResult virtualFarm({required double pondArea, required double abw, required double stockingDensity, required int doc, required double survival, required double feedPrice, required double shrimpPrice, int horizonDays = 45}) { final present = pondArea * stockingDensity * survival / 100; final bio = biomass(present, abw); final feedCost = bio * 1.5 * feedPrice; final revenue = bio * shrimpPrice; final growth = List<double>.generate(horizonDays + 1, (i) => _r(abw + i * (doc < 60 ? 0.18 : 0.12), 2)); final surv = List<double>.generate(horizonDays + 1, (i) => _r(math.max(0, survival - i * 0.03), 2)); final stress = (100 - survival).clamp(0, 100).toDouble(); return VirtualFarmResult(biomassKg: _r(bio, 2), revenue: _r(revenue, 2), feedCost: _r(feedCost, 2), profit: _r(revenue - feedCost, 2), growthProjection: growth, survivalProjection: surv, pondHealthScore: _r((survival * .55 + (100 - stress) * .25 + math.min(100, abw * 3) * .20), 2), stressIndex: _r(stress, 2)); }
  double rankingScore({required double survival, required double fcr, required double biomass}) => _r(survival * .4 + (1 / fcr) * 100 * .3 + biomass * .3 / 10, 2);
  String grade(double score) => score > 85 ? 'A' : (score > 70 ? 'B' : 'C');
  LunarPhase lunarPhase(DateTime date) { final lp = 2551443; final now = date.millisecondsSinceEpoch ~/ 1000; final newMoon = DateTime.utc(2001, 1, 24, 13, 7).millisecondsSinceEpoch ~/ 1000; final phase = ((now - newMoon) % lp) / lp * 29.530588853; if (phase < 1.84566 || phase >= 27.68493) return LunarPhase.newMoon; if (phase < 7.38265) return LunarPhase.waxingCrescent; if (phase < 14.76529) return LunarPhase.waxingGibbous; if (phase < 16.61096) return LunarPhase.fullMoon; if (phase < 23.99361) return LunarPhase.waningGibbous; return LunarPhase.waningCrescent; }
  static double _r(double v, int p) { final m = math.pow(10, p); return (v * m).round() / m; }
}
