
from bottrap.models import BlockedIp
from django.http.response import HttpResponse


def honeypot(request):
    ip = request.META.get('REMOTE_ADDR', '')
    BlockedIp.objects.get_or_create(ip=ip)
    
    return HttpResponse("Congrats, you found the honeypot!")