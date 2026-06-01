import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'screens/dashboard_screen.dart';
import 'services/database_factory.dart';
import 'screens/farm_layout_screen.dart';
import 'screens/login_screen.dart';
import 'screens/pond_detail_screen.dart';
import 'screens/technician_modules_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDatabaseFactory();
  runApp(const ProviderScope(child: PocketTechnicianApp()));
}

class PocketTechnicianApp extends StatelessWidget {
  const PocketTechnicianApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Pocket Technician',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: const Color(0xFF00A3A3),
        scaffoldBackgroundColor: const Color(0xFFF4F7FB),
        inputDecorationTheme: InputDecorationTheme(border: OutlineInputBorder(borderRadius: BorderRadius.circular(16))),
        cardTheme: CardThemeData(elevation: 0, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24))),
      ),
      routerConfig: _router,
    );
  }
}

final _router = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
    GoRoute(path: '/', redirect: (context, state) => '/dashboard'),
    GoRoute(path: '/dashboard', builder: (context, state) => const DashboardScreen()),
    GoRoute(path: '/modules', builder: (context, state) => const TechnicianModulesScreen()),
    GoRoute(
      path: '/farms/:farmId',
      builder: (context, state) => FarmLayoutScreen(farmId: state.pathParameters['farmId']!),
    ),
    GoRoute(
      path: '/ponds/:pondId',
      builder: (context, state) => PondDetailScreen(pondId: state.pathParameters['pondId']!),
    ),
  ],
);
