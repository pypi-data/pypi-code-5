# coding=UTF-8
#
#	Copyright 2013-2014, Marten de Vries
#
#	Licensed under the Apache License, Version 2.0 (the "License");
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software
#	distributed under the License is distributed on an "AS IS" BASIS,
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#	See the License for the specific language governing permissions and
#	limitations under the License.

import pouchdb
#a hack, but: it works.
from pouchdb.context import QtCore, QtGui
import unittest
import requests
import json
import os
import numbers
import warnings
import base64

configPath = os.path.join(os.path.dirname(__file__), "testconfig.json")
try:
	with open(configPath) as f: #pragma: no branch
		data = json.load(f)
except IOError: #pragma: no cover
	data = {}

USERNAME = data.get("username")
PASSWORD = data.get("password")
BASE_URL = data.get("base_url", "http://localhost:5984")
STORAGE_DIR = data.get("storage_dir", "dbs")

HTTP_AUTH = None
if USERNAME: #pragma: no branch
	HTTP_AUTH = {
		"username": USERNAME,
		"password": PASSWORD,
	}


BULK_DOCS = {
	"docs": [
		{
			"a": 1,
			"b": 2,
		},
		{
			
			"c": 3,
			"d": 4,
		},
	],
}

QUERY_FUNC = {
	"map": """function (doc) {
		emit(null, doc._rev);
	}""",
}

REVS_DIFF_DATA = {
	"myDoc1": [
		"1-b2e54331db828310f3c772d6e042ac9c",
		"2-3a24009a9525bde9e4bfa8a99046b00d",
	],
}

