import mimetypes
import logging
from models import CloudFile
from manager import FilesManager
from exceptions import FileTooLarge, FileNotFound
from cloudengine.core.models import CloudApp
from cloudengine.core.cloudapi_view import CloudAPIView
from django.core.files.base import ContentFile
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from serializers import CloudFileSerializer

logger = logging.getLogger("cloudengine")


#todo: test that cloudapi is compatible with generic
class FileListView(CloudAPIView, generics.ListCreateAPIView):
    serializer_class = CloudFileSerializer

    def get(self, request, *args, **kwargs):
        cloudapp = CloudApp.objects.get(name = request.app.name)
        self.queryset = CloudFile.objects.filter(app=cloudapp)
        return super(FileListView, self).get(request, *args, **kwargs)


# make sure filename in the newly generated url (before query string) does
# end with trailing slash
# S3 is hard coded now. Allow other storages to be plugged in
class FileView(CloudAPIView):

    manager = FilesManager()
    
    def get(self, request, filename):
        try:
            contents = self.manager.retrieve(filename, request.app)
        except FileNotFound:
            return Response({"error": "File not found"},
                            status=status.HTTP_404_NOT_FOUND)
        mimetype, encoding = mimetypes.guess_type(filename)
        response =  HttpResponse(contents, mimetype = mimetype)
        #return Response({"url": cloudfile.url})
        return response
    
    
    def post(self, request, filename):
        content_length = request.META.get("CONTENT_LENGTH", 0)
        content_length = int(content_length)
        body = request.body
        cont_file = ContentFile(body)
        try:
            url = self.manager.save(filename, cont_file, request.app)
        except FileTooLarge as e:
            return Response({'error': str(e)}, 
                            status=401)
        except Exception:
            return Response({'error': 'Error uploading file'}, status=500)

        return Response({"url": url}, status=201)
    
    def delete(self, request, filename):
        try:
            self.manager.delete(filename, request.app)
        except FileNotFound:
            return Response({'error': "File not found"}, status=404)
        except Exception:
            return Response({'error': 'Error deleting file'}, status=500)
        return Response({"result": "File deleted successfully"})


