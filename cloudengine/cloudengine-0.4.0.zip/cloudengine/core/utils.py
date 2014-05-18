
from django.core.paginator import (Paginator, 
                    EmptyPage, PageNotAnInteger)
from rest_framework.settings import api_settings
from rest_framework.pagination import PaginationSerializer

def paginate(request, list_result):
    try:
        page_size = request.QUERY_PARAMS['page_size']
        page_size = int(page_size)
        if not page_size:
            return list_result
    except KeyError:
        page_size = api_settings.PAGINATE_BY  
    paginator = Paginator(list_result, page_size)
    page = request.QUERY_PARAMS.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    serializer = PaginationSerializer(instance=objects)
    return serializer.data
