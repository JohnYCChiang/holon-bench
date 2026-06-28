/// Drives a multi-step wizard, gating forward movement on step validity.
class WizardController {
  final int stepCount;
  int _current = 0;
  final Set<int> _valid = <int>{};

  WizardController(this.stepCount) : assert(stepCount > 0);

  int get current => _current;
  bool isValid(int step) => _valid.contains(step);
  bool get canAdvance => _valid.contains(_current);

  void markValid(int step, bool valid) {
    if (valid) {
      _valid.add(step);
    } else {
      _valid.remove(step);
    }
  }

  bool next() {
    _current++; // BUG: ignores validity and the last-step bound
    return true;
  }

  bool back() {
    if (_current == 0) return false;
    _current--;
    return true;
  }

  bool goTo(int target) {
    _current = target; // BUG: jumps anywhere without validating the path
    return true;
  }
}
