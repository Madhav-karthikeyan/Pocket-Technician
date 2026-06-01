import 'dart:math';

import 'local_database.dart';

class OtpResult {
  const OtpResult({required this.phone, required this.debugCode});

  final String phone;
  final String debugCode;
}

class OtpService {
  OtpService(this._database);

  final LocalDatabase _database;
  final Map<String, String> _codes = {};
  final Random _random = Random.secure();

  Future<OtpResult> sendOtp(String rawPhone) async {
    final phone = _normalizePhone(rawPhone);
    if (phone.length < 10) {
      throw ArgumentError('Enter a valid mobile number.');
    }
    final code = (100000 + _random.nextInt(900000)).toString();
    _codes[phone] = code;

    // Production hook: send `code` using a provider such as Firebase Auth,
    // Twilio Verify, AWS SNS, or a local telecom SMS gateway. The app remains
    // Supabase-free because verification state and user records are stored on device.
    return OtpResult(phone: phone, debugCode: code);
  }

  Future<bool> verifyOtp({
    required String phone,
    required String otp,
    String role = 'CEO',
  }) async {
    final normalized = _normalizePhone(phone);
    if (_codes[normalized] != otp.trim()) return false;
    await _database.upsertUserLogin(normalized, role);
    _codes.remove(normalized);
    return true;
  }

  String _normalizePhone(String input) {
    final trimmed = input.trim();
    if (trimmed.startsWith('+')) return trimmed.replaceAll(' ', '');
    final digits = trimmed.replaceAll(RegExp('[^0-9]'), '');
    return digits.length == 10 ? '+91$digits' : '+$digits';
  }
}
