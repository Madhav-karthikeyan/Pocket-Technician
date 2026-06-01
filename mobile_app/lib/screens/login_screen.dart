import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../services/providers.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _phoneController = TextEditingController();
  final _otpController = TextEditingController();
  String? _normalizedPhone;
  String? _debugOtp;
  bool _isSending = false;

  @override
  void dispose() {
    _phoneController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    setState(() => _isSending = true);
    try {
      final result = await ref.read(otpServiceProvider).sendOtp(_phoneController.text);
      setState(() {
        _normalizedPhone = result.phone;
        _debugOtp = result.debugCode;
      });
    } catch (error) {
      _showSnack(error.toString());
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  Future<void> _verifyOtp() async {
    final phone = _normalizedPhone;
    if (phone == null) return;
    final ok = await ref.read(otpServiceProvider).verifyOtp(phone: phone, otp: _otpController.text);
    if (!mounted) return;
    if (ok) {
      context.go('/');
    } else {
      _showSnack('Invalid OTP. Please check the code and try again.');
    }
  }

  void _showSnack(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF003C43), Color(0xFF00A3A3), Color(0xFFE9FFFB)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 460),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Icon(Icons.waves_rounded, size: 56, color: Color(0xFF008C8C)),
                        const SizedBox(height: 16),
                        Text(
                          'Pocket Technician CEO',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Phone OTP login with local-first farm intelligence.',
                          textAlign: TextAlign.center,
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                        const SizedBox(height: 28),
                        TextField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                            labelText: 'Mobile number',
                            prefixIcon: Icon(Icons.phone_iphone_rounded),
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),
                        FilledButton.icon(
                          onPressed: _isSending ? null : _sendOtp,
                          icon: _isSending
                              ? const SizedBox.square(dimension: 16, child: CircularProgressIndicator(strokeWidth: 2))
                              : const Icon(Icons.sms_rounded),
                          label: const Text('Send OTP'),
                        ),
                        if (_debugOtp != null) ...[
                          const SizedBox(height: 16),
                          DecoratedBox(
                            decoration: BoxDecoration(
                              color: const Color(0xFFE7F7F5),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(12),
                              child: Text('Debug OTP: $_debugOtp'),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _otpController,
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: '6-digit OTP',
                              prefixIcon: Icon(Icons.lock_clock_rounded),
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          FilledButton(
                            onPressed: _verifyOtp,
                            child: const Text('Verify and open dashboard'),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
