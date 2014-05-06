"""OGRe Twitter Interface

:func:`twitter` : method for fetching data from Twitter

"""

import base64
import hashlib
import logging
import sys
import urllib
from datetime import datetime
from time import time
from twython import Twython
from ogre.validation import sanitize
from snowflake2time.snowflake import *


def sanitize_twitter(
        keys,
        media=("image", "text"),
        keyword="",
        quantity=15,
        location=None,
        interval=None
):

    """Validate and prepare parameters for use in Twitter data retrieval.

    .. seealso:: :meth:`ogre.validation.validate` describes the format each
                 parameter must have.

    :type keys: dict
    :param keys: Specify Twitter API keys.
                 Twitter **requires** a "consumer_key" and "access_token".

    :type media: tuple
    :param media: Specify content mediums to make lowercase and deduplicate.
                  "image" and "text" are supported mediums.

    :type keyword: str
    :param keyword: Specify search criteria to incorporate
                    the requested media in.

    :type quantity: int
    :param quantity: Specify a quota of results.

    :type location: tuple
    :param location: Specify a location to format as a Twitter geocode
                     ("<latitude>,<longitude>,<radius><unit>").

    :type interval: tuple
    :param interval: Specify earliest and latest moments to convert to
                     Twitter Snowflake IDs.

    :raises: ValueError

    :rtype: tuple
    :returns: Each passed parameter is returned (in order) in the proper format.

    """

    clean_keys = {}
    for key, value in keys.items():
        key = key.lower()
        if key not in (
            "consumer_key",
            "access_token"
        ):
            raise ValueError(
                'Valid Twitter keys are "consumer_key" and "access_token".'
            )
        if not value:
            raise ValueError("Twitter API keys are required.")
        clean_keys[key] = value
    if "consumer_key" not in clean_keys.keys() or \
       "access_token" not in clean_keys.keys():
        raise ValueError(
            'Twitter API keys must include a "consumer_key" and "access_token".'
        )

    clean_media, q, clean_quantity, clean_location, clean_interval = \
        sanitize(
            media=media,
            keyword=keyword,
            quantity=quantity,
            location=location,
            interval=interval
        )

    kinds = []
    if clean_media is not None:
        for clean_medium in clean_media:
            if clean_medium in ("image", "text"):
                kinds.append(clean_medium)
    kinds = tuple(kinds)

    if kinds == ("image",):
        q += "  pic.twitter.com"
    elif kinds == ("text",):
        q += " -pic.twitter.com"
    q = q.strip()

    geocode = None
    if location is not None and clean_location[2] > 0:
        geocode = \
            str(clean_location[0]) + "," +\
            str(clean_location[1]) + "," +\
            str(clean_location[2])+clean_location[3]

    period_id = (None, None)
    if interval is not None:
        period_id = (
            utc2snowflake(clean_interval[0]),
            utc2snowflake(clean_interval[1])
        )

    if q in ("", "-pic.twitter.com") and geocode is None:
        raise ValueError("Specify either a keyword or a location.")

    return (
        clean_keys,
        kinds,
        q,
        clean_quantity,
        geocode,
        period_id
    )


