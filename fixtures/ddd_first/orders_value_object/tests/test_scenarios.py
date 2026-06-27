import unittest

from src.orders import Money, Order


class MoneyValueObject(unittest.TestCase):
    def test_equality_by_value(self):
        self.assertEqual(Money(100, "USD"), Money(100, "USD"))

    def test_add_same_currency(self):
        self.assertEqual(Money(100, "USD").add(Money(50, "USD")), Money(150, "USD"))


class AddingSameCurrencyItems(unittest.TestCase):
    def test_total_sums_line_items(self):
        order = Order("USD")
        order.add_item("widget", Money(100, "USD"), 2)
        order.add_item("gadget", Money(50, "USD"), 1)
        self.assertEqual(order.total(), Money(250, "USD"))


class MixingCurrencies(unittest.TestCase):
    def test_mismatched_currency_rejected(self):
        order = Order("USD")
        with self.assertRaises(ValueError):
            order.add_item("imported", Money(100, "EUR"), 1)


if __name__ == "__main__":
    unittest.main()
