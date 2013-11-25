from datetime import datetime

from bson import ObjectId

from ming import Session
from ming import schema as S
from ming.datastore import create_datastore
from ming.orm import (
        Mapper,
        FieldProperty,
        )
from ming.orm.ormsession import ThreadLocalORMSession

from ming.orm.declarative import MappedClass

from .base import (
        StoredNode,
        StoredActivity,
        ActivityObject,
        Storage,
        )

activity_doc_session = Session.by_name("activitystream")
activity_orm_session = session = ThreadLocalORMSession(activity_doc_session)

class Node(MappedClass, StoredNode):
    class __mongometa__:
        session = activity_orm_session
        name = 'nodes'
        indexes = ['node_id']

    _id = FieldProperty(S.ObjectId)
    node_id = FieldProperty(str)
    followers = FieldProperty([str])
    following = FieldProperty([str])
    last_timeline_aggregation = FieldProperty(S.DateTime)

class ActivityObjectType(S.Object):
    def __init__(self, actor=False, **kw):
        fields = dict(
            activity_name=S.String(),
            activity_url=S.String(),
            activity_extras=S.Object({None: None}, if_missing={}),
            )
        if actor:
            fields['node_id'] = S.String()
        super(ActivityObjectType, self).__init__(fields=fields, **kw)

class Activity(MappedClass, StoredActivity):
    class __mongometa__:
        session = activity_orm_session
        name = 'activities'
        indexes = [
                ('node_id', 'published'),
                ('owner_id', 'score'),
                ]

    _id = FieldProperty(S.ObjectId)
    owner_id = FieldProperty(S.String, if_missing=None)
    node_id = FieldProperty(str)
    actor = FieldProperty(ActivityObjectType(actor=True))
    verb = FieldProperty(str)
    obj = FieldProperty(ActivityObjectType)
    target = FieldProperty(ActivityObjectType, if_missing=None)
    published = FieldProperty(datetime)
    score = FieldProperty(S.Float, if_missing=None)

Mapper.compile_all()


class MingStorage(Storage):
    """Ming storage engine."""

    def __init__(self, conf):
        """Initialize storage backend.

        :param conf: dictionary of config values

        """
        self.conf = conf
        datastore = create_datastore(
                conf['activitystream.master'].rstrip('/') + '/' +
                conf['activitystream.database'])
        Session._datastores['activitystream'] = datastore
        Session.by_name('activitystream').bind = datastore

    def create_edge(self, from_node, to_node):
        """Create a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        Node.query.update({"node_id": from_node.node_id},
                {"$addToSet": {"following": to_node.node_id}}, upsert=True)
        Node.query.update({"node_id": to_node.node_id},
                {"$addToSet": {"followers": from_node.node_id}}, upsert=True)

    def destroy_edge(self, from_node, to_node):
        """Destroy a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.

        """
        Node.query.update({"node_id": from_node.node_id},
                {"$pull": {"following": to_node.node_id}})
        Node.query.update({"node_id": to_node.node_id},
                {"$pull": {"followers": from_node.node_id}})

    def edge_exists(self, from_node, to_node):
        """Determine if there is a directed edge from :class:`Node`
        ``follower`` to :class:`Node` ``following``.

        """
        return Node.query.find({"node_id": from_node.node_id,
                "following": to_node.node_id}).first() is not None

    def get_node(self, node_id):
        """Return the node for the given node_id.

        """
        return Node.query.get(node_id=node_id)

    def get_nodes(self, node_ids):
        """Return nodes for the given node_ids.

        """
        return Node.query.find({"node_id": {"$in": node_ids}}).all()

    def create_node(self, node_id):
        """Create a new node.

        """
        node = Node(node_id=node_id)
        session.flush()
        return node

    def save_node(self, node):
        """Save a node.

        """
        session.flush()
        return node

    def save_activity(self, activity):
        """Save an activity.

        """
        activity = Activity(**activity.to_dict())
        session.flush()
        return activity

    def get_activities(self, nodes, since=None, sort=None, limit=None, skip=0, query=None):
        """Return all activities associated with the given nodes.

        Params:
            since (datetime) - return activities that have occured since this
                               datetime
        """
        node_ids = [node.node_id for node in nodes]
        q = {'node_id': {'$in': node_ids}}
        if since:
            q['published'] = {'$gte': since}
        if query:
            q.update(query)
        q['owner_id'] = None
        return Activity.query.find(q, sort=sort, limit=limit, skip=skip).all()

    def save_timeline(self, owner_id, activities):
        """Save a list of activities to a node's timeline.

        """
        session.clear()
        for a in activities:
            Activity(**a.to_dict(owner_id=owner_id))
        session.flush()

    def get_timeline(self, node_id, sort=None, limit=None, skip=0, query=None):
        """Return the timeline for node_id.

        Timeline is the already-aggregated list of activities in mongo.

        """
        q = {'owner_id': node_id}
        if query:
            q.update(query)
        return Activity.query.find(q, sort=sort, limit=limit, skip=skip).all()
