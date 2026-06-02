import 'package:flutter/material.dart';

class DetailScreen extends StatefulWidget {
  const DetailScreen({required this.load, super.key});

  final Future<String> Function() load;

  @override
  State<DetailScreen> createState() => _DetailScreenState();
}

class _DetailScreenState extends State<DetailScreen> {
  String text = 'Loading';

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final value = await widget.load();
      setState(() => text = value);
    } catch (_) {
      setState(() => text = 'Error');
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(home: Scaffold(body: Text(text)));
  }
}
