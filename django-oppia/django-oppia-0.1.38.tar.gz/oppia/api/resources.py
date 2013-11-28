# oppia/api/resources.py
import datetime
import json
import os
import shutil
import zipfile

from django.conf.urls import url
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.core import serializers
from django.core.servers.basehttp import FileWrapper
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse ,Http404
from django.utils.translation import ugettext_lazy as _

from tastypie import fields, bundle, http
from tastypie.authentication import Authentication,ApiKeyAuthentication
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError 
from tastypie.exceptions import Unauthorized, HydrationError, InvalidSortError, ImmediateHttpResponse
from tastypie.models import ApiKey
from tastypie.resources import ModelResource, Resource, convert_post_to_patch, dict_strip_unicode_keys
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.validation import Validation

from oppia.api.serializers import PrettyJSONSerializer, CourseJSONSerializer, TagJSONSerializer, UserJSONSerializer
from oppia.models import Activity, Section, Tracker, Course, CourseDownload, Media, Schedule, ActivitySchedule, Cohort, Tag, CourseTag
from oppia.models import Points, Award, Badge
from oppia.profile.forms import RegisterForm
from oppia.signals import course_downloaded

class UserResource(ModelResource):
    ''' 
    For user login
    
    Usage:
    POST request to ``http://localhost/api/v1/user/``
    
    Required arguments:
    
    * ``username``
    * ``password``
    
    Returns (if authorized):
    
    Object with ``first_name``, ``last_name``, ``api_key``, ``last_login``, ``username``, ``points``, ``badges``, and ``scoring``
    
    If unauthorized returns an HTTP 401 response
    
    '''
    points = fields.IntegerField(readonly=True)
    badges = fields.IntegerField(readonly=True)
    scoring = fields.BooleanField(readonly=True)
    metadata = fields.CharField(readonly=True)
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['first_name', 'last_name', 'last_login','username', 'points','badges']
        allowed_methods = ['post']
        authentication = Authentication()
        authorization = Authorization()
        serializer = UserJSONSerializer()
        always_return_data = True       
    
    def obj_create(self, bundle, **kwargs):
        
        if 'username' not in bundle.data:
            raise BadRequest(_(u'Username missing'))
        
        if 'password' not in bundle.data:
            raise BadRequest(_(u'Password missing'))
        
        username = bundle.data['username']
        password = bundle.data['password']
        
        u = authenticate(username=username, password=password)
        if u is not None:
            if u.is_active:
                login(bundle.request,u)
            else:
                raise BadRequest(_(u'Authentication failure'))
        else:
            raise BadRequest(_(u'Authentication failure'))

        del bundle.data['password']
        key = ApiKey.objects.get(user = u)
        bundle.data['api_key'] = key.key
        bundle.obj = u 
        return bundle 
    
    def dehydrate_points(self,bundle):
        points = Points.get_userscore(User.objects.get(username=bundle.request.user.username))
        return points
    
    def dehydrate_badges(self,bundle):
        badges = Award.get_userawards(User.objects.get(username=bundle.request.user.username))
        return badges 
    
    def dehydrate_scoring(self,bundle):
        return settings.OPPIA_POINTS_ENABLED
    
    def dehydrate_metadata(self,bundle):
        return settings.OPPIA_METADATA

class RegisterResource(ModelResource):
    ''' 
    For user registration
    '''
    points = fields.IntegerField(readonly=True)
    badges = fields.IntegerField(readonly=True)
    scoring = fields.BooleanField(readonly=True)
    metadata = fields.CharField(readonly=True)
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'register'
        allowed_methods = ['post']
        fields = ['username', 'first_name','last_name','email','points']
        authorization = Authorization() 
        always_return_data = True 
        include_resource_uri = False
         
    def obj_create(self, bundle, **kwargs):
        if not settings.OPPIA_ALLOW_SELF_REGISTRATION:
            raise BadRequest(_(u'Registration is disabled on this server.'))
        required = ['username','password','passwordagain', 'email', 'firstname', 'lastname']
        for r in required:
            try:
                bundle.data[r]
            except KeyError:
                raise BadRequest(_(u'Please enter your %s') % r)
        data = {'username': bundle.data['username'],
                'password': bundle.data['password'],
                'password_again': bundle.data['passwordagain'],
                'email': bundle.data['email'],
                'first_name': bundle.data['firstname'],
                'last_name': bundle.data['lastname'],}
        rf = RegisterForm(data)
        if not rf.is_valid():
            str = ""
            for key, value in rf.errors.items():
                for error in value:
                    str += error + "\n"
            raise BadRequest(str)
        else:
            username = bundle.data['username']
            password = bundle.data['password']
            email = bundle.data['email']
            first_name = bundle.data['firstname']
            last_name = bundle.data['lastname']
        try:
            bundle.obj = User.objects.create_user(username, email, password)
            bundle.obj.first_name = first_name
            bundle.obj.last_name = last_name
            bundle.obj.save()
            u = authenticate(username=username, password=password)
            if u is not None:
                if u.is_active:
                    login(bundle.request, u)
            key = ApiKey.objects.get(user = u)
            bundle.data['api_key'] = key.key
        except IntegrityError:
            raise BadRequest(_(u'Username "%s" already in use, please select another' % username))
        del bundle.data['passwordagain']
        del bundle.data['password']
        del bundle.data['firstname']
        del bundle.data['lastname']
        return bundle   
 
    def dehydrate_points(self,bundle):
        points = Points.get_userscore(User.objects.get(username__exact=bundle.data['username']))
        return points
    
    def dehydrate_badges(self,bundle):
        badges = Award.get_userawards(User.objects.get(username__exact=bundle.data['username']))
        return badges 
    
    def dehydrate_scoring(self,bundle):
        return settings.OPPIA_POINTS_ENABLED
    
    def dehydrate_metadata(self,bundle):
        return settings.OPPIA_METADATA
    
