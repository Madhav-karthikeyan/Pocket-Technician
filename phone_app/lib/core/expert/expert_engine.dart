import 'dart:math' as math;

import '../services/aquaculture_calculator.dart';

enum ExpertSeverity { critical, high, medium, low, info }
enum ExpertConfidence { high, moderate, low, insufficientData }
enum ExpertDomain { feeding, waterQuality, growth, disease, weather, stress, overall }
enum RuleStatus { active, retired, draft }
enum LogicalOperator { and, or, not, any, all, atLeast, atMost }

class ExpertContext {
  const ExpertContext({
    required this.farmName,
    required this.pondName,
    required this.doc,
    required this.pondAreaM2,
    required this.depthM,
    required this.initialStock,
    this.abwG,
    this.biomassKg,
    this.survivalPct,
    this.adgG,
    this.weeklyFcr,
    this.feedTodayKg,
    this.feed7DayAverageKg,
    this.baseFeedingPlan,
    this.temperatureC,
    this.dissolvedOxygenMgL,
    this.ph,
    this.salinityPpt,
    this.ammoniaMgL,
    this.rainForecastMm,
    this.windKmh,
    this.trayLeftoverPct,
    this.consumptionMinutes,
    this.previousDissolvedOxygen,
    this.previousSurvivalPct,
    this.previousAbwG,
    this.recentFeedKg = const [],
    this.recentTrayLeftoverPct = const [],
    this.recentFcr = const [],
    this.symptoms = const [],
  });

  final String farmName;
  final String pondName;
  final int doc;
  final double pondAreaM2;
  final double depthM;
  final int initialStock;
  final double? abwG;
  final double? biomassKg;
  final double? survivalPct;
  final double? adgG;
  final double? weeklyFcr;
  final double? feedTodayKg;
  final double? feed7DayAverageKg;
  final FeedingPlan? baseFeedingPlan;
  final double? temperatureC;
  final double? dissolvedOxygenMgL;
  final double? ph;
  final double? salinityPpt;
  final double? ammoniaMgL;
  final double? rainForecastMm;
  final double? windKmh;
  final double? trayLeftoverPct;
  final int? consumptionMinutes;
  final double? previousDissolvedOxygen;
  final double? previousSurvivalPct;
  final double? previousAbwG;
  final List<double> recentFeedKg;
  final List<double> recentTrayLeftoverPct;
  final List<double> recentFcr;
  final List<String> symptoms;

  double get biomassDensityKgM3 {
    final volume = pondAreaM2 * depthM;
    if (volume <= 0 || biomassKg == null) return 0;
    return biomassKg! / volume;
  }
}

class ExpertRule {
  const ExpertRule({required this.id, required this.name, required this.version, required this.domain, required this.description, required this.severity, required this.priority, required this.effectiveDate, required this.status, this.dependencies = const []});
  final String id;
  final String name;
  final String version;
  final ExpertDomain domain;
  final String description;
  final ExpertSeverity severity;
  final int priority;
  final DateTime effectiveDate;
  final RuleStatus status;
  final List<String> dependencies;
}

class ExpertFinding {
  const ExpertFinding({required this.rule, required this.title, required this.evidence, required this.reasoningChain, required this.actions, required this.confidence, this.feedAdjustmentFactor});
  final ExpertRule rule;
  final String title;
  final List<String> evidence;
  final List<String> reasoningChain;
  final List<String> actions;
  final ExpertConfidence confidence;
  final double? feedAdjustmentFactor;
}

class ExpertAssessment {
  const ExpertAssessment({required this.pondName, required this.overallSeverity, required this.confidence, required this.findings, required this.riskScores, required this.summary, required this.finalSuggestedFeedKg});
  final String pondName;
  final ExpertSeverity overallSeverity;
  final ExpertConfidence confidence;
  final List<ExpertFinding> findings;
  final Map<ExpertDomain, int> riskScores;
  final String summary;
  final double? finalSuggestedFeedKg;

  bool get hasFindings => findings.isNotEmpty;
}

