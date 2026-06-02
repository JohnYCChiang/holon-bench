import 'package:flutter/material.dart';

class SubmitForm extends StatefulWidget {
  const SubmitForm({required this.onSubmit, super.key});

  final Future<void> Function() onSubmit;

  @override
  State<SubmitForm> createState() => _SubmitFormState();
}

class _SubmitFormState extends State<SubmitForm> {
  bool submitting = false;

  Future<void> submit() async {
    setState(() => submitting = true);
    await widget.onSubmit();
    setState(() => submitting = false);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: ElevatedButton(
          onPressed: submit,
          child: Text(submitting ? 'Saving' : 'Save'),
        ),
      ),
    );
  }
}
