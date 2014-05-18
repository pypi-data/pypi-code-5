from datetime import datetime, timedelta
from django.views.generic import TemplateView
from django.core.context_processors import csrf
from django.utils.timezone import utc
from django.http import HttpResponse
from cloudengine.core.forms import CreateAppForm
from cloudengine.core.models import CloudApp, CloudAPI
from cloudengine.auth.models import Token
from cloudengine.push.models import PushNotification
from cloudengine.users.models import AppUser


class AccountKeysView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(AccountKeysView, self).get_context_data(**kwargs)
        apps = CloudApp.objects.all()
        context['apps'] = apps
        try:
            token = Token.objects.get(user=self.request.user)
            context['api_key'] = token.key
        except Token.DoesNotExist:
            context['api_key'] = ''
        return context


class AdminHomeView(TemplateView):
    template_name = 'admin_home.html'
    
    def get_context_data(self):
        apps = CloudApp.objects.all()
        if not apps:
            return {'n_apps': 0, 'n_api' : 0,
                'n_push': 0, 'n_users': 0}
        
        now = datetime.utcnow().replace(tzinfo=utc)
        today = now.date()
        one_month = timedelta(days=30)
        one_month_back = today - one_month
        try:
            res = CloudAPI.objects.filter(date__gt = one_month_back)
        except CloudAPI.DoesNotExist:
            res = []
        n_api = reduce(lambda x, y: x + y.count, res, 0)
        
        try:
            res = PushNotification.objects.filter(send_time__gt = one_month_back)
        except CloudAPI.DoesNotExist:
            res = []
        n_push = reduce(lambda x, y: x + y.num_subscribers, res, 0)
        
        users = AppUser.objects.all()
            
        return {'n_apps': len(apps), 'n_api' : n_api,
                'n_push': n_push, 'n_users': len(users)}


class CreateAppView(TemplateView):
    template_name = "create_app.html"
    form = CreateAppForm()
    msg  = ""
    
    def get_context_data(self):
        context = {}
        context.update(csrf(self.request))
        context['form'] = self.form
        context["msg"] = self.msg
        return context
        
    def post(self, request):
        form = CreateAppForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data['app_name']
            myapp = CloudApp(app_name)
            myapp.save()
            self.msg = "App created successfully!"
        else:
            self.form = form
        
        return self.get(request)


class AppSettingsView(TemplateView):
    template_name= "app_settings.html"

    def get_context_data(self, app_name):
        app = CloudApp.objects.get(name=app_name)
        apps = CloudApp.objects.all()
        token = Token.objects.all()[0]
        return { 'app_name': app_name, 'app': app,
                'api_key': token, 'apps': apps}


class AppsBrowser(TemplateView):
    template_name = "apps.html"

    def get_context_data(self):
        apps = CloudApp.objects.all()
        c = {'apps' : apps}
        return c
    
    
    