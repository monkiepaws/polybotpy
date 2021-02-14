import unittest

from src.matchmaking.matchmaking import GamesList
from testing.common import create_beacon


class TestGamesList(unittest.TestCase):
    def test_create(self):
        test_cases = [
            (([
                  create_beacon("sfv", 1.5, "pc"),
                  create_beacon("st", 12.5, "ps4")
              ], "All SFV"),
             "`WP Matchmaking\n"
             "All SFV Beacons\n"
             "\n"
             "🏮 SFV    Test Dummy Name    1h 29m  PC   \n"
             "🏮 ST     Test Dummy Name    12h 29m PS4  \n`"
            ),
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                beacons, title = case
                actual = GamesList.create(beacons=beacons, title=title)
                self.assertEqual(expected, actual)

    def test_take(self):
        test_cases = [
            (("less than n", 1000), "less than n"),
            (("more than n", 1), "m"),
            (("equal to n", 10), "equal to n")
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                string, n = case
                actual = GamesList.take(string, n)
                self.assertEqual(expected, actual)

    def test__time_from_mins(self):
        test_cases = [
            (30, "30m"),
            (60, "1h 0m"),
            (90, "1h 30m")
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                actual = GamesList._time_from_mins(mins=case)
                self.assertEqual(expected, actual)

    def test_entry(self):
        test_cases = [
            (
                create_beacon("st", 12.0, "pc"),
                "🏮 ST     Test Dummy Name    11h 59m PC   \n"
            ),
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                sut = GamesList()
                actual = sut.entry(case)
                self.assertEqual(expected, actual)
