import logging
import json
import StringIO
from cloudengine.core.cloudapi_view import CloudAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser
from serializers import UserSerializer
from cloudengine.core.utils import paginate
from models import AppUser



class UserClassView(CloudAPIView):
    
    logger = logging.getLogger("cloudengine")
    
    def get(self, request, *args, **kwargs):
        app_users = AppUser.objects.filter(app = request.app)
        users = [app_user.user for app_user in app_users]
        serializer = UserSerializer(users, many=True)
        return Response(paginate(request, serializer.data))
        
    def post(self, request):
        data = request.DATA
        try:
            username = data["username"]
            password = data["password"]
        except KeyError as e:
            return Response({"error": "Invalid object."},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        #todo: validate username and password
        user = User.objects.create_user(username = username, password = password)
        new_user = AppUser(user = user, app = request.app)
        try:
            new_user.full_clean()
        except ValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        
        new_user.save()
        user = authenticate(username=username, password=password)
        login(request, user)
        request.session.save()
        return Response({settings.SESSION_COOKIE_NAME : request.session.session_key,
                          "id" : user.id
                        },
                        status=status.HTTP_201_CREATED)
        
    def delete(self, request):
        try:
            users = AppUser.objects.filter(app = request.app)
            users.delete()
        except Exception:
            pass
        return Response({"result": "All users of this app are deleted"})



class LoginView(CloudAPIView):
    logger = logging.getLogger("cloudengine")
    
    def post(self, request):
        credentials  = request.DATA
        try:
            #make sure the user object has username and password
            username = credentials["username"]
            password = credentials["password"]
        except KeyError:
            return Response({"error": "username/password field missing"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.save()
                return Response({settings.SESSION_COOKIE_NAME : request.session.session_key})
            else:
                return Response({"error": "User account is inactive"},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        else:
            return Response({"error": "incorrect username/password"},
                            status=status.HTTP_400_BAD_REQUEST)


class LogoutView(CloudAPIView):
    
    def get(self, request):
        logout(request)
        return Response({"result": "User logged out successfully"})


class CurrentUserView(CloudAPIView):
    
    def get(self, request):
        user = request.user
        if isinstance(user, AnonymousUser):
            return Response({"error": "user not logged in"})
        
        serializer = UserSerializer(user)
        return Response({"result": serializer.data})


class UserDetailView(CloudAPIView):
    logger = logging.getLogger("cloudengine")
    
    def get(self, request, id):
        user = AppUser.objects.get(pk = id)
        serializer = UserSerializer(user)
        return Response({"result": serializer.data})
    
    def put(self, request, id):
        data = request.DATA
        # If valid, update the user
        user = AppUser.objects.get(pk=id)
        for key in data.keys():
            setattr(user, key, data[key])
        user.save()
        return Response({"result": "User data updated successfully"})
        

    def delete(self, request, id):
        try:
            user = AppUser.objects.get(pk = id)
        except AppUser.DoesNotExist:
            return Response({"error": "Invalid user id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        user.delete()
        return Response({"result": "User deleted successfully"})



