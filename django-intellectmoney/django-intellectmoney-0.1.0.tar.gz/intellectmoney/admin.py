# -*- encoding: utf-8 -*-
from models import IntellectMoney
from django.contrib import admin


class IntellectMoneyAdmin(admin.ModelAdmin):
    list_display = ('id','orderId','created')


admin.site.register(IntellectMoney,IntellectMoneyAdmin)