ONLY_TEST_VALIDATION_DOC = {
	"_id": "_design/test",
	"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
		if (newDoc._id !== "test") {
			throw({forbidden: "only a document named 'test' is allowed."});
		}
	}""",
}

SHOW_DOCUMENT = {
	"_id": "_design/test",
	"shows": {
		"myshow": """function (doc, req) {
			if (!doc) {
				return {body: "no doc"}
			} else {
				return {body: doc.description}
			}
		}""",
		"args": """function (doc, req) {
			return toJSON([doc, req]);
		}""",
		"usingProviders": """function (doc, req) {
			provides("json", function () {
				return toJSON({message: "Hello World!"});
			});
			provides("html", function () {
				return "<h1>Hello World!</h1>";
			});
			provides("css", function () {
				return 'body {content: "Hello World!"}';
			});
			registerType("ascii-binary", "application/octet-stream; charset=ascii")
			provides("ascii-binary", function () {
				return {
					"base64": "SGVsbG8gV29ybGQh"
				};
			})
		}""",
		"oldStyleJson": """function (doc, req) {
			return {
				json: {
					old_style: "json"
				}
			};
		}""",
		"empty": """function (doc, req) {}""",
		"nofunc": """'Hello World!'""",
		"invalidsyntax": """function (doc, req)) {}"""
	}
}

LIST_DOCUMENT = {
	"_id": "_design/test",
	"views": {
		"ids": {
			"map": """function (doc) {
				emit(doc._id, "value");
			}""",
		}
	},
	"lists": {
		"args": """function (head, req) {
			return toJSON([head, req]);
		}""",
		"use-list-api": """function (head, req) {
			start({code: 500});
			send(JSON.stringify(getRow()));
			send("\\n");
			send("test");
			return "Hello World!";
		}""",
	}
}

UPDATE_DOCUMENT = {
	"_id": "_design/test",
	"updates": {
		"args": """function (doc, req) {
			return [null, toJSON([doc, req])];
		}""",
	}
}

FAST_ONLY = bool(int(os.environ.get("TEST_FAST", "0")))

class PouchDBTestCase(unittest.TestCase):
	def assertUuid(self, uuid):
		self.assertIsInstance(uuid, basestring)
		self.assertEqual(len(uuid), 36)

class SyncPouchDBTestCase(PouchDBTestCase):
	"""Resets the context after running a test"""

	def setUp(self):
		self._env = pouchdb.setup(storageDir=STORAGE_DIR, baseUrl=BASE_URL)
		self.waitUntilCalled = self._env.context.waitUntilCalled

	def tearDown(self):
		self._env.context.reset()

class AsyncPouchDBTestCase(PouchDBTestCase):
	"""Resets the context after running a test"""

	def setUp(self):
		self._env = pouchdb.setup(storageDir=STORAGE_DIR, async=True, baseUrl=BASE_URL)
		self.waitUntilCalled = self._env.context.waitUntilCalled

	def tearDown(self):
		self._env.context.reset()

	def assertPromise(self, promise):
		self.assertIn("then", promise)
		self.assertIn("catch", promise)

class SyncPouchDBTestCaseWithDB(SyncPouchDBTestCase):
	"""Sets up a db named 'test' and resets the context afterwards."""

	def setUp(self):
		super(SyncPouchDBTestCaseWithDB, self).setUp()

		self._db = self._env.PouchDB("test")

class AsyncPouchDBTestCaseWithDB(AsyncPouchDBTestCase):
	"""Sets up a db named 'test' and resets the context afterwards."""

	def setUp(self):
		super(AsyncPouchDBTestCaseWithDB, self).setUp()

		self._db = self._env.PouchDB("test")

class SyncPouchDBTestCaseWithDBAndDoc(SyncPouchDBTestCaseWithDB):
	"""Sets up a db named 'test', a document named 'mytest' and resets
	   the context afterwards.

	"""
	def setUp(self):
		super(SyncPouchDBTestCaseWithDBAndDoc, self).setUp()

		resp = self._db.put({"_id": "mytest", "test": True})
		self.rev = resp["rev"]

class AsyncPouchDBTestCaseWithDBAndDoc(AsyncPouchDBTestCaseWithDB):
	"""Sets up a db named 'test', a document named 'mytest' and resets
	   the context afterwards.

	"""
	def setUp(self):
		super(AsyncPouchDBTestCaseWithDBAndDoc, self).setUp()

		def callback(err, resp):
			self.rev = resp["rev"]

		self._db.put({"_id": "mytest", "test": True}, callback)
		self.waitUntilCalled(callback)

class SyncPouchDBTestCaseWithDBAndAttachment(SyncPouchDBTestCaseWithDB):
	"""Sets up a db named 'test', and adds a document named
	   'attachment_test' with an attachment named 'text' inside.
	   Afterwards, it resets the context.

	"""
	def setUp(self):
		super(SyncPouchDBTestCaseWithDBAndAttachment, self).setUp()

		resp = self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain")
		self.rev = resp["rev"]

class AsyncPouchDBTestCaseWithDBAndAttachment(AsyncPouchDBTestCaseWithDB):
	"""Sets up a db named 'test', and adds a document named
	   'attachment_test' with an attachment named 'text' inside.
	   Afterwards, it resets the context.

	"""
	def setUp(self):
		super(AsyncPouchDBTestCaseWithDBAndAttachment, self).setUp()

		def cb(resp):
			self.rev = resp["rev"]

		self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain").then(cb)
		self.waitUntilCalled(cb)

class SyncDestroyTests(SyncPouchDBTestCaseWithDBAndDoc):
	def testInstanceDestroy(self):
		self.assertTrue(self._db.destroy()["ok"])
		db = self._env.PouchDB("test")
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			db.get("mytest")
		self.assertEqual(cm.exception["status"], 404)

	def testGlobalDestroy(self):
		self.assertIsNone(self._env.destroy("test"))
		db = self._env.PouchDB("test")
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			db.get("mytest")
		self.assertEqual(cm.exception["status"], 404)

	def testGlobalNoName(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._env.destroy()

class AsyncDestroyTests(AsyncPouchDBTestCaseWithDBAndDoc):
	def testInstanceDestroy(self):
		def callback(err, resp):
			self.assertFalse(err)

			db = self._env.PouchDB("test")
			def getCallback(err, resp):
				self.assertEqual(err["status"], 404)
			db.get("mytest", getCallback)
			self.waitUntilCalled(getCallback)

		self._db.destroy(callback)
		self.waitUntilCalled(callback)

	def testGlobalDestroy(self):
		def callback(err, resp):
			self.assertFalse(err)

			db = self._env.PouchDB("test")
			def getCallback(err, resp):
				self.assertEqual(err["status"], 404)
			db.get("mytest", getCallback)
			self.waitUntilCalled(getCallback)

		self._env.destroy("test", callback)
		self.waitUntilCalled(callback)

	def testGlobalDestroyWithNameOption(self):
		def getCallback(err, resp):
			self.assertEqual(err["status"], 404)

		def callback(err, resp):
			self.assertFalse(err)

			db = self._env.PouchDB("test")
			db.get("mytest", getCallback)

		self._env.destroy(callback, name="test")
		self.waitUntilCalled(getCallback)

class SyncPutTests(SyncPouchDBTestCaseWithDB):
	def testSimplePut(self):
		resp = self._db.put({"_id": "mytest", "test": True})
		self.assertEqual(resp["id"], "mytest")

class AsyncPutTests(AsyncPouchDBTestCaseWithDB):
	def testAsyncPut(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.put({"_id": "abcd", "something": 26}, callback)
		self.assertFalse(result)
		self.waitUntilCalled(callback)
		self.assertTrue(result["resp"]["ok"])

	def testPutProvidingId(self):
		def cb(err, resp):
			self.assertEqual(resp.id, "mytest")
		self._db.put({}, "mytest", cb)
		self.waitUntilCalled(cb)

class SyncPostTests(SyncPouchDBTestCaseWithDB):
	def testSimplePost(self):
		self.assertTrue(self._db.post({"test": False})["ok"])

class AsyncPostTests(AsyncPouchDBTestCaseWithDB):
	def testSimplePost(self):
		def callback(resp):
			assert resp["ok"]
		self._db.post({"test": False}).then(callback)
		self.waitUntilCalled(callback)

class SyncGetTests(SyncPouchDBTestCaseWithDBAndDoc):
	def testSimpleGet(self):
		doc = self._db.get("mytest")
		self.assertEqual(doc["_id"], "mytest")

	def testMissingDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.get("unexisting-doc")
		self.assertEqual(cm.exception["status"], 404)
		self.assertIn("404", str(cm.exception))

class AsyncGetTests(AsyncPouchDBTestCaseWithDBAndDoc):
	def testSimpleGet(self):
		def cb(doc):
			self.assertEqual(doc["_id"], "mytest")
		self._db.get("mytest").then(cb)
		self.waitUntilCalled(cb)

class SyncRemoveTests(SyncPouchDBTestCaseWithDBAndDoc):
	def testSimpleRemove(self):
		doc = self._db.get("mytest")
		self.assertTrue(self._db.remove(doc)["ok"])
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.get("mytest")
		self.assertEqual(cm.exception["status"], 404)

class AsyncRemoveTests(AsyncPouchDBTestCaseWithDBAndDoc):
	def testSimpleRemove(self):
		def removeCb(resp):
			self.assertTrue(resp["ok"])

		def getCb(doc):
			self._db.remove(doc).then(removeCb)

		self.assertPromise(self._db.get("mytest").then(getCb))
		self.waitUntilCalled(removeCb)

class SyncBulkDocsTests(SyncPouchDBTestCaseWithDB):
	def testSimpleBulkDocs(self):
		resp = self._db.bulkDocs(BULK_DOCS)
		self.assertEqual(len(resp), 2)

class AsyncBulkDocsTests(AsyncPouchDBTestCaseWithDB):
	def testSimpleBulkDocs(self):
		def cb(err, resp):
			self.assertEqual(len(resp), 2)

		self.assertPromise(self._db.bulkDocs(BULK_DOCS, cb))
		self.waitUntilCalled(cb)

class SyncAllDocsTests(SyncPouchDBTestCaseWithDB):
	def testAllDocsWithEmptyDB(self):
		resp = self._db.allDocs(include_docs=True)
		self.assertEqual(len(resp["rows"]), 0)

	def testAllDocsWithNonEmptyDB(self):
		self._db.post({})

		resp = self._db.allDocs(include_docs=True)
		self.assertEqual(len(resp["rows"]), 1)

class AsyncAllDocsTests(AsyncPouchDBTestCaseWithDB):
	def testAllDocsWithEmptyDB(self):
		def cb(err, resp):
			self.assertEqual(len(resp["rows"]), 0)

		self.assertPromise(self._db.allDocs(cb))
		self.waitUntilCalled(cb)

class SyncChangesTests(SyncPouchDBTestCaseWithDBAndDoc):
	def testSimple(self):
		self.assertEqual(len(self._db.changes()["results"][0]["changes"]), 1)

	def testLive(self):
		def cb(err, resp):
			self.assertEqual(resp["status"], "cancelled")
		promise = self._db.changes(live=True, complete=cb)
		self.assertIsNone(promise.cancel())
		self.waitUntilCalled(cb)

class AsyncChangesTests(AsyncPouchDBTestCaseWithDBAndDoc):
	def testAsync(self):
		data = {}
		def onComplete(err, resp):
			data["err"] = err
			data["resp"] = resp
		self.assertPromise(self._db.changes(complete=onComplete))
		self.waitUntilCalled(onComplete)
		self.assertIn("last_seq", data["resp"])

	def testLive(self):
		def cb(err, resp):
			self.assertEqual(resp["status"], "cancelled")
		promise = self._db.changes(live=True, complete=cb)
		self.assertIsNone(promise.cancel())
		self.waitUntilCalled(cb)

class SyncReplicateTests(SyncPouchDBTestCaseWithDBAndDoc):
	def testSimpleReplicate(self):
		resp = self._env.replicate("test", "testb")
		self.assertTrue(resp["ok"])

	def testLocalSync(self):
		resp = self._db.sync("b")
		self.assertTrue(resp["pull"]["ok"])
		self.assertTrue(resp["push"]["ok"])

	def testGlobalSync(self):
		resp = self._env.sync("test", "b")
		self.assertTrue(resp["pull"]["ok"])
		self.assertTrue(resp["push"]["ok"])

	def testSimpleReplicateTo(self):
		self.assertTrue(self._db.replicate_to("testb")["ok"])
		db = self._env.PouchDB("testb")
		#this should not throw a PouchDBError
		self.assertTrue(db.get("mytest")["test"])

	def testSimpleReplicateFrom(self):
		self.assertTrue(self._db.replicate_from("testb")["ok"])

	def testLive(self):
		resp = self._db.replicate_to("testb", live=True)
		self.assertIsNone(resp["cancel"]())

		resp2 = self._db.replicate_from("testb", live=True)
		self.assertIsNone(resp2["cancel"]())

		resp3 = self._env.replicate("test", "testb", live=True)
		self.assertIsNone(resp3["cancel"]())

class AsyncReplicateTests(AsyncPouchDBTestCaseWithDBAndDoc):
	def testReplicateWithOnComplete(self):
		result = {}
		def onComplete(err, resp):
			result["err"] = err
			result["resp"] = resp

		promise = self._env.replicate("test", "testb", complete=onComplete)
		self.assertFalse(promise["cancelled"])
		self.waitUntilCalled(onComplete)
		self.assertEqual(result["resp"]["docs_written"], 1)

	def testLocalSync(self):
		def cb(err, resp):
			self.assertTrue(resp["pull"]["ok"])
			self.assertTrue(resp["push"]["ok"])
		self._db.sync("b", cb, complete=cb)
		self.waitUntilCalled(cb)

	def testGlobalSync(self):
		def cb(err, resp):
			self.assertTrue(resp["pull"]["ok"])
			self.assertTrue(resp["push"]["ok"])
		self._env.sync("test", "b", complete=cb)
		self.waitUntilCalled(cb)

	def testLive(self):
		resp = self._db.replicate_to("testb", live=True)
		self.assertIsNone(resp["cancel"]())

		resp2 = self._db.replicate_from("testb", live=True)
		self.assertIsNone(resp2["cancel"]())

		resp3 = self._env.replicate("test", "testb", live=True)
		self.assertIsNone(resp3["cancel"]())

	def testReplicateFromWithCallback(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp

		self._db.replicate_from("testb", callback)
		self.waitUntilCalled(callback)
		self.assertEqual(result["resp"]["docs_written"], 0)

	def testReplicateToWithCallback(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp

		self._db.replicate_to("testb", callback)
		self.waitUntilCalled(callback)
		self.assertEqual(result["resp"]["docs_written"], 1)

class SyncPutAttachmentTests(SyncPouchDBTestCaseWithDB):
	def testSimplePutAttachment(self):
		resp = self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain")
		self.assertTrue(resp["ok"])

	def testPutTwoAttachmentsInSameDoc(self):
		resp = self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain")
		rev = resp["rev"]
		resp2 = self._db.putAttachment("attachment_test", "text2", u"éfgh".encode("UTF-8"), "text/plain", rev)
		self.assertTrue(resp2["ok"])

class AsyncPutAttachmentTests(AsyncPouchDBTestCaseWithDB):
	def testPutAttachmentAsync(self):
		result = {}
		def putAttachmentCallback(err, resp):
			result["err"] = err
			result["resp"] = resp

		self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain", callback=putAttachmentCallback)
		self.waitUntilCalled(putAttachmentCallback)
		self.assertTrue(result["resp"]["ok"])

class SyncGetAttachmentTests(SyncPouchDBTestCaseWithDBAndAttachment):
	def testSimpleGetAttachment(self):
		resp = self._db.getAttachment("attachment_test", "text")
		self.assertEqual(resp["data"], b"abcd")

	def testMissingDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.getAttachment("unexisting_doc", "text")
		self.assertEqual(cm.exception["status"], 404)

	def testMissingAttachment(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.getAttachment("attachment_test", "unexisting_attachment")
		self.assertEqual(cm.exception["status"], 404)

class AsyncGetAttachmentTests(AsyncPouchDBTestCaseWithDBAndAttachment):
	def testGetAttachmentAsync(self):
		result = {}
		def callback(err, resp=None):
			result["err"] = err
			result["resp"] = resp
		self._db.getAttachment("attachment_test", "text", callback)
		self.waitUntilCalled(callback)
		self.assertEqual(result["resp"]["data"], b"abcd")

	def testMissingAttachmentAsync(self):
		result = {}
		def callback(err, resp=None):
			result["err"] = err
			result["resp"] = resp
		self._db.getAttachment("attachment_test", "unexisting_attachment", callback)
		self.waitUntilCalled(callback)
		self.assertEqual(result["err"]["status"], 404)

class SyncRemoveAttachmentTests(SyncPouchDBTestCaseWithDBAndAttachment):
	def testSimpleRemoveAttachment(self):
		resp = self._db.removeAttachment("attachment_test", "text", self.rev)
		self.assertTrue(resp["ok"])

	@unittest.skip("While this might be the expected API, it's not the one PouchDB uses.")
	def testRemoveUnexistingAttachment(self): #pragma: no cover
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.removeAttachment("attachment_test", "unexisting-attachment", self.rev)
		self.assertEqual(cm.exception["status"], 404)

	def testRemoveAttachmentFromUnexistingDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.removeAttachment("unexisting-doc", "text", self.rev)
		self.assertEqual(cm.exception["status"], 404)

class AsyncRemoveAttachmentTests(AsyncPouchDBTestCaseWithDBAndAttachment):
	def testRemoveAttachmentAsync(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.removeAttachment("attachment_test", "text", self.rev, callback)
		self.waitUntilCalled(callback)
		self.assertTrue(result["resp"]["ok"])

	@unittest.skip("While this might be the expected API, it's not the one PouchDB uses.")
	def testRemoveUnexistingAttachmentAsync(self): #pragma: no cover
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.removeAttachment("attachment_test", "unexisting-attachment", self.rev, callback)
		self.waitUntilCalled(callback)
		self.assertTrue(result["err"]["status"], 404)

	def testRemoveAttachmentFromUnexistingDocAsync(self):
		result = {}
		def callback(err, resp=None):
			result["err"] = err
			result["resp"] = resp
		self._db.removeAttachment("unexisting-doc", "text", self.rev, callback)
		self.waitUntilCalled(callback)
		self.assertTrue(result["err"]["status"], 404)

class SyncQueryTests(SyncPouchDBTestCaseWithDB):
	def testQueryWithEmptyDB(self):
		resp = self._db.query(QUERY_FUNC)
		self.assertEqual(len(resp["rows"]), 0)

	def testAllDocsWithNonEmptyDB(self):
		self._db.post({})

		resp = self._db.query(QUERY_FUNC)
		self.assertEqual(len(resp["rows"]), 1)

class AsyncQueryTests(AsyncPouchDBTestCaseWithDB):
	def testQueryWithEmptyDB(self):
		def cb(resp):
			self.assertEqual(len(resp["rows"]), 0)
		self._db.query(QUERY_FUNC).then(cb)
		self.waitUntilCalled(cb)

class InfoVerifierMixin(object):
	def verifyInfo(self, info):
		self.assertIn("update_seq", info)
		self.assertEqual(info["db_name"], "test")

class SyncInfoTests(SyncPouchDBTestCaseWithDB, InfoVerifierMixin):
	def testSimpleInfo(self):
		info = self._db.info()
		self.verifyInfo(info)

class AsyncInfoTests(AsyncPouchDBTestCaseWithDB, InfoVerifierMixin):
	def testInfoAsync(self):
		data = {}
		def callback(err, resp):
			data["err"] = err
			data["resp"] = resp
		self._db.info(callback)
		self.waitUntilCalled(callback)

		self.assertIsNone(data["err"])
		self.verifyInfo(data["resp"])

class SyncCompactTests(SyncPouchDBTestCaseWithDB):
	def testCompactOnEmptyDB(self):
		self.assertIsNone(self._db.compact())

	def testCompactOnNonEmptyDB(self):
		self._db.post({})
		self.assertIsNone(self._db.compact())

class AsyncCompactTests(AsyncPouchDBTestCaseWithDB):
	def testCompactOnEmptyDB(self):
		self.assertPromise(self._db.compact())

class SyncRevsDiffTests(SyncPouchDBTestCaseWithDB):
	def testSimpleRevsDiff(self):
		resp = self._db.revsDiff(REVS_DIFF_DATA)
		#the doc isn't in the db
		self.assertEqual(len(resp["myDoc1"]["missing"]), 2)

class AsyncRevsDiffTests(AsyncPouchDBTestCaseWithDB):
	def testSimpleRevsDiff(self):
		def cb(err, resp):
			#the doc isn't in the db
			self.assertEqual(len(resp["myDoc1"]["missing"]), 2)
		self._db.revsDiff(REVS_DIFF_DATA, cb)
		self.waitUntilCalled(cb)

class EventTests(SyncPouchDBTestCase):
	"""The sync and async implementains are the same (as in, implemented
	   in the base class), so there are no async tests.

	"""
	def testPouchCreatedEvent(self):
		#setup
		resp = {}
		def onCreate(dbName):
			resp["created"] = dbName
		self._env.on("created", onCreate)

		#test created
		self._env.PouchDB("abc")
		if not "created" in resp: #pragma: no cover
			self.waitUntilCalled(onCreate)
		self.assertEqual(resp["created"], "abc")

	def testPouchDestroyedEvent(self):
		#setup
		resp = {}
		def onDestroy(dbName):
			resp["destroyed"] = dbName
		self._env.addListener("destroyed", onDestroy)

		#test destroyed
		self._env.destroy("test")
		if not "destroyed" in resp: #pragma: no cover
			self.waitUntilCalled(onDestroy)
		self.assertEqual(resp["destroyed"], "test")

	def testOnceAndEmit(self):
		data = {"count": 0}
		def cb(i=1):
			data["count"] += i
		self._env.once("test", cb)
		self.assertEqual(data["count"], 0)

		self.assertTrue(self._env.emit("test", 2))
		self.waitUntilCalled(cb)
		self.assertEqual(data["count"], 2)

		self.assertFalse(self._env.emit("test"))
		self.assertEqual(data["count"], 2)

	def testListeners(self):
		#setup
		resp = {"called": False}
		def cb1():
			pass
		def cb2():
			resp["called"] = True
		self._env.on("test", cb1).on("test", cb2)

		listeners = self._env.listeners("test")
		self.assertEqual(len(listeners), 2)
		self.assertFalse(resp["called"])
		for listener in listeners:
			self.assertIsNone(listener())
			self.waitUntilCalled([cb1, cb2])
		self.assertTrue(resp["called"])

	def testSetMaxListeners(self):
		def cb():
			pass #pragma: no cover
		self._env.setMaxListeners(1)
		self._env.on("test", cb)
		with self.assertRaises(self._env.context.JSError) as cm:
			self._env.on("test", cb)
		self.assertIn("possible EventEmitter memory leak detected.", str(cm.exception))

	def testRemoveListener(self):
		called = {"cb1": False, "cb2": False}
		def cb1():
			called["cb1"] = True #pragma: no cover
		def cb2():
			called["cb2"] = True
		self._env.on("test", cb1)
		self._env.on("test", cb2)
		self._env.removeListener("test", cb1)
		self._env.emit("test")
		self.waitUntilCalled(cb2)
		self.assertFalse(called["cb1"])
		self.assertTrue(called["cb2"])

	def testRemoveAllListenersWithArg(self):
		called = {"cb1": False, "cb2": False, "cb3": False}
		def cb1():
			called["cb1"] = True #pragma: no cover
		def cb2():
			called["cb2"] = True #pragma: no cover
		def cb3():
			called["cb3"] = True

		self._env.on("test", cb1)
		self._env.on("test", cb2)
		self._env.on("myTest", cb3)

		self._env.removeAllListeners("test")
		self._env.emit("test")
		self._env.emit("myTest")
		self.waitUntilCalled(cb3)

		self.assertFalse(called["cb1"])
		self.assertFalse(called["cb2"])
		self.assertTrue(called["cb3"])

	def testRemoveAllListenersWithoutArg(self):
		called = {"cb1": False, "cb2": False, "cb3": False}
		def cb1():
			called["cb1"] = True #pragma: no cover
		def cb2():
			called["cb2"] = True #pragma: no cover
		def cb3():
			called["cb3"] = True #pragma: no cover
		self._env.on("test", cb1)
		self._env.on("test", cb2)
		self._env.on("myTest", cb3)

		self._env.removeAllListeners()
		self._env.emit("test")
		self._env.emit("myTest")

		self.assertFalse(called["cb1"])
		self.assertFalse(called["cb2"])
		self.assertFalse(called["cb3"])

@unittest.skipIf(FAST_ONLY, "Too slow.")
class HttpTests(SyncPouchDBTestCase):
	def setUp(self):
		super(HttpTests, self).setUp()

		self._db = self._env.PouchDB(BASE_URL + "/test", auth=HTTP_AUTH)

	def testSomeSimpleMethods(self):
		id = self._db.post({"test": True})["id"]
		self.assertTrue(self._db.get(id)["test"])
		self.assertIn(id, str(self._db.allDocs()))

		self.assertIn("db_name", self._db.info())

	def testAttachment(self):
		#Suppress a ResourceWarning requests throws in Python 3.
		warnings.filterwarnings("ignore", message="unclosed")

		rev = self._db.putAttachment("attachment-doc", "attachment", b"<h1>Hello World!</h1>", "text/html")["rev"]

		resp = requests.get(BASE_URL + "/test/attachment-doc/attachment")
		self.assertEqual(resp.content, b"<h1>Hello World!</h1>")
		self.assertEqual(resp.headers["Content-Type"], "text/html")

		a = self._db.getAttachment("attachment-doc", "attachment")
		self.assertEqual(a["data"], b"<h1>Hello World!</h1>")
		self.assertEqual(a["type"], "text/html")

		self._db.removeAttachment("attachment-doc", "attachment", rev)

	def testReplication(self):
		rev = self._db.put({"_id": "mytest"})["rev"]
		self._db.replicate_to("local")

		localDb = self._env.PouchDB("local")
		self.assertEqual(localDb.get("mytest")["_rev"], rev)

	def tearDown(self):
		self._env.PouchDB(BASE_URL + "/test", auth=HTTP_AUTH).destroy()

class EnvironmentTests(SyncPouchDBTestCase):
	def testVersion(self):
		self.assertTrue(self._env.POUCHDB_VERSION)

	def testSecondEnvironmentDifferentDir(self):
		with self.assertRaises(pouchdb.EnvironmentError) as cm:
			pouchdb.setup(storageDir=os.path.join(STORAGE_DIR, "a"))

		#should complain about this property
		self.assertIn("storageDir", str(cm.exception))
		self.assertIn(STORAGE_DIR, str(cm.exception))

class ContextTestsWithDb(SyncPouchDBTestCaseWithDB):
	def testDbSizeOfExistingsDB(self):
		size = self._env.context.getDbSize("test")
		self.assertIsInstance(size, numbers.Integral)
		self.assertGreater(size, 0)

	def testDbSizeOfUnexisting(self):
		with self.assertRaises(KeyError):
			self._env.context.getDbSize("unexisting_database")

class ContextTests(SyncPouchDBTestCase):
	@unittest.skipIf(FAST_ONLY, "Too slow.")
	def testInspect(self):
		self._env.context.inspect(block=False)

	def testAttributeError(self):
		with self.assertRaises(AttributeError):
			self._env.context._evalJs("return {}").a

	def testException(self):
		with self.assertRaises(Exception) as cm:
			self._env.context._evalJs("throw new Error('Hello World!')");
		self.assertIn("Hello World!", str(cm.exception))

class SyncGQLTests(SyncPouchDBTestCaseWithDBAndDoc):
	def testSelectWhereGql(self):
		resp = self._db.gql({"select": "*", "where": "test=true"})
		self.assertEqual(len(resp["rows"]), 1)

	def testInvalidQueryFormat(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.gql("invalid")
		self.assertEqual(cm.exception["status"], 400)

class AsyncGQLTests(AsyncPouchDBTestCaseWithDBAndDoc):
	def testSelectWhereGql(self):
		def cb(err, resp):
			self.assertEqual(len(resp["rows"]), 1)
		self._db.gql({"select": "*", "where": "test=true"}, cb)
		self.waitUntilCalled(cb)

class SpatialTestsMixin(object):
	_designDoc = {
		'_id': '_design/foo',
		'spatial': {
			'test': 'function(doc) {if (doc.key) {emit(doc.key, doc); }}',
		},
	}
	_docs = [
		_designDoc,
		{'foo': 'bar', 'key': [1]},
		{'_id': 'volatile', 'foo': 'baz', 'key': [2]},
	]

class SyncSpatialTests(SyncPouchDBTestCaseWithDB, SpatialTestsMixin):
	def testSpatial(self):
		"""Based on the first test in the geopouch test suite.

		"""
		self._db.bulkDocs({"docs": self._docs})
		doc = self._db.get("volatile")
		self._db.remove(doc)

		resp = self._db.spatial('foo/test', start_range=[None], end_range=[None])
		self.assertEqual(len(resp["rows"]), 1, msg='Dont include deleted documents')
		for row in resp["rows"]:
			self.assertIn("key", row, msg='view row has a key')
			self.assertIn("_rev", row["value"], msg='emitted doc has rev')
			self.assertIn("_id", row["value"], msg='emitted doc has id')

class AsyncSpatialTests(AsyncPouchDBTestCaseWithDB, SpatialTestsMixin):
	def testSpatial(self):
		"""Based on the first test in the geopouch test suite.

		"""
		def spatialCb(err, resp):
			self.assertIsNone(err)
			self.assertEqual(len(resp["rows"]), 1, msg='Dont include deleted documents')
			for row in resp["rows"]:
				self.assertIn("key", row, msg='view row has a key')
				self.assertIn("_rev", row["value"], msg='emitted doc has rev')
				self.assertIn("_id", row["value"], msg='emitted doc has id')

		def removeCb(resp):
			self._db.spatial('foo/test', spatialCb, start_range=[None], end_range=[None])

		def getCb(doc):
			self._db.remove(doc).then(removeCb)

		def bulkDocsCb(resp):
			self._db.get("volatile").then(getCb)

		self._db.bulkDocs({"docs": self._docs}).then(bulkDocsCb)
		self.waitUntilCalled(spatialCb)

class SearchTestsMixin(object):
	#based on the pouchdb-search test suite
	_doc1 = {
		"_id": "c240s1",
		"chapter": "240",
		"title": "III",
		"href": "/Laws/GeneralLaws/PartIII/TitleIII/Chapter240/Section1",
		"text": "If the record title of land is clouded by an adverse claim, or by the possibility thereof, a person in possession of such land claiming an estate of freehold therein or an unexpired term of not less than ten years, and a person who by force of the covenants in a deed or otherwise may be liable in damages, if such claim should be sustained, may file a petition in the land court stating his interest, describing the land, the claims and the possible adverse claimants so far as known to him, and praying that such claimants may be summoned to show cause why they should not bring an action to try such claim. If no better description can be given, they may be described generally, as the heirs of A B or the like. Two or more persons having separate and distinct parcels of land in the same county and holding under the same source of title, or persons having separate and distinct interests in the same parcel or parcels, may join in a petition against the same supposed claimants. If the supposed claimants are residents of the commonwealth, the petition may be inserted like a declaration in a writ, and served by a copy, like a writ of original summons. Whoever is in the enjoyment of an easement shall be held to be in possession of land within the meaning of this section",
		"section": "1",
		"part": "III",
		"type": "general",
		"desc": "Petition to compel adverse claimant to try title",
	}
	_doc2 = {
		"_id": "c240s10",
		"chapter": "240",
		"title": "III",
		"href": "/Laws/GeneralLaws/PartIII/TitleIII/Chapter240/Section10",
		"text": "After all the defendants have been served with process or notified as provided in section seven and after the appointment of a guardian ad litem or next friend, if such appointment has been made, the court may proceed as though all defendants had been actually served with process. Such action shall be a proceeding in rem against the land, and a judgment establishing or declaring the validity, nature or extent of the plaintiff’s title may be entered, and shall operate directly on the land and have the force of a release made by or on behalf of all defendants of all claims inconsistent with the title established or declared thereby. This and the four preceding sections shall not prevent the court from also exercising jurisdiction in personam against defendants actually served with process who are personally amenable to its judgments",
		"section": "10",
		"part": "III",
		"type": "general",
		"desc": "Proceeding in rem; effect of judgment",
	}
	_doc3 = {
		"_id": "c240s10A",
		"chapter": "240",
		"title": "III",
		"href": "/Laws/GeneralLaws/PartIII/TitleIII/Chapter240/Section10A",
		"text": "The superior court and the land court shall have concurrent jurisdiction of a civil action by any person or persons claiming an estate of freehold, or an unexpired term of not less than ten years, in land subject to a restriction described in section twenty-six of chapter one hundred and eighty-four, to determine and declare whether and in what manner and to what extent and for the benefit of what land the restriction is then enforceable, whether or not a violation has occurred or is threatened. The complaint shall state the names and addresses, so far as known to the plaintiff or plaintiffs, of the owners of the subject parcels as to which the determination is sought, of the owners of any benefited land and of any persons benefited other than persons interested in benefited land. There shall be filed therewith (1) a certified copy of the instrument or instruments imposing the restriction, or of a representative instrument if there are many and the complaint includes a summary of the remainder, and (2) a plan or sketch showing the approximate locations of the parcels as to which the determination is sought, and the other parcel or parcels, if any, which may have the benefit of the restriction, and the ways, public or open to public use, upon which the respective parcels abut or nearest thereto, and the street numbers, if any, of such parcels",
		"section": "10A",
		"part": "III",
		"type": "general",
		"desc": "Restrictions on land; determination; jurisdiction; petition",
	}
	_doc4 = {
		"_id": "_design/find",
		"indexes": {
			"things": {
				"index": """function(doc) {
					if (doc.text) {
						index('default', doc.text);
					}
					if (doc.desc) {
						index('title', doc.desc);
					}
				}""",
			},
		},
	}

	_docs = [_doc1, _doc2, _doc3, _doc4]

class SyncSearchTests(SyncPouchDBTestCaseWithDB, SearchTestsMixin):
	def setUp(self):
		super(SyncSearchTests, self).setUp()

		self._db.bulkDocs({"docs": self._docs})

	def testBasic(self):
		result = self._db.search("find/things", q="freehold")
		self.assertEqual(len(result.rows), 2)
		ids = [v.id for v in result.rows]
		self.assertEqual(ids, ["c240s10A", "c240s1"])

class AsyncSearchTests(AsyncPouchDBTestCaseWithDB, SearchTestsMixin):
	def setUp(self):
		super(AsyncSearchTests, self).setUp()

		def cb(*args):
			pass

		self._db.bulkDocs({"docs": self._docs}, cb)
		self.waitUntilCalled(cb)

	def testBasic(self):
		def searchCb(err, result):
			self.assertIsNone(err)
			self.assertEqual(len(result.rows), 2)
			ids = [v.id for v in result.rows]
			self.assertEqual(ids, ["c240s10A", "c240s1"])

		self._db.search("find/things", searchCb, q="freehold")
		self.waitUntilCalled(searchCb)

class AuthenticationMixin(object):
	_username = "python_pouchdb_test"
	_password = "thePassword"
	_metadata = {"updated": "02-02-2002"}

@unittest.skipIf(FAST_ONLY, "Too slow.")
class SyncAuthenticationTests(SyncPouchDBTestCase, AuthenticationMixin):
	def setUp(self):
		super(SyncAuthenticationTests, self).setUp()

		self._db = self._env.PouchDB(BASE_URL + "/test", auth=HTTP_AUTH)

	def tearDown(self):
		self._db.destroy()

	def testAuth(self):
		#sign up
		signupResp = self._db.signup(self._username, self._password, metadata=self._metadata)
		self.assertTrue(signupResp["ok"])

		try:
			#log in
			loginResp = self._db.login(self._username, self._password)
			self.assertEqual(loginResp["name"], self._username)

			#login info
			session = self._db.getSession()
			self.assertEqual(session["userCtx"]["name"], self._username)
			user = self._db.getUser(self._username)
			self.assertEqual(user["updated"], self._metadata["updated"])

			#logout
			logoutResp = self._db.logout()
			self.assertTrue(logoutResp["ok"])
		finally:
			userDb = self._env.PouchDB(BASE_URL + "/_users", auth=HTTP_AUTH)
			teardownReq = userDb.remove({
				"_id": signupResp.id,
				"_rev": signupResp.rev
			})
			self.assertTrue(teardownReq["ok"])

	def testAliases(self):
		#sign up
		signupResp = self._db.signUp(self._username, self._password, metadata=self._metadata)
		self.assertTrue(signupResp["ok"])

		try:
			#log in
			loginResp = self._db.logIn(self._username, self._password)
			self.assertEqual(loginResp["name"], self._username)

			#login info - basic test only
			session = self._db.getSession()
			self.assertEqual(session["userCtx"]["name"], self._username)

			#logout
			logoutResp = self._db.logOut()
			self.assertTrue(logoutResp["ok"])
		finally:
			userDb = self._env.PouchDB(BASE_URL + "/_users", auth=HTTP_AUTH)
			teardownReq = userDb.remove({
				"_id": signupResp.id,
				"_rev": signupResp.rev
			})
			self.assertTrue(teardownReq["ok"])

@unittest.skipIf(FAST_ONLY, "Too slow.")
class AsyncAuthenticationTests(AsyncPouchDBTestCase, AuthenticationMixin):
	def setUp(self):
		super(AsyncAuthenticationTests, self).setUp()

		self._db = self._env.PouchDB(BASE_URL + "/test", auth=HTTP_AUTH)

	def tearDown(self):
		def cb(*args):
			pass
		self._db.destroy()

		if self._signupResp: #pragma: no branch
			userDb = self._env.PouchDB(BASE_URL + "/_users", auth=HTTP_AUTH)
			userDb.remove({
				"_id": self._signupResp.id,
				"_rev": self._signupResp.rev
			}, cb)
			self.waitUntilCalled(cb)

	def testAuth(self):	
		"""Handles the actual test."""

		self._signupResp = None

		self._db.signup(self._username, self._password, metadata=self._metadata, callback=self.onSignUp)
		self.waitUntilCalled(self.onLogOut)

	def onSignUp(self, err, resp):
		#for tearDown use
		self._signupResp = resp

		self.assertTrue(resp["ok"])
		self._db.login(self._username, self._password, self.onLogIn)

	def onLogIn(self, err, resp):
		self.assertEqual(resp["name"], self._username)

		self._db.getSession(self.onGetSession)

	def onGetSession(self, err, resp):
		self.assertEqual(resp["userCtx"]["name"], self._username)
		self._db.getUser(self._username, self.onGetUser)

	def onGetUser(self, err, resp):
		self.assertEqual(resp["updated"], self._metadata["updated"])

		logoutResp = self._db.logout(self.onLogOut)

	def onLogOut(self, err, resp):
		self.assertTrue(resp["ok"])

class SyncValidationSuccessTests(SyncPouchDBTestCaseWithDB):
	"""Where the other tests just check if the wrappers work and are 
	   barely checking behaviour, the validation tests do more. That is
	   because the other things have JS test suites, and the validation
	   plugin doesn't.

	"""

	def setUp(self):
		super(SyncValidationSuccessTests, self).setUp()

		self._db.put(ONLY_TEST_VALIDATION_DOC)

	def testSuccessfulPut(self):
		doc = self._db.validatingPut({"_id": "test"})
		self.assertTrue(doc["ok"])

	def testSuccessfulPost(self):
		doc = self._db.validatingPost({"_id": "test"})
		self.assertTrue(doc["ok"])

	def testSuccessfulRemove(self):
		info = self._db.put({"_id": "test"})
		rmInfo = self._db.validatingRemove({
			"_id": "test",
			"_rev": info["rev"],
		})
		self.assertTrue(rmInfo.ok)

	def testSuccessfulBulkDocs(self):
		resp = self._db.validatingBulkDocs({
			"docs": [
				{
					"_id": "test",
				},
			],
		})
		self.assertTrue(resp[0].ok)

class AsyncValidationTests(AsyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(AsyncValidationTests, self).setUp()

		def cb(resp):
			pass
		self._db.put(ONLY_TEST_VALIDATION_DOC).then(cb)
		self.waitUntilCalled(cb)

	def testSuccessfulPut(self):
		def cb(err, doc):
			self.assertTrue(doc["ok"])
		self._db.validatingPut({"_id": "test"}, cb)
		self.waitUntilCalled(cb)

	def testSuccessfulPost(self):
		def cb(err, doc):
			self.assertTrue(doc.ok)
		self._db.validatingPost({"_id": "test"}, cb)
		self.waitUntilCalled(cb)

	def testSuccessfulRemove(self):
		def removeCb(err, info):
			self.assertTrue(info["ok"])
		def putCb(info):
			self._db.validatingRemove({
				"_id": "test",
				"_rev": info["rev"],
			}, removeCb)
		info = self._db.put({"_id": "test"}).then(putCb)
		self.waitUntilCalled(removeCb)

	def testSuccessfulBulkDocs(self):
		def cb(err, resp):
			self.assertTrue(resp[0].ok)
		self._db.validatingBulkDocs({
			"docs": [
				{
					"_id": "test",
				},
			],
		}, cb)
		self.waitUntilCalled(cb)

	def testSuccessfulPutAttachment(self):
		def getCb(resp):
			self.assertEqual(resp["data"], b"Hello world!")
		def putCb(err, resp):
			self.assertTrue(resp.ok)
			self._db.getAttachment("test", "test").then(getCb)

		self._db.validatingPutAttachment("test", "test", b"Hello world!", "text/plain", putCb)
		self.waitUntilCalled(getCb)

	def testFailingRemoveAttachment(self):
		def removeCb(err, resp):
			self.assertEqual(err["status"], 403)
			self.assertEqual(err.error, "forbidden")

		#setup - put an attachment
		def putCb(resp):
			#start of the test
			self._db.validatingRemoveAttachment("mytest", "test", resp.rev, removeCb)
		self._db.putAttachment("mytest", "test", b"Hello world!", "text/plain").then(putCb)
		self.waitUntilCalled(removeCb)

class SyncValidationUnauthorizedTests(SyncPouchDBTestCaseWithDBAndDoc):
	"""See the note at the :class:`ValidationSuccessTests` class"""

	def setUp(self):
		super(SyncValidationUnauthorizedTests, self).setUp()

		self._db.put({
			"_id": "_design/test",
			"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
				if (newDoc._id !== "test") {
					throw({unauthorized: "only a document named 'test' is allowed."});
				}
			}""",
		})

	def _checkException(self, exc):
		self.assertEqual(exc["error"], "unauthorized")
		self.assertEqual(exc["reason"], "only a document named 'test' is allowed.")

	def testInvalidPut(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPut({"_id": "test_invalid"})
		self._checkException(cm.exception)

	def testInvalidPost(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPost({})
		self._checkException(cm.exception)

	def testInvalidRemove(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingRemove({
				"_id": "mytest",
				"_rev": self.rev,
			})
		self._checkException(cm.exception)

	def testInvalidBulkDocs(self):
		resp = self._db.validatingBulkDocs({
				"docs": [
					{
						"_id": "test_invalid",
					},
				],
			})
		self._checkException(resp[0])

class SyncValidationForbiddenTests(SyncPouchDBTestCaseWithDBAndDoc):
	"""See the note at the :class:`ValidationSuccessTests` class"""

	def setUp(self):
		super(SyncValidationForbiddenTests, self).setUp()

		self._db.put(ONLY_TEST_VALIDATION_DOC)

	def _checkException(self, exc):
		self.assertEqual(exc["error"], "forbidden")
		self.assertEqual(exc["reason"], "only a document named 'test' is allowed.")

	def testInvalidPut(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPut({"_id": "test_invalid"})
		self._checkException(cm.exception)

	def testInvalidPost(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPost({})
		self._checkException(cm.exception)

	def testInvalidRemove(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingRemove({
				"_id": "mytest",
				"_rev": self.rev,
			})
		self._checkException(cm.exception)

	def testInvalidBulkDocs(self):
		resp = self._db.validatingBulkDocs({
			"docs": [
				{
					"_id": "test_invalid",
				},
			],
		})
		self._checkException(resp[0])

	def testDesignDoc(self):
		"""A design doc is always valid, so no matter the
		   validate_doc_update function, the stuff below should succeed.

		"""
		self._db.validatingPut({
			"_id": "_design/mytest",
		})

class SyncValidationCompilationErrorTests(SyncPouchDBTestCaseWithDB):
	"""See the note at the :class:`ValidationSuccessTests` class"""

	def _checkException(self, e):
		self.assertEqual(e["error"], "compilation_error")
		self.assertIn("Expression does not eval to a function.", e["reason"])

	def testSyntaxError(self):
		self._db.put({
			"_id": "_design/test",
			"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
				return;
			}324j3lkl;""",
		})

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			doc = self._db.validatingPut({"_id": "test"})
		self._checkException(cm.exception)

	def testNonFunctionError(self):
		self._db.put({
			"_id": "_design/test",
			"validate_doc_update": "'a string instead of a function'",
		})
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			doc = self._db.validatingPut({"_id": "test"})
		self._checkException(cm.exception)

class SyncValidationExceptionTests(SyncPouchDBTestCaseWithDBAndDoc):
	"""See the note at the :class:`ValidationSuccessTests` class"""

	def setUp(self):
		super(SyncValidationExceptionTests, self).setUp()

		self._db.put({
			"_id": "_design/test",
			"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
				//reference error
				test;
			}""",
		})

	def testPut(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPut({"_id": "test"})

		self.assertEqual(cm.exception["error"], "ReferenceError")
		#'test' is the name of the missing variable.
		self.assertIn("test", cm.exception["reason"])

class SyncValidationAttachmentTests(SyncPouchDBTestCaseWithDBAndAttachment):
	def setUp(self):
		super(SyncValidationAttachmentTests, self).setUp()

		self.forbiddenDesignDoc = {
			"_id": "_design/test",
			"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
				throw({forbidden: JSON.stringify(newDoc)});
			}"""
		}

	def testRemoveAttachmentSuccess(self):
		self._db.validatingRemoveAttachment("attachment_test", "text", self.rev)

	def testRemoveAttachmentWhenForbidden(self):
		self._db.put(self.forbiddenDesignDoc)
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingRemoveAttachment("attachment_test", "text", self.rev)
		self.assertEqual(cm.exception["error"], "forbidden")
		#checks if the newDoc argument is filled in correctly
		self.assertIn('"_attachments":{}', cm.exception["reason"])

	def testPutAttachmentSuccess(self):
		self._db.validatingPutAttachment("attachment_test2", "text", u"tést".encode("UTF-8"), "text/plain")

	def testPutAttachmentWhenForbidden(self):
		self._db.put(self.forbiddenDesignDoc)
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPutAttachment("attachment_test2", "text", u"tést".encode("UTF-8"), "text/plain")
		self.assertEqual(cm.exception["error"], "forbidden")
		#checks if the newDoc argument is filled in correctly
		self.assertIn("text/plain", cm.exception["reason"])

class SyncValidationArgsTests(SyncPouchDBTestCaseWithDBAndDoc):
	def setUp(self):
		super(SyncValidationArgsTests, self).setUp()

		self._db.put({
			"_id": "_design/test",
			"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
				throw({forbidden: JSON.stringify([newDoc, oldDoc, userCtx, secObj])});
			}"""
		})

	def testArgsWithNewDoc(self):
		doc = {
			"_id": "test",
		}
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPut(doc)
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["reason"])
		self.assertEqual(newDoc, doc)
		self.assertIsNone(oldDoc)

		self.assertEqual(userCtx, {
			"db": "test",
			"name": None,
			"roles": ["_admin"]
		})
		self.assertEqual(secObj, {
			"admins": {
				"names": [],
				"roles": [],
			},
			"members": {
				"names": [],
				"roles": [],
			},
		})

	def testArgsWithExistingDoc(self):
		doc = {"_id": "mytest", "_rev": self.rev}
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPut(doc)
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["reason"])
		self.assertTrue(oldDoc["test"])

	def testChangingUserCtx(self):
		theUserCtx = {
			"db": "test",
			"name": "pypouchtest",
			"roles": ["the_boss"]
		}

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPost({}, userCtx=theUserCtx)
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["reason"])

		self.assertEqual(userCtx, theUserCtx)

	def testChangingSecObj(self):
		theSecObj = {
			"admins": {
				"names": ["the_boss"],
				"roles": [],
			},
			"members": {
				"names": [],
				"roles": [],
			},
		}

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPost({}, secObj=theSecObj)
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["reason"])

		self.assertEqual(secObj, theSecObj)

