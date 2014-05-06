"""OGRe Twitter Interface Tests

:class:`TwitterTest` -- Twitter interface test template

:meth:`TwitterTest.setUp` -- test initialization

:meth:`TwitterTest.test_sanitize_twitter` -- Twitter parameter preparation tests

:meth:`TwitterTest.test_twitter` -- Twitter API query tests

"""

import base64
import copy
import json
import os
import unittest
from datetime import datetime
from mock import MagicMock
from StringIO import StringIO
from twython import TwythonError
from snowflake2time import snowflake
from ogre import OGRe
from ogre.Twitter import *


def twitter_limits(remaining):
    return {
        "resources": {
            "search": {
                "/search/tweets": {
                    "remaining": remaining
                }
            }
        }
    }


class TwitterTest (unittest.TestCase):

    """Create objects that test the OGRe module.

    :meth:`TwitterTest.setUp` -- retriever and Twython Mock initialization

    :meth:`TwitterTest.test_sanitize_twitter` -- parameter cleansing tests

    :meth:`TwitterTest.test_twitter` -- API access and results-packaging tests

    """

    def setUp(self):

        """Prepare to run tests on the Twitter interface.

        Since OGRe requires API keys to run and they cannot be stored
        conveniently, this test module retrieves them from the OS;
        however, to prevent OGRe from actually querying the APIs
        (and subsequently retrieving unpredictable data),
        a MagicMock object is used to do a dependency injection.
        This relieves the need for setting environment variables
        (although they may be necessary in the future).
        Predictable results are stored in the data directory to be read
        during these tests.

        """

        self.retriever = OGRe(
            keys={
                "Twitter": {
                    "consumer_key": os.environ.get("TWITTER_CONSUMER_KEY"),
                    "access_token": os.environ.get("TWITTER_ACCESS_TOKEN")
                }
            }
        )
        with open("ogre/test/data/Twitter-response-example.json") as tweets:
            self.tweets = json.load(tweets)

        self.api = {
            "regular": MagicMock(),
            "limited": MagicMock(),
            "Twython": MagicMock(),
            "complex": MagicMock(),
            "single": MagicMock()
        }

        self.api["regular"]().get_application_rate_limit_status.return_value =\
            twitter_limits(2)
        self.api["regular"]().search.return_value = copy.deepcopy(self.tweets)

        self.api["limited"]().get_application_rate_limit_status.return_value =\
            twitter_limits(0)
        self.api["limited"]().search.return_value = {
            "errors": [
                {
                    "code": 88,
                    "message": "Rate limit exceeded"
                }
            ]
        }

        self.api["Twython"]().get_application_rate_limit_status.return_value =\
            self.api["regular"]().get_application_rate_limit_status.return_value
        self.api["Twython"]().search.side_effect = TwythonError("test_error")

        self.api["complex"]().get_application_rate_limit_status.return_value =\
            self.api["regular"]().get_application_rate_limit_status.return_value
        self.api["complex"]().search.return_value = {
            "error": "Sorry, your query is too complex." +
                     " Please reduce complexity and try again."
        }

        self.api["single"]().get_application_rate_limit_status.return_value =\
            twitter_limits(1)
        self.api["single"]().search.return_value = copy.deepcopy(self.tweets)
        self.api["single"]().search.return_value["search_metadata"].pop(
            "next_results",
            None
        )

        self.api["regular"].reset_mock()
        self.api["limited"].reset_mock()
        self.api["Twython"].reset_mock()
        self.api["complex"].reset_mock()
        self.api["single"].reset_mock()

        self.network = {
            "regular": MagicMock(),
            "limited": MagicMock(),
            "Twython": MagicMock(),
            "complex": MagicMock(),
            "single": MagicMock()
        }
        self.network["regular"].side_effect = lambda _: StringIO("test_image")
        self.network["limited"].side_effect = Exception()
        self.network["Twython"].side_effect = Exception()
        self.network["complex"].side_effect = Exception()
        self.network["single"].return_value = StringIO("test_image")
        self.network["regular"].reset_mock()
        self.network["limited"].reset_mock()
        self.network["Twython"].reset_mock()
        self.network["complex"].reset_mock()
        self.network["single"].reset_mock()

    def test_sanitize_twitter(self):

        """Test the Twitter interface parameter sanitizer.

        These tests should verify that malformed or invalid data is detected
        before being sent to Twitter. They should also test that valid data is
        formatted correctly for use by Twython.

        """

        with self.assertRaises(ValueError):
            sanitize_twitter(keys={})
        with self.assertRaises(ValueError):
            sanitize_twitter(keys={"invalid": None})
        with self.assertRaises(ValueError):
            sanitize_twitter(keys={"consumer_key": None})
        with self.assertRaises(ValueError):
            sanitize_twitter(keys={"consumer_key": "key", "invalid": None})
        with self.assertRaises(ValueError):
            sanitize_twitter(
                keys={
                    "consumer_key": "key",
                    "access_token": None
                }
            )
        with self.assertRaises(ValueError):
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ]
            )
        with self.assertRaises(ValueError):
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                location=(2, 1, 0, "km")
            )

        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("text",),
                keyword="test"
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("text",),
                "test -pic.twitter.com",
                15,
                None,
                (None, None)
            )
        )
        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image",),
                keyword="test"
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("image",),
                "test  pic.twitter.com",
                15,
                None,
                (None, None)
            )
        )
        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                location=(0, 1, 2, "km")
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("image", "text"),
                "",
                15,
                "0.0,1.0,2.0km",
                (None, None)
            )
        )
        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                interval=(0, 1)
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("image", "text"),
                "test",
                15,
                None,
                (-5405765689543753728, -5405765685349449728)
            )
        )

    def test_twitter(self):

        """Test OGRe's access point to the Twitter API.

        These tests should make sure all input is validated correctly,
        and they should make sure that any relevant Twitter data is extracted
        and packaged in GeoJSON format correctly.

        The first two Tweets in the example Twitter response data
        must be geotagged, and the first one must an image entity attached.
        If any other geotagged data is included, this test will fail;
        however, it is a good idea to include non-geotagged Tweets
        to ensure that OGRe omits them in the returned results.

        """

        # Requesting no media fails fast.
        self.api["regular"].reset_mock()
        self.network["regular"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=(),
                keyword="test",
                test=True,
                test_message="Media Fail-Fast",
                api=self.api["regular"],
                network=self.network["regular"]
            ),
            []
        )
        self.assertEqual(self.api["regular"].call_count, 0)
        self.assertEqual(
            self.api["regular"]().get_application_rate_limit_status.call_count,
            0
        )
        self.assertEqual(self.api["regular"]().search.call_count, 0)
        self.assertEqual(self.network["regular"].call_count, 0)

        # Requesting < 1 result fails fast.
        self.api["regular"].reset_mock()
        self.network["regular"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                quantity=0,
                test=True,
                test_message="Quantity Fail-Fast",
                api=self.api["regular"],
                network=self.network["regular"]
            ),
            []
        )
        self.assertEqual(self.api["regular"].call_count, 0)
        self.assertEqual(
            self.api["regular"]().get_application_rate_limit_status.call_count,
            0
        )
        self.assertEqual(self.api["regular"]().search.call_count, 0)
        self.assertEqual(self.network["regular"].call_count, 0)

        # The constructor is called appropriately once per request.
        # The rate limit is retrieved once per request.
        # The API is queried once per lap around the loop.
        # HTTPS is used by default to retrieve images.
        self.api["regular"].reset_mock()
        self.network["regular"].reset_mock()
        twitter(
            keys=self.retriever.keychain[
                self.retriever.keyring["twitter"]
            ],
            media=("image", "text"),
            keyword="test",
            quantity=2,
            location=(4, 3, 2, "km"),
            interval=(1, 0),
            test=True,
            test_message="Appropriate API Use and HTTPS by Default",
            api=self.api["regular"],
            network=self.network["regular"]
        )
        self.api["regular"].assert_called_once_with(
            self.retriever.keychain[
                self.retriever.keyring["twitter"]
            ]["consumer_key"],
            access_token=self.retriever.keychain[
                self.retriever.keyring["twitter"]
            ]["access_token"]
        )
        self.api["regular"]().get_application_rate_limit_status\
            .assert_called_once_with()
        self.api["regular"]().search.assert_called_once_with(
            q="test",
            count=2,
            geocode="4.0,3.0,2.0km",
            since_id=-5405765689543753728,
            max_id=-5405765685349449728
        )
        self.network["regular"].assert_called_once_with(
            self.tweets["statuses"][0]
            ["entities"]["media"][0]["media_url_https"]
        )

        # The rate limit is applied appropriately.
        self.api["limited"].reset_mock()
        self.network["limited"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                test=True,
                test_message="Rate Limit Application",
                api=self.api["limited"],
                network=self.network["limited"]
            ),
            []
        )
        self.assertEqual(self.api["limited"].call_count, 1)
        self.assertEqual(
            self.api["limited"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["limited"]().search.call_count, 0)
        self.assertEqual(self.network["limited"].call_count, 0)

        # TwythonErrors are relayed correctly.
        self.api["Twython"].reset_mock()
        self.network["Twython"].reset_mock()
        with self.assertRaises(TwythonError):
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                test=True,
                test_message="TwythonError Relay",
                api=self.api["Twython"],
                network=self.network["Twython"]
            )
        self.assertEqual(self.api["Twython"].call_count, 1)
        self.assertEqual(
            self.api["Twython"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["Twython"]().search.call_count, 1)
        self.assertEqual(self.network["Twython"].call_count, 0)

        # No "statuses" key in Twitter response causes a break.
        self.api["complex"].reset_mock()
        self.network["complex"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                test=True,
                test_message="Empty Response",
                api=self.api["complex"],
                network=self.network["complex"]
            ),
            []
        )
        self.assertEqual(self.api["complex"].call_count, 1)
        self.assertEqual(
            self.api["complex"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["complex"]().search.call_count, 1)
        self.assertEqual(self.network["complex"].call_count, 0)

        # Ungeotagged or untimestamped results are omitted.
        # "Text" media is returned when requested.
        # "Image" media is not returned unless requested.
        # No remaining pages causes a break.
        self.api["single"].reset_mock()
        self.network["single"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("text",),
                keyword="test",
                quantity=4,
                location=(0, 1, 2, "km"),
                interval=(3, 4),
                test=True,
                test_message="Filtering and Out of Pages",
                api=self.api["single"],
                network=self.network["single"]
            ),
            [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][0]
                                ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][0]
                                ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][0]["text"],
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][0]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                },
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][1]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][1]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][1]["text"],
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][1]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                }
            ]
        )
        self.assertEqual(self.api["single"].call_count, 1)
        self.assertEqual(
            self.api["single"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["single"]().search.call_count, 1)
        self.assertEqual(self.network["single"].call_count, 0)

        # "Text" media is returned when not requested.
        # "Image" media is returned when requested.
        # Remaining results are calculated correctly.
        # Setting "secure" kwarg to False causes HTTP retrieval.
        self.api["regular"].reset_mock()
        self.network["regular"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image",),
                keyword="test",
                quantity=1,
                location=(0, 1, 2, "km"),
                interval=(3, 4),
                secure=False,
                test=True,
                test_message="Filtering, Counting, and HTTP by Request",
                api=self.api["regular"],
                network=self.network["regular"]
            ),
            [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][0]["text"],
                        "image": base64.b64encode("test_image"),
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][0]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                },
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][1]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][1]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][1]["text"],
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][1]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                }
            ]
        )
        self.assertEqual(self.api["regular"].call_count, 1)
        self.assertEqual(
            self.api["regular"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["regular"]().search.call_count, 1)
        self.network["regular"].assert_called_once_with(
            self.tweets["statuses"][0]
            ["entities"]["media"][0]["media_url"]
        )

        # Setting "strict_media" kwarg to True returns only requested media.
        # Parameters for paging are computed correctly.
        # Paging is not used unless it is needed.
        # Duplicates are not filtered.
        self.api["regular"].reset_mock()
        self.network["regular"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image",),
                keyword="test",
                quantity=2,
                location=(0, 1, 2, "km"),
                interval=(3, 4),
                strict_media=True,
                test=True,
                test_message="Strict Media, Paging, and Duplication",
                api=self.api["regular"],
                network=self.network["regular"]
            ),
            [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "image": base64.b64encode("test_image"),
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][0]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                },
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "image": base64.b64encode("test_image"),
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][0]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                }
            ]
        )
        self.assertEqual(self.api["regular"].call_count, 1)
        self.assertEqual(
            self.api["regular"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["regular"]().search.call_count, 2)
        self.api["regular"]().search.assert_has_any_call(
            q="test pic.twitter.com",
            count=2,
            geocode="0.0,0.1,2.0km",
            since_id=-5405765676960841728,
            max_id=-5405765672766537728
        )
        self.api["regular"]().search.assert_has_any_call(
            q="test pic.twitter.com",
            count=1,
            geocode="0.0,0.1,2.0km",
            since_id=-5405765676960841728,
            max_id=445633721891164159
        )
        self.assertEqual(self.network["regular"].call_count, 2)

        # Results are packages correctly.
        self.api["regular"].reset_mock()
        self.network["regular"].reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image", "text"),
                keyword="test",
                quantity=2,
                location=(0, 1, 2, "km"),
                interval=(3, 4),
                test=True,
                test_message="Packaging",
                api=self.api["regular"],
                network=self.network["regular"]
            ),
            [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][0]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][0]["text"],
                        "image": base64.b64encode("test_image"),
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][0]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                },
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][1]
                            ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][1]
                            ["coordinates"]["coordinates"][1]
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][1]["text"],
                        "time": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][1]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                }
            ]
        )
        self.assertEqual(self.api["regular"].call_count, 1)
        self.assertEqual(
            self.api["regular"]().get_application_rate_limit_status.call_count,
            1
        )
        self.assertEqual(self.api["regular"]().search.call_count, 1)
        self.assertEqual(self.network["regular"].call_count, 1)


if __name__ == "__main__":
    unittest.main()
