import datetime
import unittest

import src.bot.matchmaking.beacons as beacons
import src.testing.common as common

test_games_list = {
    "sfv": {
        "title": "Street Fighter V",
        "aliases": ["sf5"],
        "platforms": ["ps4", "pc"],
        "defaultPlatform": "pc",
        "message": "Another fight is coming your way!"
    },
    "st": {
        "title": "Super Turbo",
        "aliases": ["sf2", "ssf2t"],
        "platforms": ["ps4", "pc", "fc"],
        "defaultPlatform": "pc",
        "message": "Here comes a new challenger!"
    },
    "sfa": {
        "title": "Street Fighter Alpha 2/3",
        "aliases": ["sfa2", "sfa3"],
        "platforms": ["pc", "fc"],
        "defaultPlatform": "fc",
        "message": "Now, fight a new rival!"
    },
    "3s": {
        "title": "3rd Strike",
        "aliases": ["sf3", "sfiii", "3rdstrike", "goat", "thegoat"],
        "platforms": ["ps4", "pc", "fc"],
        "defaultPlatform": "pc",
        "message": "Now, fight a new rival!"
    }
}

test_aliases = {
    "sfv": {
        "game": "sfv"
    },
    "sf5": {
        "game": "sfv"
    },
    "sfa2": {
        "game": "sfa"
    },
    "sfa3": {
        "game": "sfa"
    },
    "st": {
        "game": "st"
    },
    "sf2": {
        "game": "st"
    },
    "ssf2t": {
        "game": "st"
    },
    "3s": {
        "game": "3s"
    },
    "sf3": {
        "game": "3s"
    },
    "sfiii": {
        "game": "3s"
    },
    "3rdstrike": {
        "game": "3s"
    }
}

test_platforms = beacons.load_platforms(test_games_list)


