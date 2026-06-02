import 'dart:async';

class TickerController {
  TickerController(this.onTick);

  final void Function() onTick;
  Timer? _timer;

  void start() {
    _timer = Timer.periodic(const Duration(milliseconds: 10), (_) => onTick());
  }

  void dispose() {}
}