class ExpertKnowledgeBase {
  static final rules = <ExpertRule>[
    ExpertRule(id: 'WQ_DO_001', name: 'Low DO Risk', version: '1.0.0', domain: ExpertDomain.waterQuality, description: 'Dissolved oxygen below safe threshold.', severity: ExpertSeverity.high, priority: 90, effectiveDate: DateTime(2026, 8, 12), status: RuleStatus.active),
    ExpertRule(id: 'STRESS_TEMP_DO_BIOMASS_FEED_001', name: 'High biomass low DO feeding stress', version: '1.0.0', domain: ExpertDomain.stress, description: 'Compound environmental and feeding stress.', severity: ExpertSeverity.critical, priority: 100, effectiveDate: DateTime(2026, 8, 12), status: RuleStatus.active, dependencies: ['WQ_DO_001']),
    ExpertRule(id: 'FEED_TRAY_LEFTOVER_001', name: 'Tray leftover overfeeding risk', version: '1.0.0', domain: ExpertDomain.feeding, description: 'Tray leftover indicates reduced feed response.', severity: ExpertSeverity.medium, priority: 70, effectiveDate: DateTime(2026, 8, 12), status: RuleStatus.active),
    ExpertRule(id: 'WEATHER_RAIN_001', name: 'Heavy rainfall stress risk', version: '1.0.0', domain: ExpertDomain.weather, description: 'Heavy rain forecast can dilute salinity and reduce feed response.', severity: ExpertSeverity.medium, priority: 65, effectiveDate: DateTime(2026, 8, 12), status: RuleStatus.active),
    ExpertRule(id: 'GROWTH_FCR_001', name: 'Growth and FCR deterioration', version: '1.0.0', domain: ExpertDomain.growth, description: 'Weak growth combined with high FCR.', severity: ExpertSeverity.medium, priority: 60, effectiveDate: DateTime(2026, 8, 12), status: RuleStatus.active),
    ExpertRule(id: 'CONFLICT_FEED_ENV_001', name: 'Conflicting feeding signals', version: '1.0.0', domain: ExpertDomain.feeding, description: 'Tray suggests increase but environment suggests caution.', severity: ExpertSeverity.high, priority: 95, effectiveDate: DateTime(2026, 8, 12), status: RuleStatus.active),
  ];

  static ExpertRule byId(String id) => rules.firstWhere((rule) => rule.id == id);
}

class AquacultureExpertEngine {
  const AquacultureExpertEngine();

  ExpertAssessment assess(ExpertContext context) {
    final validation = _validate(context);
    if (validation.isNotEmpty) {
      return ExpertAssessment(pondName: context.pondName, overallSeverity: ExpertSeverity.info, confidence: ExpertConfidence.insufficientData, findings: const [], riskScores: _baseScores(), summary: 'Insufficient or invalid data: ${validation.join(', ')}.', finalSuggestedFeedKg: context.baseFeedingPlan?.weatherAdjustedFeedKgDay);
    }

    final findings = <ExpertFinding>[];
    final lowDo = context.dissolvedOxygenMgL != null && context.dissolvedOxygenMgL! < 4;
    final highTemp = context.temperatureC != null && context.temperatureC! > 32;
    final highBiomass = context.biomassDensityKgM3 > 0.65;
    final highFeed = context.feedTodayKg != null && context.feed7DayAverageKg != null && context.feedTodayKg! > context.feed7DayAverageKg! * 1.10;
    final leftoverHigh = context.trayLeftoverPct != null && context.trayLeftoverPct! >= 10;
    final fastConsumption = context.trayLeftoverPct != null && context.trayLeftoverPct! <= 0 && (context.consumptionMinutes ?? 999) <= 30;
    final rainHeavy = (context.rainForecastMm ?? 0) > 20;
    final doDeclining = context.previousDissolvedOxygen != null && context.dissolvedOxygenMgL != null && context.dissolvedOxygenMgL! < context.previousDissolvedOxygen!;
    final growthWeak = context.previousAbwG != null && context.abwG != null && context.abwG! <= context.previousAbwG!;
    final fcrHigh = context.weeklyFcr != null && context.weeklyFcr! > 1.8;

    if (lowDo) findings.add(_lowDo(context, doDeclining));
    if (highTemp && lowDo && highBiomass && (highFeed || leftoverHigh)) findings.add(_compoundStress(context));
    if (leftoverHigh) findings.add(_trayLeftover(context));
    if (rainHeavy) findings.add(_rain(context));
    if (growthWeak && fcrHigh) findings.add(_growth(context));
    if (fastConsumption && (highTemp || lowDo || rainHeavy)) findings.add(_conflict(context));

    final deduped = _dedupe(findings)..sort((a, b) => b.rule.priority.compareTo(a.rule.priority));
    final riskScores = _riskScores(context, deduped);
    final severity = deduped.isEmpty ? ExpertSeverity.low : deduped.first.rule.severity;
    final confidence = _confidence(context, deduped);
    final finalFeed = _finalFeed(context, deduped);
    final summary = deduped.isEmpty ? '${context.pondName} has no active expert warning from available local data.' : '${context.pondName} — ${_label(severity)} risk. Primary concern: ${deduped.first.rule.name}.';

    return ExpertAssessment(pondName: context.pondName, overallSeverity: severity, confidence: confidence, findings: deduped, riskScores: riskScores, summary: summary, finalSuggestedFeedKg: finalFeed);
  }

