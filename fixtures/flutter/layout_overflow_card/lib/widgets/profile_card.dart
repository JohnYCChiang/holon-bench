import 'package:flutter/material.dart';

class ProfileCard extends StatelessWidget {
  const ProfileCard({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: Row(
          children: [
            Icon(Icons.person, size: 96),
            SizedBox(width: 24),
            Text('Very long profile name that must remain visible'),
          ],
        ),
      ),
    );
  }
}
