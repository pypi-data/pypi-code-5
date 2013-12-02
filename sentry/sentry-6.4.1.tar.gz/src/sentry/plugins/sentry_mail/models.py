"""
sentry.plugins.sentry_mail.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import sentry

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from sentry.models import User, UserOption
from sentry.plugins import register
from sentry.plugins.bases.notify import NotificationPlugin
from sentry.utils.cache import cache
from sentry.utils.email import MessageBuilder, group_id_to_email
from sentry.utils.http import absolute_uri

NOTSET = object()


class MailPlugin(NotificationPlugin):
    title = _('Mail')
    conf_key = 'mail'
    slug = 'mail'
    version = sentry.VERSION
    author = "Sentry Team"
    author_url = "https://github.com/getsentry/sentry"
    project_default_enabled = True
    project_conf_form = None
    subject_prefix = settings.EMAIL_SUBJECT_PREFIX

    def _send_mail(self, subject, template=None, html_template=None, body=None,
                   project=None, headers=None, context=None, fail_silently=False):
        send_to = self.get_send_to(project)
        if not send_to:
            return

        subject_prefix = self.get_option('subject_prefix', project) or self.subject_prefix

        msg = MessageBuilder(
            subject='%s%s' % (subject_prefix, subject),
            template=template,
            html_template=html_template,
            body=body,
            headers=headers,
            context=context,
        )
        msg.send(send_to, fail_silently=fail_silently)

    def send_test_mail(self, project=None):
        self._send_mail(
            subject='Test Email',
            body='This email was requested as a test of Sentry\'s outgoing email',
            project=project,
            fail_silently=False,
        )

    def get_notification_settings_url(self):
        return absolute_uri(reverse('sentry-account-settings-notifications'))

    def on_alert(self, alert):
        project = alert.project
        subject = '[{0}] ALERT: {1}'.format(
            project.name.encode('utf-8'),
            alert.message.encode('utf-8'),
        )
        template = 'sentry/emails/alert.txt'
        html_template = 'sentry/emails/alert.html'

        context = {
            'alert': alert,
            'link': alert.get_absolute_url(),
            'settings_link': self.get_notification_settings_url(),
        }

        headers = {
            'X-Sentry-Project': project.name,
        }

        self._send_mail(
            subject=subject,
            template=template,
            html_template=html_template,
            project=project,
            fail_silently=False,
            headers=headers,
            context=context,
        )

    def get_emails_for_users(self, user_ids, project=None):
        email_list = set()
        user_ids = set(user_ids)

        # XXX: It's possible that options have been set to an empty value
        if project:
            alert_queryset = UserOption.objects.filter(
                project=project,
                user__in=user_ids,
                key='mail:email',
            )
            for option in (o for o in alert_queryset if o.value):
                user_ids.remove(option.user_id)
                email_list.add(option.value)

        if user_ids:
            alert_queryset = UserOption.objects.filter(
                user__in=user_ids,
                key='alert_email',
            )
            for option in (o for o in alert_queryset if o.value):
                user_ids.remove(option.user_id)
                email_list.add(option.value)

        if user_ids:
            email_list |= set(User.objects.filter(
                pk__in=user_ids, is_active=True
            ).values_list('email', flat=True))

        return email_list

    def get_send_to(self, project=None):
        """
        Returns a list of email addresses for the users that should be notified of alerts.

        The logic for this is a bit complicated, but it does the following:

        The results of this call can be fairly expensive to calculate, so the send_to list gets cached
        for 60 seconds.
        """
        if project:
            project_id = project.pk
        else:
            project_id = ''
        conf_key = self.get_conf_key()
        cache_key = '%s:send_to:%s' % (conf_key, project_id)

        send_to_list = cache.get(cache_key)
        if send_to_list is None:
            send_to_list = set()

            if project and project.team:
                member_set = self.get_sendable_users(project)
                send_to_list |= set(self.get_emails_for_users(
                    member_set, project=project))

            send_to_list = filter(bool, send_to_list)
            cache.set(cache_key, send_to_list, 60)  # 1 minute cache
        return send_to_list

    def notify_users(self, group, event, fail_silently=False):
        project = group.project

        interface_list = []
        for interface in event.interfaces.itervalues():
            body = interface.to_email_html(event)
            if not body:
                continue
            interface_list.append((interface.get_title(), mark_safe(body)))

        subject = '[%s] %s: %s' % (
            project.name.encode('utf-8'),
            unicode(event.get_level_display()).upper().encode('utf-8'),
            event.error().encode('utf-8').splitlines()[0])

        link = group.get_absolute_url()

        template = 'sentry/emails/error.txt'
        html_template = 'sentry/emails/error.html'

        context = {
            'group': group,
            'event': event,
            'link': link,
            'interfaces': interface_list,
            'settings_link': self.get_notification_settings_url(),
        }

        headers = {
            'X-Sentry-Logger': event.logger,
            'X-Sentry-Logger-Level': event.get_level_display(),
            'X-Sentry-Project': project.name,
            'X-Sentry-Server': event.server_name,
            'X-Sentry-Reply-To': group_id_to_email(group.pk),
        }

        self._send_mail(
            subject=subject,
            template=template,
            html_template=html_template,
            project=project,
            fail_silently=fail_silently,
            headers=headers,
            context=context,
        )


# Legacy compatibility
MailProcessor = MailPlugin

register(MailPlugin)