class TrackerResource(ModelResource):
    ''' 
    Submitting a Tracker
    '''
    user = fields.ForeignKey(UserResource, 'user')
    points = fields.IntegerField(readonly=True)
    badges = fields.IntegerField(readonly=True)
    scoring = fields.BooleanField(readonly=True)
    metadata = fields.CharField(readonly=True)
    
    class Meta:
        queryset = Tracker.objects.all()
        resource_name = 'tracker'
        allowed_methods = ['post','patch']
        detail_allowed_methods = ['post','patch']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        serializer = PrettyJSONSerializer()
        always_return_data =  True
        fields = ['points','digest','data','tracker_date','badges','course','completed','scoring','metadata']
              
    def hydrate(self, bundle, request=None):
        # remove any id if this is submitted - otherwise it may overwrite existing tracker item
        if 'id' in bundle.data:
            del bundle.obj.id
        bundle.obj.user = bundle.request.user
        bundle.obj.ip = bundle.request.META.get('REMOTE_ADDR','0.0.0.0')
        bundle.obj.agent = bundle.request.META.get('HTTP_USER_AGENT','unknown')
            
        # find out the course & activity type from the digest
        try:
            if 'course' in bundle.data:
                activities = Activity.objects.filter(digest=bundle.data['digest'],section__course__shortname=bundle.data['course'])[:1]
            else:
                activities = Activity.objects.filter(digest=bundle.data['digest'])[:1]
            if activities.count() > 0:
                activity = activities[0]
                bundle.obj.course = activity.section.course
                bundle.obj.type = activity.type
        except Activity.DoesNotExist:
            pass
        
        try:
            if 'course' in bundle.data:
                media_objs = Media.objects.filter(digest=bundle.data['digest'],course__shortname=bundle.data['course'])[:1]
            else:
                media_objs = Media.objects.filter(digest=bundle.data['digest'])[:1]
            if media_objs.count() > 0:
                media = media_objs[0]
                bundle.obj.course = media.course
                bundle.obj.type = 'media'
        except Media.DoesNotExist:
            pass
        
        # this try/except block is temporary until everyone is using client app v17
        try:
            json_data = json.loads(bundle.data['data'])
            if json_data['activity'] == "completed":
                bundle.obj.completed = True
        except:
            bundle.obj.completed = False
        
        try:
            json_data = json.loads(bundle.data['data'])
            if json_data['timetaken']:
                bundle.obj.time_taken = json_data['timetaken']
        except:
            pass
        
        return bundle 
    
    def dehydrate_points(self,bundle):
        points = Points.get_userscore(bundle.request.user)
        return points
    
    def dehydrate_badges(self,bundle):
        badges = Award.get_userawards(bundle.request.user)
        return badges
    
    def dehydrate_scoring(self,bundle):
        return settings.OPPIA_POINTS_ENABLED
    
    def dehydrate_metadata(self,bundle):
        return settings.OPPIA_METADATA
    
    def patch_list(self,request,**kwargs):
        request = convert_post_to_patch(request)
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        for data in deserialized["objects"]:
            data = self.alter_deserialized_detail_data(request, data)
            bundle = self.build_bundle(data=dict_strip_unicode_keys(data))
            bundle.request.user = request.user
            bundle.request.META['REMOTE_ADDR'] = request.META.get('REMOTE_ADDR','0.0.0.0')
            bundle.request.META['HTTP_USER_AGENT'] = request.META.get('HTTP_USER_AGENT','unknown')
            self.obj_create(bundle, request=request)
        response_data = {'points': self.dehydrate_points(bundle),
                         'badges':self.dehydrate_badges(bundle),
                         'scoring':self.dehydrate_scoring(bundle),
                         'metadata':self.dehydrate_metadata(bundle)}
        response = HttpResponse(content=json.dumps(response_data),content_type="application/json; charset=utf-8")
        return response
    
