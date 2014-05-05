#encoding=utf-8
from django.db import models
from django.conf import settings
from datetime import datetime
import calendar


class ParameterManager(models.Manager):

    def parameter_compare(self, one, other):
        if getattr(one, 'factor', 0) > getattr(other, 'factor', 0):
            return -1
        elif getattr(one, 'factor', 0) == getattr(other, 'factor', 0):
            if getattr(one, 'arg_num', 0) <= getattr(other, 'arg_num', 0):
                return 1
            else:
                return -1
        else:
            return 1

    def get_parameters(self, app, version=None, channel=None,
                       since=None, last_modify=None):
        """获得在线参数
            - app，应用id
            - version，应用的版本号
            - channel，应用的渠道
            - since，版本对应应用的安装时间, utc时间戳。
            - last_modify, 上次成功更新的最新时间。utc时间戳。
        """
        parameters = self.get_query_set().filter(app=app)
        if last_modify:
            last_modify = datetime.fromtimestamp(last_modify)
            parameters = parameters.filter(modify_time__lte=last_modify)
        parameters = [v for v in parameters if
                      v.calculate_factor(version, channel, since) >= 0]
        data, mdata = {}, {}
        for p in parameters:
            if p.name in data:
                if isinstance(data[p.name], list):
                    data[p.name].append(p)
                else:
                    data[p.name] = [data[p.name], p]
                mdata[p.name] = data[p.name]
            else:
                data[p.name] = p

        if mdata:
            for key, value in mdata.iteritems():
                value = sorted(value, cmp=self.parameter_compare)
                data[key] = value[0]

        return data.values()


class Parameter(models.Model):
    app = models.CharField(u'应用', max_length=100,
                           choices=settings.APP_DEFINITION)
    version = models.CharField(u'版本', max_length=20, null=True, blank=True)
    channel = models.CharField(u'渠道', max_length=20, null=True, blank=True)
    name = models.CharField(u'参数名', max_length=255)
    value = models.CharField(u'参数值', max_length=1000)

    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    modify_time = models.DateTimeField(auto_now=True, editable=False)
    effect_time = models.DateTimeField(null=True, blank=True)

    objects = ParameterManager()

    class Meta:
        verbose_name = u'在线参数'
        verbose_name_plural = u'在线参数'

    def __unicode__(self):
        return self.name

    def calculate_factor(self, version, channel, since):
        """该参数与条件的匹配度。
        如果参数不完全匹配视为不匹配。
        如果参数匹配，则返回参数个数。
        - 0 无多余匹配
        """

        factor = 0
        number = 0
        if self.version:
            number += 1
            if version != self.version:
                return -1
            factor += 1
        if self.channel:
            number += 1
            if channel != self.channel:
                return -1
            factor += 1
        if self.effect_time:
            number += 1
            if not since or (
                    since < calendar.timegm(self.effect_time.timetuple())):
                return -1
            factor += 1
        self.arg_num = number
        self.factor = factor
        return factor
