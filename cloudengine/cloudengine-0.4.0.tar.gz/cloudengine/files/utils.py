
from cloudengine.files.models import CloudFile


def get_total_size(owner):
    total_size = 0
    try:
        all_files = CloudFile.objects.filter(owner=owner)
        for file in all_files:
            total_size += file.size
    except Exception:
        pass

    return total_size


def delete_app_files(app):
    try:
        files = CloudFile.objects.filter(app=app)
    except CloudFile.DoesNotExist:
        pass
    for fileobj in files:
        fileobj.content.delete()
        fileobj.delete()