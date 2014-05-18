import mimetypes
import logging, urllib
from models import CloudFile
from exceptions import FileTooLarge, FileNotFound
from manager import FilesManager
from cloudengine.files.forms import FileUploadForm
from cloudengine.core.models import CloudApp
from django.views.generic import TemplateView
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.conf import settings

logger = logging.getLogger("cloudengine")


class AppFilesView(TemplateView):
    
    template_name= "app_files.html"
    form = FileUploadForm()
    msg = ''
    
    def __init__(self):
        try:
            backend = settings.CLOUDFILE_BACKEND
            backend = __import__(backend)
            self.manager = FilesManager(backend = backend)
        except Exception:
            self.manager = FilesManager()
            
    
    def get_context_data(self):
        curr_app = self.request.session.get("current_app", None)
        files = []
        if curr_app:
            app  = CloudApp.objects.get(name = curr_app)
            files = CloudFile.objects.filter(app = app)
        return {'app_name': curr_app, 'files': files,
                'form' : self.form, 'msg': self.msg,
                }
    
    def post(self, request, *args, **kwargs):
        myfile = request.FILES.get("file", None)
        app = request.POST.get("app", "")
        appobj = self.is_validapp(app)
        error_msg = ""
        if not myfile:
            error_msg = "Please select a file to upload."
        elif not appobj:
            error_msg = "Please select an app before uploading file."
        
        if error_msg:
            self.msg = error_msg
            return redirect('cloudengine-app-files')

        try:
            self.manager.save(myfile.name, myfile, appobj)
            self.msg = "File uploaded successfully!"
        except FileTooLarge as e:
            self.msg = str(e)
        except Exception as ex:
            self.msg = "Error uploading file"
            logger.error(str(ex))
        request.session['current_app'] = app
        return redirect("cloudengine-app-files")

    def is_validapp(self, app):
        try:
            return CloudApp.objects.get(name=app)
        except CloudApp.DoesNotExist:
            return False
    

def download_file(request, appname, filename):
    manager = FilesManager()
    print filename
    filename = urllib.unquote(filename)
    print filename
    try:
        app = CloudApp.objects.get(name=appname)
    except CloudApp.DoesNotExist:
        return HttpResponse("Invalid App", status=500)
    
    try:
        contents = manager.retrieve(filename, app)
    except FileNotFound:
        return HttpResponse("File not found", status=404)
    except Exception:
        return HttpResponse("Internal server error", status=500)
    
    mimetype, encoding = mimetypes.guess_type(filename)
    response = HttpResponse(contents, mimetype = mimetype)
    response["Content-Disposition"] = "attachment; filename=%s"%filename
    return response
    
