import mock
import unittest

from pyramid import testing

from pyramid_urbanairship import IUrbanAirship, UrbanAirship


class TestPyramidUrbanAirship(unittest.TestCase):
    def test_constructs_utility(self):
        from pyramid_urbanairship import includeme
        settings = {
            'urbanairship.application_key': 'my_app',
            'urbanairship.application_secret': 'my_secret',
            }

        with testing.testConfig(settings=settings) as config:
            includeme(config)
            config.commit()

            utility = config.registry.getUtility(IUrbanAirship)
            self.assertIsInstance(utility, UrbanAirship)

    def test_missing_setting_application_key(self):
        from pyramid_urbanairship import includeme
        settings = {
            'urbanairship.application_secret': 'my_secret',
            }

        with testing.testConfig(settings=settings) as config:
            with self.assertRaises(KeyError):
                includeme(config)

    def test_missing_setting_application_secret(self):
        from pyramid_urbanairship import includeme
        settings = {
            'urbanairship.application_key': 'my_app',
            }

        with testing.testConfig(settings=settings) as config:
            with self.assertRaises(KeyError):
                includeme(config)

    def test_get_urbanairship_utility(self):
        from pyramid_urbanairship import get_urbanairship_utility

        request = mock.Mock()

        result = get_urbanairship_utility(request)

        request.registry.getUtility.assert_called_once_with(IUrbanAirship)

        self.assertEqual(
            result,
            request.registry.getUtility.return_value,
            )
