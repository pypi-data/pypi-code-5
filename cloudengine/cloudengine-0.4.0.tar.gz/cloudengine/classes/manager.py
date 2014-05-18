import copy
import logging 
import pymongo
from bson.objectid import ObjectId
from django.conf import settings
from cloudengine.classes.utils import validate_db_name
from cloudengine.classes.exceptions import (
                InvalidObjectError, InvalidSchemaError)

            
class SchemaHandler(object):
    client = pymongo.MongoClient(settings.MONGO_HOST)
    logger = logging.getLogger("cloudengine")
    
    def is_same_type(self, schema_value, curr_value):
            t = type(curr_value)
            if schema_value == "string":
                return t in (str, unicode)
            elif schema_value == "number":
                return t in (int, long, float)
            elif schema_value == "boolean":
                return t == bool
            elif schema_value == "array":
                return t == list
            elif schema_value == "object":
                return t == dict
            else:
                return False

    def get_data_type(self, value):
            type_map = {
                            str: "string",
                            unicode: "string",
                            int : "number",
                            float: "number",
                            long: "number",
                            bool: "boolean",
                            list: "array",
                            dict: "object"
                        }
            t = type(value)
            return type_map[t]

    def valid_schema(self, app_name, klass, obj):
        
        db = self.client[app_name]
        collection = db["schema"]
        schema = collection.find_one({"_collection": klass},
                                     {"_collection": False}
                                     )
        keys = obj.keys()
        
        if schema:
            self.logger.info("schema exists for the given collection")
            self.logger.info("Updating existing schema")
            schema_modified = {}
            
            for key in keys:
                curr_value = obj[key]
                try:
                    schema_value = schema[key]
                    if not self.is_same_type(schema_value, curr_value):
                        raise InvalidSchemaError("Key %s expected to be of type %s but received %s"%(
                                                          key, schema_value, self.get_data_type(curr_value)))                        
                except KeyError:
                    # A new column is being added
                    curr_type = self.get_data_type(curr_value)
                    schema_modified[key] = curr_type
            
            if schema_modified:
                collection.update({"_collection": klass},
                              {"$set": schema_modified})
        else:
            # A new collection is being created
            self.logger.info("creating a new schema for class %s"%klass)
            schema = {}
            for key in keys:
                curr_value = obj[key]
                curr_type = self.get_data_type(curr_value)
                schema[key] = curr_type
            
            schema["_collection"] = klass
            collection.insert(schema)
            
        return True

    # todo: add collection name validation similar to validate_db_name??
    def get_class_schema(self, app_name, klass):
        db = self.client[app_name]
        collection = db["schema"]
        schema = collection.find_one({"_collection": klass},
                                     {"_collection": False, 
                                      "_id": False}
                                     )
        if schema:
            self.logger.info("Schema exists")
            return schema
        else:
            self.logger.info("Schema doesn't exist. Creating new schema")
            schema = {}
            # check if there are any documents present under this collection
            db = self.client[app_name]
            collection = db[klass]
            if not collection.find_one():
                self.logger.info("No existing documents found. Schema cannot be created")
                return schema
            
            #try to create a schema by looking at first 10 records
            sample_docs = collection.find({}, {"app_id": False,
                                               "_id": False}, 
                                          limit=10)
            self.logger.info("Generating new schema from %d sample documents"%sample_docs.count())
            for doc in sample_docs:
                schema_keys = schema.keys()
                keys = doc.keys()
                self.logger.info("schema keys: %s, current doc keys: %s"%(str(schema_keys), str(keys)))
                if set(keys) != set(schema_keys):
                    self.logger.info("schema missing a few keys from current doc")
                    for key in keys:
                        if key not in schema_keys:
                            self.logger.info("adding key %s to schema"%key)
                            curr_value = doc[key]
                            curr_type = self.get_data_type(curr_value)
                            schema[key] = curr_type
                    
            #save this schema in db
            coll_schema = copy.deepcopy(schema)
            coll_schema["_collection"] = klass
            
            db = self.client["schema"]
            collection = db[app_name]
            collection.insert(coll_schema)
            
            return schema
        
    def remove_schema(self, app_name, klass):
        db = self.client[app_name]
        coll = db["schema"]
        coll.remove({"_collection": klass})
        
                    


class ClassesManager(object):
    client = pymongo.MongoClient(settings.MONGO_HOST)
    schema_handler = SchemaHandler()
    ce_system_classes = ("schema",)
    
    def get_classes(self, db):
        db = validate_db_name(db)
        db = self.client[db]
        collections = db.collection_names(include_system_collections=False)
        app_classes = []
        for coll in collections:
            doc = db[coll].find_one()
            if doc and (coll not in self.ce_system_classes): 
                app_classes.append(coll)
        return app_classes
    
    
    def get_class(self, db, klass, query, sort_key=None, direction = None):
        db = validate_db_name(db)
        try:
            if direction:
                assert(direction == pymongo.ASCENDING or direction == pymongo.DESCENDING)
        except AssertionError:
            raise Exception("valid values for order are 1 & -1")
        
        db = self.client[db]
        collection = db[klass]
        cursor = collection.find(query)      
        if sort_key:
            cursor = cursor.sort(sort_key, direction)
            
        res = [doc for doc in cursor]

        for doc in res:
            objid = doc["_id"]
            doc["_id"] = str(objid)
        return res
    
    
    def delete_class(self, db_name, klass):
        db_name = validate_db_name(db_name)
        db = self.client[db_name]
        if klass in db.collection_names():
            db.drop_collection(klass)
            self.schema_handler.remove_schema(db_name, klass)


    def add_object(self, db_name, klass, obj):
        db_name = validate_db_name(db_name)
        db = self.client[db_name]
        collection = db[klass]
        keys = obj.keys()
        self.schema_handler.valid_schema(db_name, klass, obj)
        if ("_id" in keys):
            raise InvalidObjectError("Invalid object. _id is a reserved field")
        
        objid = collection.insert(obj)
        return objid
    
    
    def add_multiple_objects(self, db, klass, objects):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        for obj in objects:
            keys = obj.keys()
            if ("_id" in keys):
                raise Exception("Invalid object. _id is a reserved field")
        ids = collection.insert(objects)
        return ids
        
        
    def get_object(self, db, klass, id):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        query = {"_id": ObjectId(id)}
        obj = collection.find_one( query)
        if obj:
            objid = obj["_id"]
            obj["_id"] = str(objid)
        return obj
        
        
    def update_object(self, db_name, klass, id, obj):
        db_name = validate_db_name(db_name)
        db = self.client[db_name]
        collection = db[klass]
        updates = obj.keys()
        self.schema_handler.valid_schema(db_name, klass, obj)
        if ("_id" in updates):
            raise Exception("Invalid object. _id is a reserved field")
        collection.update({"_id": ObjectId(id)},
                          {"$set": obj})               # todo: set multi = true??
        
    def delete_object(self, db, klass, id):
        db = validate_db_name(db)
        db = self.client[db]
        collection = db[klass]
        collection.remove(ObjectId(id))
        if not collection.count():
            db.drop_collection(klass)
        
    def delete_app_data(self, db):
        db = validate_db_name(db)
        self.client.drop_database(db)
