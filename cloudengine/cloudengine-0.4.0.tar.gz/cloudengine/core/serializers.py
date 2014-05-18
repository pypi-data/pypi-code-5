from rest_framework import serializers
from cloudengine.core.models import CloudAPI


class CloudAPISerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CloudAPI
        fields = ('date', 'count')