  List<String> _validate(ExpertContext c) {
    final errors = <String>[];
    if (c.pondAreaM2 <= 0) errors.add('pond area must be greater than 0');
    if (c.initialStock <= 0) errors.add('initial stock must be greater than 0');
    if (c.dissolvedOxygenMgL != null && c.dissolvedOxygenMgL! < 0) errors.add('DO cannot be negative');
    if (c.ph != null && (c.ph! < 0 || c.ph! > 14)) errors.add('pH must be between 0 and 14');
    if (c.abwG != null && c.abwG! < 0) errors.add('ABW cannot be negative');
    if (c.survivalPct != null && (c.survivalPct! < 0 || c.survivalPct! > 150)) errors.add('survival is outside expected range');
    return errors;
  }

  ExpertFinding _lowDo(ExpertContext c, bool declining) => ExpertFinding(rule: ExpertKnowledgeBase.byId('WQ_DO_001'), title: 'Low dissolved oxygen risk', evidence: ['DO = ${c.dissolvedOxygenMgL!.toStringAsFixed(1)} mg/L', if (declining) 'DO is lower than previous reading'], reasoningChain: ['Measured low DO', 'Oxygen stress risk rises', 'Feed response can weaken'], actions: ['Review aeration immediately', 'Recheck DO before increasing feed'], confidence: declining ? ExpertConfidence.high : ExpertConfidence.moderate, feedAdjustmentFactor: .90);
  ExpertFinding _compoundStress(ExpertContext c) => ExpertFinding(rule: ExpertKnowledgeBase.byId('STRESS_TEMP_DO_BIOMASS_FEED_001'), title: 'Elevated environmental/feeding stress', evidence: ['Temperature = ${c.temperatureC!.toStringAsFixed(1)} °C', 'DO = ${c.dissolvedOxygenMgL!.toStringAsFixed(1)} mg/L', 'Biomass density = ${c.biomassDensityKgM3.toStringAsFixed(2)} kg/m³'], reasoningChain: ['High temperature increases stress', 'Low DO reduces feeding safety', 'High biomass increases oxygen demand', 'Overfeeding can increase organic load'], actions: ['Apply calculated feed reduction', 'Increase DO monitoring', 'Review aeration and tray response'], confidence: ExpertConfidence.high, feedAdjustmentFactor: .80);
  ExpertFinding _trayLeftover(ExpertContext c) => ExpertFinding(rule: ExpertKnowledgeBase.byId('FEED_TRAY_LEFTOVER_001'), title: 'Feed tray leftover indicates weaker response', evidence: ['Tray leftover = ${c.trayLeftoverPct!.toStringAsFixed(1)}%'], reasoningChain: ['Leftover feed is above threshold', 'Consumption response is weak', 'Overfeeding risk increases'], actions: ['Reduce or hold feed according to feeding engine', 'Clean tray and reassess next feeding'], confidence: ExpertConfidence.moderate, feedAdjustmentFactor: .90);
  ExpertFinding _rain(ExpertContext c) => ExpertFinding(rule: ExpertKnowledgeBase.byId('WEATHER_RAIN_001'), title: 'Heavy rainfall forecast stress risk', evidence: ['Rain forecast = ${c.rainForecastMm!.toStringAsFixed(1)} mm'], reasoningChain: ['Heavy rain forecast', 'Salinity dilution and water instability risk', 'Feed response may change'], actions: ['Prepare water-quality monitoring', 'Avoid aggressive feed increases before rain'], confidence: ExpertConfidence.moderate, feedAdjustmentFactor: .80);
  ExpertFinding _growth(ExpertContext c) => ExpertFinding(rule: ExpertKnowledgeBase.byId('GROWTH_FCR_001'), title: 'Growth efficiency concern', evidence: ['ABW is not improving versus previous sample', 'Weekly FCR = ${c.weeklyFcr!.toStringAsFixed(2)}'], reasoningChain: ['Growth is weak', 'FCR is elevated', 'Feed conversion efficiency may be deteriorating'], actions: ['Review sampling accuracy', 'Check feed quality, tray response, and water quality'], confidence: ExpertConfidence.moderate);
  ExpertFinding _conflict(ExpertContext c) => ExpertFinding(rule: ExpertKnowledgeBase.byId('CONFLICT_FEED_ENV_001'), title: 'Conflicting feeding signals', evidence: ['Tray response suggests feed increase', 'Environmental condition suggests caution'], reasoningChain: ['Fast tray consumption can support feed increase', 'Environmental stress has higher safety priority', 'Farmer confirmation is required before operational change'], actions: ['Do not automatically increase feed', 'Maintain/reduce feed until DO/weather risk improves', 'Reassess tray response after water check'], confidence: ExpertConfidence.moderate, feedAdjustmentFactor: .95);

