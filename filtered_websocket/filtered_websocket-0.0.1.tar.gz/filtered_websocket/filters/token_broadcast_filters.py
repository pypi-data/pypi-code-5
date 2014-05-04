import logging
import re

from base import WebSocketMessageFilter, WebSocketDisconnectFilter


class TokenMessageFilter(WebSocketMessageFilter):

    @classmethod
    def filter(cls, web_socket_instance, msg):
        token = re.search("token:([^\s]*)", msg)
        if token is not None:
            web_socket_instance.token = token.group(1)
            logging.debug("Registering %s with broadcast group: %s" % (web_socket_instance.id, token.group(1)))
            web_socket_instance.storage_object.add(web_socket_instance.token, web_socket_instance.id)
            web_socket_instance.sendMessage("Successfully registered with broadcast group: %s" % web_socket_instance.token)
        elif web_socket_instance.token is not None:
            for _id, user in web_socket_instance.users.items():
                if _id != web_socket_instance.id and _id in web_socket_instance.storage_object[web_socket_instance.token]:
                    user.sendMessage(msg)
        else:
            logging.error("Unable to broadcast message, no token is set for %s" % web_socket_instance.id)
            web_socket_instance.sendMessage("Error: No token has been set")


class TokenDisconnectFilter(WebSocketDisconnectFilter):

    @classmethod
    def filter(cls, web_socket_instance, data):
        if web_socket_instance.token:
            try:
                web_socket_instance.storage_object.remove(web_socket_instance.token, web_socket_instance.id)
            except Exception as e:
                logging.error(e.message)