class TestGame(unittest.TestCase):
    def test_list(self):
        test_cases = [
            (None, beacons.Game.default_list),
            (test_games_list, test_games_list)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                game = beacons.Game.from_str(
                    arg="st",
                    provided_game_list=case
                )
                actual = game.list
                self.assertEqual(expected, actual)

    def test_aliases(self):
        test_cases = [
            (None, beacons.Game.default_alias_list),
            (test_aliases, test_aliases)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                game = beacons.Game.from_str(
                    arg="st",
                    provided_aliases=case
                )
                actual = game.alias_list
                self.assertEqual(expected, actual)

    @common.async_test
    async def test_convert(self):
        expected = "st"
        game = await beacons.Game.convert(None, expected)
        actual = game.name
        self.assertEqual(expected, actual)

    def test_from_str(self):
        expected = "st"
        game = beacons.Game.from_str(
            arg="st",
            provided_game_list=test_games_list,
            provided_aliases=test_aliases
        )
        actual = game.name
        self.assertEqual(expected, actual)

    def test_from_str_raises_exception_when_given_bad_argument(self):
        arg = "nonsense"
        with self.assertRaises(beacons.BadArgument):
            beacons.Game.from_str(
                arg=arg,
                provided_game_list=test_games_list,
                provided_aliases=test_aliases
            )

    def test__obj_or_default(self):
        test_cases = [
            ((None, "default"), ("default", None)),
            (("object", "default"), ("object", "object"))
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                actual = beacons.Game._obj_or_default(*case)
                self.assertEqual(expected, actual)

    def test___eq__(self):
        test_cases = [
            ((beacons.Game.from_str("st"), beacons.Game.from_str("st")), True),
            ((beacons.Game.from_str("st"), beacons.Game.from_str("sfv")),
             False)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                g1, g2 = case
                actual = g1 == g2
                self.assertEqual(expected, actual)


class TestWaitTime(unittest.TestCase):
    @common.async_test
    async def test_convert(self):
        expected = 12.0
        wait_time = await beacons.WaitTime.convert(None, expected)
        actual = wait_time.value
        self.assertEqual(expected, actual)

    def test_from_float(self):
        test_cases = [
            (beacons.WaitTime.min - 0.01, beacons.WaitTime.min),
            (beacons.WaitTime.max + 0.01, beacons.WaitTime.max),
            (beacons.WaitTime.min + 1, beacons.WaitTime.min + 1),
            (beacons.WaitTime.max - 1, beacons.WaitTime.max - 1)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                wait_time = beacons.WaitTime.from_float(case)
                actual = wait_time.value
                self.assertAlmostEqual(expected, actual)

    def test_from_float_raises_bad_argument_exception(self):
        with self.assertRaises(beacons.BadArgument):
            beacons.WaitTime.from_float("text")

    def test_from_timestamps(self):
        test_cases = [
            ((0, 3600), 1.0),
            ((3600, 0), beacons.WaitTime.min)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                start_timestamp, end_timestamp = case
                wait_time = beacons.WaitTime.from_timestamps(
                    start_timestamp,
                    end_timestamp
                )
                actual = wait_time.value
                self.assertAlmostEqual(expected, actual)

    def test_from_minutes(self):
        test_cases = [
            (60, 1.0),
            (beacons.WaitTime.min * 60, beacons.WaitTime.min),
            (beacons.WaitTime.max * 60, beacons.WaitTime.max)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                wait_time = beacons.WaitTime.from_minutes(case)
                actual = wait_time.value
                self.assertAlmostEqual(expected, actual)

    def test_minutes(self):
        expected = 60
        wait_time = beacons.WaitTime.from_minutes(expected)
        actual = wait_time.minutes
        self.assertEqual(expected, actual)

    def test___eq__(self):
        test_cases = [
            ((beacons.WaitTime.from_minutes(60), beacons.WaitTime.from_minutes(
                60)),
             True),
            ((beacons.WaitTime.from_minutes(60), beacons.WaitTime.from_minutes(
                120)),
             False)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                w1, w2 = case
                actual = w1 == w2
                self.assertEqual(expected, actual)


class TestPlatform(unittest.TestCase):
    @common.async_test
    async def test_convert(self):
        expected = "ps4"
        platform = await beacons.Platform.convert(None, expected)
        actual = platform.value
        self.assertEqual(expected, actual)

    def test_list(self):
        test_cases = [
            (beacons.Platform.from_str(
                arg="pc",
                platform_list=None
            ), beacons.Platform.default_list),
            (beacons.Platform.from_str(
                arg="pc",
                platform_list=test_platforms
            ), test_platforms)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                actual = case.list
                self.assertTrue(expected is actual)

    def test_from_str(self):
        test_cases = [
            (beacons.Platform.from_str(
                arg="pc",
                platform_list=None
            ), ("pc", beacons.Platform.default_list)),
            (beacons.Platform.from_str(
                arg="pc",
                platform_list=test_platforms
            ), ("pc", test_platforms))
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                expected_platform, expected_list = expected
                actual_platform = case.value
                actual_list = case.list
                self.assertEqual(expected_platform, actual_platform)
                self.assertTrue(expected_list is actual_list)

    def test_from_str_raises_bad_argument_exception(self):
        test_cases = [test_platforms, beacons.Platform.default_list]

        for case in test_cases:
            with self.subTest(case=case):
                with self.assertRaises(beacons.BadArgument):
                    beacons.Platform.from_str(
                        arg="nonsense",
                        platform_list=case
                    )

    def test___eq__(self):
        test_cases = [
            ((beacons.Platform.from_str("pc"), beacons.Platform.from_str(
                "pc")),
             True),
            ((beacons.Platform.from_str("xbox"), beacons.Platform.from_str(
                "xbox")),
             True),
            ((beacons.Platform.from_str("pc"), beacons.Platform.from_str(
                "ps4")),
             False)
        ]

        for case, expected in test_cases:
            with self.subTest(case=case):
                p1, p2 = case
                actual = p1 == p2
                self.assertEqual(expected, actual)


class TestBeaconBase(unittest.TestCase):
    def test___eq___returns_true(self):
        b1 = common.create_beacon()

        b2 = beacons.BeaconBase.from_dict({
            "user_id": 1234567890,
            "username": "Test Dummy Name",
            "game": beacons.Game.from_str("st"),
            "wait_time": beacons.WaitTime.from_float(12.0),
            "platform": beacons.Platform.from_str("pc"),
            "start": datetime.datetime.fromtimestamp(b1.start_timestamp,
                                                     datetime.timezone.utc)
        })

        actual = b1 == b2
        self.assertTrue(actual)

    def test___eq___compare_user_id_returns_false(self):
        b1 = common.create_beacon()

        b2 = beacons.BeaconBase.from_dict({
            "user_id": 123456789,
            "username": "Test Dummy Name",
            "game": beacons.Game.from_str("st"),
            "wait_time": beacons.WaitTime.from_float(12.0),
            "platform": beacons.Platform.from_str("pc"),
            "start": datetime.datetime.fromtimestamp(b1.start_timestamp,
                                                     datetime.timezone.utc)
        })

        actual = b1 == b2
        self.assertFalse(actual)

    def test_full_equality(self):
        start_time = datetime.datetime.now(datetime.timezone.utc) \
            .replace(microsecond=0)
        b1 = common.create_beacon(start=start_time)
        b2 = common.create_beacon(start=start_time)

        wait_time = beacons.WaitTime.from_minutes(60)
        b3 = beacons.BeaconBase.with_wait_time(beacon=b2, wait_time=wait_time)

        actual1 = b1.full_equality(b2)
        actual2 = b2.full_equality(b3)

        self.assertTrue(actual1)
        self.assertFalse(actual2)

    def test_start_timestamp_and_end_timestamp(self):
        dt = datetime.datetime(2021, 1, 1, 1, 0, 0,
                               tzinfo=datetime.timezone.utc)
        delta = datetime.timedelta(seconds=3600.0)
        start_timestamp = dt.timestamp()
        end_timestamp = (dt + delta).timestamp()
        beacon = common.create_beacon(start=dt, waiting_time=1.0)

        start_actual = beacon.start_timestamp
        end_actual = beacon.end_timestamp
        self.assertEqual(start_timestamp, start_actual)
        self.assertEqual(end_timestamp, end_actual)

    def test_platform_or_default_returns_default_if_given_none_or_other(self):
        test_cases = [
            (None, "pc"),
            (beacons.Platform.from_str(arg="ps3",
                                       platform_list=test_platforms),
             "pc")
        ]
        game = beacons.Game.from_str(arg="st",
                                     provided_game_list=test_games_list,
                                     provided_aliases=test_aliases)

        for case in test_cases:
            with self.subTest(case=case):
                platform, expected = case
                actual = beacons.BeaconBase.platform_or_default(
                    platform=platform,
                    game=game
                )
                self.assertEqual(expected, actual)

    def test_platform_or_default_returns_given_platform_if_correct(self):
        expected = "ps4"
        platform = beacons.Platform.from_str(
            arg=expected,
            platform_list=test_platforms
        )
        game = beacons.Game.from_str(arg="st",
                                     provided_game_list=test_games_list,
                                     provided_aliases=test_aliases)

        actual = beacons.BeaconBase.platform_or_default(
            platform=platform,
            game=game
        )
        self.assertEqual(expected, actual)

    def test_datetime_or_default_returns_new_or_given_value_as_expected(self):
        now = datetime.datetime.now(datetime.timezone.utc) \
            .replace(microsecond=0)
        delta = datetime.timedelta(days=365)
        last_year = now - delta
        test_cases = [
            (None, now),
            (last_year, last_year)
        ]

        for case in test_cases:
            dt_param, expected = case
            with self.subTest(case=case):
                actual = beacons.BeaconBase.datetime_or_default(dt_param)
                delta_limit = datetime.timedelta(seconds=10)
                self.assertAlmostEqual(
                    expected,
                    actual,
                    delta=delta_limit
                )

    def test_from_dict(self):
        start_time = datetime.datetime.now(datetime.timezone.utc)
        expected = common.create_beacon(start=start_time)
        beacon_dict = {
            "user_id": expected.user_id,
            "username": expected.username,
            "game": beacons.Game.from_str(expected.game_name),
            "wait_time": beacons.WaitTime.from_float(
                expected.minutes_available /
                60),
            "platform": beacons.Platform.from_str(expected.platform),
            "start": expected._start_datetime
        }
        beacon = beacons.BeaconBase.from_dict(beacon_dict)
        actual = expected.full_equality(beacon)
        self.assertTrue(actual)

    def test_with_wait_time(self):
        start_time = datetime.datetime.now(datetime.timezone.utc) \
            .replace(microsecond=0)
        beacon = common.create_beacon(start=start_time)
        minutes = 15
        wait_time = beacons.WaitTime.from_minutes(minutes)
        delta = datetime.timedelta(minutes=minutes)
        expected_end_timestamp = (start_time + delta).timestamp()

        actual = beacons.BeaconBase.with_wait_time(beacon, wait_time)
        self.assertEqual(beacon, actual)  # checking equality for non-time attr
        self.assertEqual(expected_end_timestamp, actual.end_timestamp)