  List<ExpertFinding> _dedupe(List<ExpertFinding> findings) {
    final byDomain = <ExpertDomain, ExpertFinding>{};
    for (final finding in findings) {
      final existing = byDomain[finding.rule.domain];
      if (existing == null || finding.rule.priority > existing.rule.priority) byDomain[finding.rule.domain] = finding;
    }
    return byDomain.values.toList();
  }

  Map<ExpertDomain, int> _baseScores() => {for (final d in ExpertDomain.values) d: 100};
  Map<ExpertDomain, int> _riskScores(ExpertContext c, List<ExpertFinding> findings) {
    final scores = _baseScores();
    for (final f in findings) {
      scores[f.rule.domain] = math.max(0, (scores[f.rule.domain] ?? 100) - (f.rule.severity == ExpertSeverity.critical ? 35 : f.rule.severity == ExpertSeverity.high ? 25 : 15));
    }
    scores[ExpertDomain.overall] = (scores.values.reduce((a, b) => a + b) / scores.length).round();
    return scores;
  }

  ExpertConfidence _confidence(ExpertContext c, List<ExpertFinding> findings) {
    if (findings.isEmpty) return ExpertConfidence.low;
    final dataPoints = [c.abwG, c.biomassKg, c.survivalPct, c.feedTodayKg, c.temperatureC, c.dissolvedOxygenMgL, c.trayLeftoverPct].whereType<double>().length;
    if (dataPoints >= 5 && findings.length >= 2) return ExpertConfidence.high;
    if (dataPoints >= 3) return ExpertConfidence.moderate;
    return ExpertConfidence.low;
  }

  double? _finalFeed(ExpertContext c, List<ExpertFinding> findings) {
    final base = c.baseFeedingPlan?.weatherAdjustedFeedKgDay ?? c.feedTodayKg;
    if (base == null) return null;
    var factor = 1.0;
    for (final finding in findings) {
      factor = math.min(factor, finding.feedAdjustmentFactor ?? 1.0);
    }
    return (base * factor * 100).round() / 100;
  }

  String _label(ExpertSeverity s) => s.name.toUpperCase();
}
