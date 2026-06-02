import 'package:flutter/material.dart';

class ResponsivePanel extends StatelessWidget {
  const ResponsivePanel({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Row(
          children: const [
            SizedBox(width: 220, child: Text('Filters')),
            SizedBox(width: 220, child: Text('Results')),
          ],
        ),
      ),
    );
  }
}
