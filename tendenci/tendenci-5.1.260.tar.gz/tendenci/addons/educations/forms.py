from tendenci.addons.educations.models import Education
from tendenci.core.perms.forms import TendenciBaseForm
from django import forms


class EducationForm(TendenciBaseForm):

    status_detail = forms.ChoiceField(
        choices=(('active', 'Active'),
                 ('inactive', 'Inactive'),
                 ('pending', 'Pending'),))

    class Meta:
        model = Education
        fields = (
        'user',
        'school',
        'major',
        'degree',
        'graduation_dt',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status',
        'status_detail',
        )

        fieldsets = [('Education Information', {
                      'fields': ['user',
                                'school',
                                'major',
                                'degree',
                                'graduation_dt',
                                 ],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status',
                                 'status_detail'],
                      'classes': ['admin-only'],
                    })]

#    def __init__(self, *args, **kwargs):
#        super(IndustryForm, self).__init__(*args, **kwargs)
#
#        if not self.user.profile.is_superuser:
#            if 'status' in self.fields:
#                self.fields.pop('status')
#            if 'status_detail' in self.fields:
#                self.fields.pop('status_detail')
