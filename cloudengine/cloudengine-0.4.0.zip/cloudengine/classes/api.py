
import logging
import json
from rest_framework.response import Response
from rest_framework import status
from cloudengine.classes.manager import ClassesManager
from cloudengine.core.cloudapi_view import CloudAPIView
from cloudengine.core.utils import paginate
from cloudengine.classes.manager import SchemaHandler
from cloudengine.classes.exceptions import (
            InvalidObjectError, InvalidSchemaError)

logger = logging.getLogger("cloudengine")

manager = ClassesManager()


class AppClassesView(CloudAPIView):
    
    def get(self, request):
        app_classes = manager.get_classes(request.app.name)
        return Response(paginate(request, app_classes))


class ClassView(CloudAPIView):

    DEFAULT_QUERY = '{}'

    def get(self, request, cls):
        query_str = request.QUERY_PARAMS.get('query', self.DEFAULT_QUERY)
        try:
            # urlparse the query
            query = json.loads(query_str)
        except Exception:
            return Response({"error": "Invalid query"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        
        
        try:
            # urlparse the query
            order_str = request.GET['orderby']
            order_obj = json.loads(order_str)
            assert(len(order_obj) == 1)      # sorting possible only on one key
            order_by = order_obj.keys()[0]
            order = order_obj.values()[0]
        except AssertionError:
            return Response({'error': 'orderby option takes only one property value'},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        except Exception, e:
            order_by = order = None
        try:
            res = manager.get_class(request.app.name, cls, query, order_by, order)
        except Exception, e:
            return Response({'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            exception=True)
        return Response(paginate(request, res))

    def delete(self, request, cls):
        manager.delete_class( request.app.name, cls)
        return Response({"result" : "The class was deleted successfully"})

    def post(self, request, cls):
        try:
            objid = manager.add_object(request.app.name, cls, request.DATA)
        except InvalidObjectError:
            return Response({"error": "Invalid object"}, 
                            status= status.HTTP_400_BAD_REQUEST)
        except InvalidSchemaError as e:
            return Response({"error": str(e)},
                            status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error while adding object to db: %s"%str(e))
            return Response({
                "error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
        return Response({"_id": str(objid)}, status=201)


class ObjectView(CloudAPIView):

    def get(self, request, cls, objid):
        try:
            obj = manager.get_object(request.app.name, cls, objid)
        except Exception:
            return Response({"error": "Invalid object id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)
        if obj:
            return Response({"result": obj})
        else:
            return Response({"error": "Invalid object id"},
                            status=status.HTTP_400_BAD_REQUEST,
                            exception=True)

    # todo: _id cannot be updated by the request
    def put(self, request, cls, objid):
        try:
            manager.update_object(request.app.name, cls, objid, request.DATA)
        except Exception as e:
                return Response({
                    "error": "Invalid object. _id/app_id is a reserved field"},
                    status=status.HTTP_400_BAD_REQUEST
                                )
        return Response({"_id": str(objid), "result": "Object updated successfully"}, 
                        status=200)

    def delete(self, request, cls, objid):
        manager.delete_object(request.app.name, cls, objid)
        return Response({"result": "Object deleted successfully"})



class SchemaView(CloudAPIView):
    
    def get(self, request, cls):
        schema_handler = SchemaHandler()
        schema = schema_handler.get_class_schema(request.app.name, cls)
        return Response(schema)
        
        
        