class SyncShowTests(SyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(SyncShowTests, self).setUp()

		self._db.put(SHOW_DOCUMENT)

	def testShowWithoutDoc(self):
		result = self._db.show("test/myshow")
		self.assertEqual(result["code"], 200)
		self.assertEqual(result["headers"]["Content-Type"], "text/html; charset=utf-8")
		self.assertEqual(result["headers"]["Vary"], "Accept")
		self.assertEqual(result["body"], "no doc")

	def testShowWithDoc(self):
		self._db.post({"_id": "mytest", "description": "Hello World!"})
		result = self._db.show("test/myshow/mytest")
		self.assertEqual(result["body"], "Hello World!")

	def testOverwriteArgs(self):
		resp = self._db.show("test/args", reqObjStub={"method": "POST"})
		doc, req = json.loads(resp.body)
		self.assertEqual(req["method"], "POST")

	def testOverwriteHeader(self):
		resp = self._db.show("test/args", reqObjStub={"headers": {"Host": "example.com"}})
		doc, req = json.loads(resp.body)
		#check if the header update was succesful.
		self.assertEqual(req["headers"]["Host"], "example.com")
		#check if other headers (test subject is Accept) are still set.
		self.assertEqual(req["headers"]["Accept"], "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

	def testShowArgs(self):
		doc, req = json.loads(self._db.show("test/args").body)

		#test doc - well, the unavailability of it...
		self.assertIsNone(doc)

		#test request object
		self.assertEqual(req["body"], "undefined")
		self.assertEqual(req["cookie"], {})
		self.assertEqual(req["form"], {})

		self.assertEqual(req["headers"]["Host"], "localhost:5984")
		self.assertEqual(req["headers"]["Accept"], "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		self.assertIn("en", req["headers"]["Accept-Language"])
		self.assertIn("en-us", req["headers"]["Accept-Language"])
		self.assertIn("Mozilla", req["headers"]["User-Agent"])
		self.assertIn("AppleWebKit", req["headers"]["User-Agent"])
		self.assertIn("KHTML", req["headers"]["User-Agent"])
		self.assertIn("Gecko", req["headers"]["User-Agent"])

		self.assertIsNone(req["id"])
		self.assertEqual(req["info"]["db_name"], "test")
		self.assertIn("update_seq", req["info"])
		self.assertEqual(req["method"], "GET")
		self.assertEqual(req["path"], ["test", "_design", "test", "_show", "args"])
		self.assertEqual(req["peer"], "127.0.0.1")
		self.assertEqual(req["query"], {})
		self.assertEqual(req["raw_path"], "/test/_design/test/_show/args")
		self.assertEqual(req["requested_path"], ["test", "_design", "test", "_show", "args"])
		self.assertEqual(req["secObj"], {
			"admins": {
				"names": [],
				"roles": [],
			},
			"members": {
				"names": [],
				"roles": [],
			},
		})
		self.assertEqual(req["userCtx"], {
			"db": "test",
			"name": None,
			"roles": [
				"_admin",
			],
		})
		self.assertUuid(req["uuid"])

	def testUnexistingDoc(self):
		doc, req = json.loads(self._db.show("test/args/abc").body)
		self.assertIsNone(doc)
		self.assertEqual(req["id"], "abc")
		self.assertIn("abc", req["path"])

	def testWithDesignDocAsArg(self):
		doc, req = json.loads(self._db.show("test/args/_design/test").body)
		self.assertEqual(req["id"], "_design/test")
		self.assertEqual(req["raw_path"], "/test/_design/test/_show/args/_design/test")
		self.assertIn("shows", doc)

	def testWithFakeDesignDocAsArg(self):
		doc, req = json.loads(self._db.show("test/args/_design").body)
		self.assertIsNone(doc)
		self.assertEqual(req["id"], "_design")
		self.assertEqual(req["raw_path"], "/test/_design/test/_show/args/_design")

	def testSettingQuery(self):
		resp = self._db.show("test/args", reqObjStub={"query": {"a": 1}})
		doc, req = json.loads(resp.body)
		self.assertIsNone(doc)
		self.assertTrue(req["raw_path"].endswith("?a=1"))
		self.assertTrue(req["requested_path"] == ["test", "_design", "test", "_show", "args?a=1"])
		self.assertTrue(req["path"] == ["test", "_design", "test", "_show", "args"])

	def testSettingForm(self):
		resp = self._db.show("test/args", reqObjStub={"form": {"a": 1}})
		doc, req = json.loads(resp.body)
		self.assertIsNone(doc)
		self.assertEqual(req["body"], "a=1")
		self.assertEqual(req["headers"]["Content-Type"], "application/x-www-form-urlencoded")
		self.assertEqual(req["headers"]["Content-Length"], "3")
		self.assertEqual(req["method"], "POST")

	def testUnexistingDDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("abc/args")
		self.assertEqual(cm.exception["name"], "not_found")
		self.assertEqual(cm.exception["message"], "missing")

	def testUnexistingShowFunc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/unexisting-show")
		self.assertEqual(cm.exception["status"], 404)
		self.assertEqual(cm.exception["error"], "not_found")
		self.assertEqual(cm.exception["reason"], "missing show function unexisting-show on design doc _design/test")

	def testProvidersDefault(self):
		resp = self._db.show("test/usingProviders")
		self.assertEqual(resp["code"], 200)
		self.assertEqual(resp["body"], "<h1>Hello World!</h1>")
		self.assertEqual(resp["headers"]["Content-Type"], "text/html; charset=utf-8")
		self.assertEqual(resp["headers"]["Vary"], "Accept")

	def testProvidersFormat(self):
		resp = self._db.show("test/usingProviders", format="json")
		self.assertEqual(resp["code"], 200)
		self.assertEqual(json.loads(resp["body"]), {"message": "Hello World!"})
		self.assertEqual(resp["headers"]["Content-Type"], "application/json")
		self.assertEqual(resp["headers"]["Vary"], "Accept")

	def testProvidersAcceptHeader(self):
		resp = self._db.show("test/usingProviders", reqObjStub={"headers": {"Accept": "text/css,*/*;q=0.1"}})
		self.assertEqual(resp["body"], 'body {content: "Hello World!"}')
		self.assertEqual(resp["headers"]["Content-Type"], "text/css")

	def testCustomProvider(self):
		resp = self._db.show("test/usingProviders", reqObjStub={"headers": {"Accept": "application/octet-stream"}})
		self.assertEqual(resp["code"], 200)
		with self.assertRaises(KeyError):
			resp["body"]
		self.assertEqual(base64.b64decode(resp["base64"].encode("ascii")), b"Hello World!")
		self.assertEqual(resp["headers"]["Content-Type"], "application/octet-stream; charset=ascii")

	def testUnexistingFormat(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/usingProviders", format="text")
		self.assertEqual(cm.exception["status"], 500)
		self.assertEqual(cm.exception["error"], "render_error")
		self.assertEqual(cm.exception["reason"], "the format option is set to 'text', but there's no provider registered for that format.")

	def testNoMatchingProvider(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/usingProviders", reqObjStub={"headers": {"Accept": "text/plain"}})
		self.assertEqual(cm.exception["status"], 406)
		self.assertEqual(cm.exception["error"], "not_acceptable")
		self.assertTrue(cm.exception["reason"].startswith("Content-Type(s) text/plain not supported, try one of: "))
		self.assertIn("application/json", cm.exception["reason"])

	def testOldStyleJson(self):
		resp = self._db.show("test/oldStyleJson")
		self.assertEqual(resp["headers"]["Content-Type"], "application/json")
		self.assertEqual(json.loads(resp["body"]), {"old_style": "json"})

	def testFormatWhenEmptyShowFunc(self):
		resp = self._db.show("test/empty")
		self.assertEqual(resp.code, 200)
		self.assertEqual(resp["headers"]["Content-Type"], "text/html; charset=utf-8")
		self.assertEqual(resp.body, "")

	def testNoFunc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/nofunc")
		self.assertEqual(cm.exception["status"], 500)
		self.assertEqual(cm.exception["error"], "compilation_error")

	def testInvalidSyntax(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/invalidsyntax")
		self.assertEqual(cm.exception["status"], 500)
		self.assertEqual(cm.exception["error"], "compilation_error")

class AsyncShowTests(AsyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(AsyncShowTests, self).setUp()

		def cb(*args):
			pass
		self._db.put(SHOW_DOCUMENT, cb)
		self.waitUntilCalled(cb)

	def testShowWithoutDoc(self):
		def cb(err, result):
			self.assertEqual(result["body"], "no doc")
		self._db.show("test/myshow", cb)
		self.waitUntilCalled(cb)

class AsyncListTests(AsyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(AsyncListTests, self).setUp()

		def docCb(resp):
			pass

		def ddocCb(resp):
			self._db.put({"_id": "testdoc"}).then(docCb)

		self._db.put(LIST_DOCUMENT).then(ddocCb)
		self.waitUntilCalled(docCb)

	def testArgs(self):
		def cb(err, resp):
			head, req = json.loads(resp.body)
			self.assertEqual(head["offset"], 0)
			self.assertIsNone(req["id"])
			self.assertEqual(req["query"]["a"], "b")

		self._db.list("test/args/ids", cb, reqObjStub={"query": {"a": "b"}})
		self.waitUntilCalled(cb)

class SyncListTests(SyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(SyncListTests, self).setUp()

		self._db.put(LIST_DOCUMENT)
		self._db.put({"_id": "testdoc"})

	def testArgs(self):
		resp = self._db.list("test/args/ids", reqObjStub={"query": {"a": "b"}})
		head, req = json.loads(resp.body)
		self.assertEqual(head["offset"], 0)
		self.assertEqual(head["total_rows"], 1)

		self.assertIsNone(req["id"])
		self.assertEqual(req["raw_path"], "/test/_design/test/_list/args/ids?a=b")
		self.assertEqual(req["requested_path"], ["test", "_design", "test", "_list", "args", "ids?a=b"])
		self.assertEqual(req["path"], ["test", "_design", "test", "_list", "args", "ids"])
		#and one at random, to check if the rest (shared with show) is still ok.
		self.assertEqual(req["peer"], "127.0.0.1")

	def testUnexistingDesignDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("unexisting/args/ids")
		self.assertEqual(cm.exception["name"], "not_found")

	def testUnexistingShowFunc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("test/unexisting/ids")
		self.assertTrue(str(cm.exception))
		self.assertEqual(cm.exception["error"], "not_found")
		self.assertEqual(cm.exception["reason"], "missing list function unexisting on design doc _design/test")

	def testUnexistingView(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("test/args/unexisting")
		self.assertEqual(cm.exception["name"], "not_found")

	def testListApi(self):
		resp = self._db.list("test/use-list-api/ids")
		self.assertEqual(resp["headers"]["Transfer-Encoding"], "chunked")
		self.assertEqual(resp["code"], 500)
		row1, row2 = resp.body.split("\n")
		self.assertEqual(json.loads(row1), {"id": "testdoc", "key": "testdoc", "value": "value"})
		self.assertEqual(row2, "testHello World!")

class SyncUpdateTests(SyncPouchDBTestCaseWithDBAndDoc):
	def setUp(self):
		super(SyncUpdateTests, self).setUp()

		self._db.put(UPDATE_DOCUMENT)

	def testArgs(self):
		doc, req = json.loads(self._db._updatingPost("test/args/mytest", reqObjStub={"query": {"a": 3}}))
		self.assertTrue(doc["test"])
		self.assertEqual(req["id"], "mytest")
		self.assertEqual(req["raw_path"], "/test/_design/test/_update/args/mytest?a=3")

	def testArgsWithoutDoc(self):
		doc, req = json.loads(self._db._updatingPost("test/args"))
		self.assertIsNone(doc)

	def testUnexistingFunction(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db._updatingPost("test/unexisting/mytest")
		self.assertTrue(str(cm.exception))
		self.assertEqual(cm.exception["error"], "not_found")
		self.assertEqual(cm.exception["reason"], "missing update function unexisting on design doc _design/test")

	#FIXME: More tests. Including .put and async ones.
