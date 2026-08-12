import 'package:flutter/material.dart';

class SubtleOceanTheme {
  static const deepOcean = Color(0xFF0B4F6C);
  static const oceanTeal = Color(0xFF0F7B8C);
  static const seafoam = Color(0xFF4ECDC4);
  static const coral = Color(0xFFFF6B6B);
  static const pearlWhite = Color(0xFFF7FAFC);
  static const sand = Color(0xFFE8DCC4);

  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(seedColor: oceanTeal, primary: deepOcean, secondary: seafoam, tertiary: coral, surface: pearlWhite);
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: pearlWhite,
      fontFamily: 'Inter',
      cardTheme: CardThemeData(elevation: 0, shadowColor: deepOcean.withValues(alpha: .14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20))),
      inputDecorationTheme: InputDecorationTheme(filled: true, fillColor: Colors.white, border: OutlineInputBorder(borderRadius: BorderRadius.circular(20)), contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 18)),
      filledButtonTheme: FilledButtonThemeData(style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(52), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)))),
    );
  }
}
