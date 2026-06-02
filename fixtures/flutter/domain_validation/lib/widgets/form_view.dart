import 'package:flutter/material.dart';

class RegistrationForm extends StatefulWidget {
  const RegistrationForm({super.key});

  @override
  State<RegistrationForm> createState() => _RegistrationFormState();
}

class _RegistrationFormState extends State<RegistrationForm> {
  final emailController = TextEditingController();
  String? error;

  @override
  void dispose() {
    emailController.dispose();
    super.dispose();
  }

  void submit() {
    final email = emailController.text;
    setState(() {
      if (!email.contains('@')) {
        error = 'Enter a valid email';
      } else {
        error = null;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Column(
          children: [
            TextField(key: const Key('email'), controller: emailController),
            ElevatedButton(onPressed: submit, child: const Text('Submit')),
            if (error != null) Text(error!, key: const Key('error')),
          ],
        ),
      ),
    );
  }
}
