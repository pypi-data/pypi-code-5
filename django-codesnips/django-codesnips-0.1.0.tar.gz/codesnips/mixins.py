import json
from django.core.urlresolvers import resolve
from django.http import HttpResponseRedirect, HttpResponse

class ActiveToggleActionMixin(object):
    actions = ['activate', 'deactivate']
    readonly_fields = ['active']

    def activate(self, request, queryset):
        for obj in queryset:
            obj.active = True
            obj.save()
            self.message_user(request, "Activated %s" % (obj))
    activate.short_description = "Activate"

    def deactivate(self, request, queryset):
        for obj in queryset:
            obj.active = False
            obj.save()
            self.message_user(request, "Deactivated %s" % (obj))
    deactivate.short_description = "Deactivate"

    def get_actions(self, request):
        actions = super(ActiveToggleActionMixin, self).get_actions(request)

        # see if we're in the change view
        try:
            if resolve(request.path).url_name.endswith('_change'):
                # can't find a better way to get the current object....
                obj_id = int(request.path.rstrip('/').split('/')[-1])
                obj = super(ActiveToggleActionMixin, self).get_object(request, obj_id)
                if obj.active and 'activate' in actions:
                    del actions['activate']
                elif 'deactivate' in actions:
                    del actions['deactivate']
        except:
            pass # cant resolve the path, send default actions
        return actions

class ActionInChangeFormMixin(object):
    def response_action(self, request, queryset):
        """
        Prefer http referer for redirect
        """
        response = super(ActionInChangeFormMixin, self).response_action(request,
                queryset)
        if isinstance(response, HttpResponseRedirect):
            response['Location'] = request.META.get('HTTP_REFERER', response.url)
        return response

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'GET':
            actions = self.get_actions(request)
            if actions:
                action_form = self.action_form(auto_id=None)
                action_form.fields['action'].choices = self.get_action_choices(request)
            else:
                action_form = None
            extra_context = extra_context or {}
            extra_context.update({'action_form': action_form})
        return super(ActionInChangeFormMixin, self).change_view(request, object_id, form_url,
                                                                extra_context=extra_context)

class DjangoModelEncoder(json.JSONEncoder):
    def default(self, obj):
        from django.db.models import Model
        from django.core import serializers

        if isinstance(obj, Model):
            return json.loads(serializers.serialize("json", [obj]).strip('[]'))
        else:
            return super(DjangoModelEncoder, self).default(obj)

class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response from a class based view.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json.dumps(context, cls=DjangoModelEncoder)