class CourseResource(ModelResource):
    
    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        allowed_methods = ['get']
        fields = ['id', 'title', 'version', 'shortname','is_draft']
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization() 
        serializer = CourseJSONSerializer()
        always_return_data = True
        include_resource_uri = True
   
    def get_object_list(self,request):
        if request.user.is_staff:
            return Course.objects.filter(is_archived=False)
        else:
            return Course.objects.filter(is_archived=False,is_draft=False)
        
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/download%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('download_detail'), name="api_download_detail"),
            ]

    def download_detail(self, request, **kwargs):
        self.is_authenticated(request)
        self.throttle_check(request)
        
        pk = kwargs.pop('pk', None)
        try:
            if request.user.is_staff:
                course = self._meta.queryset.get(pk = pk,is_archived=False)
            else:
                course = self._meta.queryset.get(pk = pk, is_archived=False,is_draft=False)
        except Course.DoesNotExist:
            raise Http404()
         
        file_to_download = course.getAbsPath();
        schedule = course.get_default_schedule()
        has_completed_trackers = Tracker.has_completed_trackers(course,request.user)
        cohort = Cohort.member_now(course,request.user)
        if cohort:
            if cohort.schedule:
                schedule = cohort.schedule
        
        # add scheduling XML file     
        if schedule or has_completed_trackers:
            file_to_download = settings.COURSE_UPLOAD_DIR +"temp/"+ str(request.user.id) + "-" + course.filename
            shutil.copy2(course.getAbsPath(), file_to_download)
            zip = zipfile.ZipFile(file_to_download,'a')
            if schedule:
                zip.writestr(course.shortname +"/schedule.xml",schedule.to_xml_string())
            if has_completed_trackers:
                zip.writestr(course.shortname +"/tracker.xml",Tracker.to_xml_string(course,request.user))
            zip.close()

        wrapper = FileWrapper(file(file_to_download))
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Length'] = os.path.getsize(file_to_download)
        response['Content-Disposition'] = 'attachment; filename="%s"' %(course.filename)
        
        md = CourseDownload()
        md.user = request.user
        md.course = course
        md.course_version = course.version
        md.ip = request.META.get('REMOTE_ADDR','0.0.0.0')
        md.agent= request.META.get('HTTP_USER_AGENT','unknown')
        md.save()
        
        course_downloaded.send(sender=self, course=course, user=request.user)
        
        return response
    
    def dehydrate(self, bundle):
        # Include full download url
        if bundle.request.is_secure():
            prefix = 'https://'
        else:
            prefix = 'http://'
        bundle.data['url'] = prefix + bundle.request.META['SERVER_NAME'] + bundle.data['resource_uri'] + 'download/'
        # make sure title is shown as json object (not string representation of one)
        bundle.data['title'] = json.loads(bundle.data['title'])
        
        course = Course.objects.get(pk=bundle.obj.pk)
        schedule = course.get_default_schedule()
        cohort = Cohort.member_now(course,bundle.request.user)
        if cohort:
            if cohort.schedule:
                schedule = cohort.schedule
        if schedule:
            bundle.data['schedule'] = schedule.lastupdated_date.strftime("%Y%m%d%H%M%S")
            sr = ScheduleResource()
            bundle.data['schedule_uri'] = sr.get_resource_uri(schedule)
        
        return bundle
    
class CourseTagResource(ModelResource):
    course = fields.ToOneField('oppia.api.resources.CourseResource', 'course', full=True)
    class Meta:
        queryset = CourseTag.objects.all()
        allowed_methods = ['get']
        fields = ['id','course','tag']
        include_resource_uri = False
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        always_return_data = True  
         
class ScheduleResource(ModelResource):
    activityschedule = fields.ToManyField('oppia.api.resources.ActivityScheduleResource', 'activityschedule_set', related_name='schedule', full=True, null=True)
    class Meta:
        queryset = Schedule.objects.all()
        resource_name = 'schedule'
        allowed_methods = ['get']
        fields = ['id', 'title', 'lastupdated_date']
        authentication = ApiKeyAuthentication()
        authorization = Authorization() 
        always_return_data = True
        include_resource_uri = False
       
    def dehydrate(self, bundle):
        bundle.data['version'] = bundle.data['lastupdated_date'].strftime("%Y%m%d%H%M%S")
        return bundle 
   
