from base import WebSocketMessageFilter


class BroadcastMessageFilter(WebSocketMessageFilter):

    @classmethod
    def filter(cls, web_socket_instance, msg):
        for _id, user in web_socket_instance.users.items():
            if _id != web_socket_instance.id:
                user.sendMessage(msg)