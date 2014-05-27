from django.contrib.admin import site
from models import *

site.register(Job)
site.register(Mail)
site.register(MailTemplate)
site.register(NewsletterSettings)