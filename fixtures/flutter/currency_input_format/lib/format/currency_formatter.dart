/// Formats an integer number of cents as a grouped currency string.
String formatCents(int cents, {String symbol = '\$'}) {
  return '$symbol${cents / 100}'; // BUG: no grouping, no padding, wrong sign
}
