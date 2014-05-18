import json
from rest_framework import status
from rest_framework.response import Response
from cloudengine.core.cloudapi_view import CloudAPIView
from cloudengine.push.push_service import get_subscriber_count
from cloudengine.push.push_service import push_to_channel
from cloudengine.push.models import PushNotification



class PushSubscribers(CloudAPIView):

    def get(self, request):
        channel = request.app.name
        count = get_subscriber_count(channel)
        return Response({"result": count})


class PushAPIView(CloudAPIView):

    def post(self, request):
        channel = request.app.name
        count = get_subscriber_count(channel)
        try:
            message = request.DATA["message"]
        except KeyError:
            return Response({"error": "Invalid message format"},
                            status = status.HTTP_400_BAD_REQUEST)

        push_to_channel(channel, message)
        notification = PushNotification(app=request.app, num_subscribers=count)
        notification.save()
        return Response({"result": "Notification sent to %d subscriber(s)"%count})
