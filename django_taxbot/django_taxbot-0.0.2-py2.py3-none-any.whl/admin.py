from django.contrib import admin
from tax_toffee import models as mod

# Register your models here.
admin.site.register(mod.Tax)
admin.site.register(mod.CanadianTax)