def twitter(
        keys,
        media=("image", "text"),
        keyword="",
        quantity=15,
        location=None,
        interval=None,
        **kwargs
):

    """Fetch Tweets from the Twitter API.

    .. seealso:: :meth:`sanitize_twitter` describes more about
                 the format each parameter must have.

    :type keys: dict
    :param keys: Specify an API key and access token.

    :type media: tuple
    :param media: Specify content mediums to fetch.
                  "text" or "image" are supported mediums.

    :type keyword: str
    :param keyword: Specify search criteria.
                    "Queries can be limited due to complexity."
                    If this happens, no results will be returned.
                    To avoid this, follow Twitter Best Practices including
                    the following:
                    "Limit your searches to 10 keywords and operators."

    :type quantity: int
    :param quantity: Specify a quota of results to fetch.
                     Twitter will return 15 results by default,
                     and up to 100 can be requested in a single query.
                     If a number larger than 100 is specified,
                     the retriever will make multiple queries in an attempt
                     to satisfy the requested `quantity`,
                     but this is done on a best effort basis.
                     Whether the specified number is returned or
                     not depends on Twitter.

    :type location: tuple
    :param location: Specify a place (latitude, longitude, radius, unit)
                     to search.
                     Since OGRe only returns geotagged results,
                     the larger the specified radius,
                     the fewer results will be returned.
                     This is because of the way Twitter satisfies
                     geocoded queries.
                     It uses so-called "fuzzy matching logic" to deduce the
                     location of Tweets posted publicly without location data.
                     OGRe filters these out.

    :type interval: tuple
    :param interval: Specify a period of time (earliest, latest) to search.
                     "The Search API is not complete index of all Tweets,
                     but instead an index of recent Tweets."
                     Twitter's definition of "recent" is rather vague,
                     but when an interval is not specified,
                     "that index includes between 6-9 days of Tweets."

    :type strict_media: bool
    :param strict_media: Specify whether to only return the requested media
                         (defaults to False).
                         Setting this to False helps build caches faster at
                         no additional cost.
                         For instance, since Twitter automatically sends the
                         text of a Tweet back, if `("image",)` is passed for
                         `media`, the text on hand will only be filtered if
                         `strict_media` is True.

    :type secure: bool
    :param secure: Specify whether to prefer HTTPS or not (defaults to True).

    :type test: bool
    :param test: Specify whether a the current request is a trial run.
                 This affects what gets logged and should be accompanied by
                 the next 3 parameters (`test_message`, `api`, and `network`).

    :type test_message: str
    :param test_message: Specify a description of the test to log.
                         This is ignored if the `test` parameter is False.

    :type api: callable
    :param api: Specify API access point (for dependency injection).

    :type network: callable
    :param network: Specify a network access point (for dependency injection).

    :raises: TwythonError

    :rtype: list
    :returns: GeoJSON Feature(s)

    .. seealso:: Visit https://dev.twitter.com/docs/using-search for tips on
                 how to build queries for Twitter using the `keyword` parameter.
                 More information may also be found at
                 https://dev.twitter.com/docs/api/1.1/get/search/tweets.

    """

    keychain, kinds, q, remaining, geocode, (since_id, max_id) = \
        sanitize_twitter(
            keys=keys,
            media=media,
            keyword=keyword,
            quantity=quantity,
            location=location,
            interval=interval
        )

    qid = hashlib.md5(
        str(time.time()) +
        str(q) +
        str(remaining) +
        str(geocode) +
        str(since_id) +
        str(max_id)
    ).hexdigest()
    logging.basicConfig(
        filename="OGRe.log",
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%Y/%m/%d %H:%M:%S %Z"
    )
    log = logging.getLogger(__name__)
    if kwargs.get("test", False):
        log.setLevel(logging.DEBUG)
        log.info(qid+" Request: Twitter TEST "+kwargs.get("test_message", ""))
        log.debug(
            qid+" Status:" +
            " media("+str(media)+")" +
            " keyword("+str(q)+")" +
            " quantity("+str(remaining)+")" +
            " location("+str(geocode)+")" +
            " interval("+str(since_id)+","+str(max_id)+")" +
            " kwargs("+str(kwargs)+")"
        )
    else:
        log.setLevel(logging.INFO)
        log.info(qid+" Request: Twitter")

    if not kinds or remaining < 1:
        log.info(qid+" Success: No results were requested.")
        return []

    api = kwargs.get("api", Twython)(
        keychain["consumer_key"],
        access_token=keychain["access_token"]
    )
    limits = api.get_application_rate_limit_status()
    maximum_queries = 450  # Twitter allows 450 queries every 15 minutes.
    try:
        maximum_queries =\
            int(limits["resources"]["search"]["/search/tweets"]["remaining"])
        if maximum_queries < 1:
            log.info(qid+" Failure: Queries are being limited.")
        else:
            log.debug(qid+" Status: "+str(maximum_queries)+" queries remain.")
    except KeyError:
        log.warn(qid+" Unobtainable Rate Limit")
    total = remaining

    collection = []
    for query in range(0, maximum_queries):
        count = min(remaining, 100)  # Twitter accepts a max count of 100.
        try:
            results = api.search(
                q=q,
                count=count,
                geocode=geocode,
                since_id=since_id,
                max_id=max_id
            )
        except:
            log.info(
                qid+" Failure: " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                str(sys.exc_info()[1])
            )
            raise
        if results.get("statuses") is None:
            log.info(
                qid+" Failure: " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                "The request is too complex."
            )
            break
        for tweet in results["statuses"]:
            if tweet.get("coordinates") is None or tweet.get("id") is None:
                # Tweets must be geotagged and timestamped.
                continue
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        tweet["coordinates"]["coordinates"][0],
                        tweet["coordinates"]["coordinates"][1]
                    ]
                },
                "properties": {
                    "source": "Twitter",
                    "time": datetime.utcfromtimestamp(
                        snowflake2utc(tweet["id"])
                    ).isoformat()+"Z"
                }
            }
            if "text" in kinds:
                if tweet.get("text") is not None:
                    feature["properties"]["text"] = tweet["text"]
            if "image" in kinds:
                if not kwargs.get("strict_media", False):
                    if tweet.get("text") is not None:
                        feature["properties"]["text"] = tweet["text"]
                if tweet.get("entities", {}).get("media") is not None:
                    for entity in tweet["entities"]["media"]:
                        if entity.get("type") is not None:
                            if entity["type"].lower() == "photo":
                                media_url = "media_url_https"
                                if not kwargs.get("secure", True):
                                    media_url = "media_url"
                                if entity.get(media_url) is not None:
                                    feature["properties"]["image"] =\
                                        base64.b64encode(
                                            kwargs.get(
                                                "network",
                                                urllib.urlopen
                                            )(
                                                entity[media_url]
                                            ).read()
                                        )
            if len(feature["properties"]) > 2:
                collection.append(feature)
        remained = remaining
        remaining = total-len(collection)
        log.debug(
            qid+" Status:" +
            " 1 query produced "+str(remained-remaining)+" results."
        )
        if remaining <= 0:
            log.info(
                qid+" Success: " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results."
            )
            break
        if results.get("search_metadata", {}).get("next_results") is None:
            outcome = "Success" if len(collection) > 0 else "Failure"
            log.info(
                qid+" "+outcome+": " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                "No retrievable results remain."
            )
            break
        max_id = int(
            results["search_metadata"]["next_results"]
            .split("max_id=")[1]
            .split("&")[0]
        )
        if query+1 >= maximum_queries:
            outcome = "Success" if len(collection) > 0 else "Failure"
            log.info(
                qid+" "+outcome+": " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                "No remaining results are retrievable."
            )
    return collection