class TagResource(ModelResource):
    count = fields.IntegerField(readonly=True)
    
    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'
        allowed_methods = ['get']
        fields = ['id','name']
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization() 
        always_return_data = True
        include_resource_uri = False
        serializer = TagJSONSerializer()
    
    def get_object_list(self,request):
        if request.user.is_staff:
            return Tag.objects.filter(courses__isnull=False, coursetag__course__is_archived=False).distinct().order_by("name")
        else:
            return Tag.objects.filter(courses__isnull=False, coursetag__course__is_archived=False,coursetag__course__is_draft=False).distinct().order_by("name")
        
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('tag_detail'), name="api_tag_detail"),
            ]
        
    def tag_detail(self, request, **kwargs): 
        self.is_authenticated(request)
        self.throttle_check(request)
        
        pk = kwargs.pop('pk', None)
        try:
            tag = self._meta.queryset.get(pk = pk)
        except Tag.DoesNotExist:
            raise Http404()
        
        if request.user.is_staff:
            courses = Course.objects.filter(tag=tag, is_archived=False).order_by("title")
        else:
            courses = Course.objects.filter(tag=tag, is_archived=False,is_draft=False).order_by("title")
        
        course_data = []
        cr = CourseResource()
        for c in courses:
            bundle = cr.build_bundle(obj=c,request=request)
            d = cr.full_dehydrate(bundle)
            course_data.append(bundle.data)
        
        response = HttpResponse(content=json.dumps({'id':pk,'count':courses.count(),'courses':course_data,'name':tag.name}),content_type="application/json; charset=utf-8")
        return response

    def dehydrate_count(self,bundle):
        tmp = Course.objects.filter(tag__id=bundle.obj.id, is_archived=False)
        if bundle.request.user.is_staff:
            count = tmp.count()
        else:
            count = tmp.filter(is_draft=False).count()
        return count
        
    def alter_list_data_to_serialize(self, request, data):
        if isinstance(data, dict):
            if 'objects' in data:
                data['tags'] = data['objects']
                del data['objects']  
        return data 
          
class ActivityScheduleResource(ModelResource):
    schedule = fields.ToOneField('oppia.api.resources.ScheduleResource', 'schedule', related_name='activityschedule')
    class Meta:
        queryset = ActivitySchedule.objects.all()
        resource_name = 'activityschedule'
        allowed_methods = ['get']
        fields = ['digest', 'start_date', 'end_date']
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization() 
        always_return_data = True
        include_resource_uri = False
        
    def dehydrate(self, bundle):
        bundle.data['start_date'] = bundle.data['start_date'].strftime("%Y-%m-%d %H:%M:%S")
        bundle.data['end_date'] = bundle.data['end_date'].strftime("%Y-%m-%d %H:%M:%S")
        return bundle
    
class PointsResource(ModelResource):
    class Meta:
        queryset = Points.objects.all().order_by('-date')
        allowed_methods = ['get']
        fields = ['date', 'description','points','type']
        resource_name = 'points'
        include_resource_uri = False
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        always_return_data = True
        
    def get_object_list(self, request):
        return super(PointsResource, self).get_object_list(request).filter(user = request.user)
    
    def dehydrate(self, bundle):
        bundle.data['date'] = bundle.data['date'].strftime("%Y-%m-%d %H:%M:%S")
        return bundle

class BadgesResource(ModelResource):
    class Meta:
        queryset = Badge.objects.all()
        allowed_methods = ['get']
        resource_name = 'badges'
        include_resource_uri = False
        serializer = PrettyJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        always_return_data = True
        
class AwardsResource(ModelResource):
    badge = fields.ForeignKey(BadgesResource, 'badge', full=True, null=True)
    badge_icon = fields.CharField(attribute='_get_badge', readonly=True)
    class Meta:
        queryset = Award.objects.all().order_by('-award_date')
        allowed_methods = ['get']
        resource_name = 'awards'
        include_resource_uri = False
        serializer = PrettyJSONSerializer()
        authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        always_return_data = True
        
    def get_object_list(self, request):
        return super(AwardsResource, self).get_object_list(request).filter(user = request.user)
    
    def dehydrate_badge_icon(self, bundle):
        if bundle.request.is_secure():
            prefix = 'https://'
        else:
            prefix = 'http://'
        url = prefix + bundle.request.META['SERVER_NAME'] + settings.MEDIA_URL + bundle.data['badge_icon']
        return url
    

    
    
