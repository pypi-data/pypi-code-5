import requests
from json import JSONEncoder

from .exceptions import *

def get_session(uuid):
    """
    Gets the session for a given UUID, containing all sorts of fun details.

    If a UUID is invalid, an InvalidUsername exception will be raised.

    :param uuid: The UUID to get session information for.
    :return: Decoded JSON for the session of the given UUID.
    """
    r = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/%s" % uuid)

    if r.text == "":
        raise InvalidUsername

    return r.json()

def to_uuid(users):
    """
    Provides easy method for checking UUID of one or multiple users.
    Will always return a dictionary with the keys representing usernames.

    If a username is invalid, it will not be included in the response dictionary.

    :param users: String or list of usernames to convert to UUIDs.
    :return: A dictionary mapping all (valid) users to UUIDs.
    """
    resp = {}

    r = requests.post(
        "https://api.mojang.com/profiles/minecraft",
        headers={"Content-Type": "application/json"},
        data=JSONEncoder().encode(users)
    )

    for pair in r.json():
        resp[pair['name']] = pair['id']

    return resp

def to_user(uuid):
    """
    Provides method for checking username of a single UUID.
    Will always return a string containing the username.

    If a UUID is invalid, an InvalidUsername exception will be raised.

    :param uuid: The UUID to look up through the API.
    :return: The username associated with the given UUID.
    """
    s = get_session(uuid)

    return s['name']