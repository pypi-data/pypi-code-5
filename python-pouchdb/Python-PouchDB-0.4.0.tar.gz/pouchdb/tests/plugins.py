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

from pouchdb.tests.utils import (
	SyncPouchDBTestCaseWithDB,
	SyncPouchDBTestCaseWithDBAndDoc,
	SyncPouchDBTestCaseWithDBAndAttachment,
	SyncPouchDBHTTPTestCase,

	AsyncPouchDBTestCaseWithDB,

	BASE_URL,
	FAST_ONLY,
)

import pouchdb
import json
import base64
import unittest

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
			return toJSON({args: [doc, req]});
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
		"invalidsyntax": """function (doc, req)) {}""",
		"invalidReturnTypeAndProvides": """function (doc, req) {
			provides("html", function () {
				return 42;
			});
		}""",
		"throwingErrorInProvides": """function (doc, req) {
			provides("text", function () {
				throw new Error("Hello World!");
			});
		}""",
		"invalidRespObject": """function (doc, req) {
			return {body: "test", abc: "test"};
		}"""
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
			return toJSON({args: [head, req]});
		}""",
		"use-list-api": """function (head, req) {
			start({code: 500});
			send(JSON.stringify(getRow()));
			send("\\n");
			send("test");
			return "Hello World!";
		}""",
		"test-coucheval": """function (head, req) {
			var result = sum([1, 2, 3]);
			return result + " - " + require("lib/thingy").data;
		}"""
	},
	"lib": {
		"thingy": "exports.data = 'Hello World!';"
	}
}

UPDATE_DOCUMENT = {
	"_id": "_design/test",
	"updates": {
		"args": """function (doc, req) {
			return [null, toJSON([doc, req])];
		}""",
		"exception": """function (doc, req) {
			return abc;
		}""",
		"save-adding-date": """function (oldDoc, req) {
			var doc = JSON.parse(req.body);
			doc.updated = new Date();
			return [doc, "Hello World!"];
		}"""
	}
}

class AlternateSignatureTests(SyncPouchDBTestCaseWithDB):
	"""Tests alternative signatures for the internally developed
	plug-ins that ship with Python-PouchDB. Hard to do via the Python
	interface since that interface uses a fixed JS signature regardless
	of which Python signature is used. (At least mostly)

	"""
	def testShow(self):
		#the fact that dbs are stored in ``objects`` is an
		#implementation detail.
		promise = self._env.context.evalJs("return objects[%s].show('test/test/test', function () {});" % self._db._id)
		self.assertPromise(promise)

	def testList(self):
		promise = self._env.context.evalJs("return objects[%s].list('test/test/test', function () {});" % self._db._id)
		self.assertPromise(promise)

	def testValidatingPost(self):
		promise = self._env.context.evalJs("return objects[%s].validatingPost({}, function () {});" % self._db._id)
		self.assertPromise(promise)

	def testUpdatingPost(self):
		promise = self._env.context.evalJs("return objects[%s].updatingPost('test/test/test', function () {});" % self._db._id)
		self.assertPromise(promise)

@unittest.skipIf(FAST_ONLY, "too slow")
class PluginHTTPTests(SyncPouchDBHTTPTestCase):
	def testShow(self):
		self._db.put(SHOW_DOCUMENT)

		resp = self._db.show("test/args", body="Hello World!", headers={"Content-Type": "text/plain"})
		self.assertEqual(resp["code"], 200)
		self.assertEqual(resp["headers"]["Content-Type"], "text/html; charset=utf-8")

		doc, req = json.loads(resp.body)["args"]

		#test doc - well, the unavailability of it...
		self.assertIsNone(doc)

		#test request object
		self.assertEqual(req["body"], "Hello World!")
		self.assertEqual(req["cookie"], {})
		self.assertEqual(req["form"], {})

		self.assertIn(req["headers"]["Host"], BASE_URL)
		self.assertEqual(req["headers"]["Accept"], "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		self.assertEqual(req["headers"]["Content-Type"], "text/plain")
		self.assertIn("en", req["headers"]["Accept-Language"])
		self.assertIn("en-us", req["headers"]["Accept-Language"])
		self.assertWebKitUserAgent(req["headers"]["User-Agent"])

		self.assertIsNone(req["id"])
		self.assertEqual(req["info"]["db_name"], "test")
		self.assertIn("update_seq", req["info"])
		self.assertEqual(req["method"], "POST")
		self.assertEqual(req["path"], ["test", "_design", "test", "_show", "args"])
		self.assertEqual(req["peer"], "127.0.0.1")
		self.assertEqual(req["query"], {})
		self.assertEqual(req["raw_path"], "/test/_design/test/_show/args")
		self.assertEqual(req["requested_path"], ["test", "_design", "test", "_show", "args"])
		self.assertEqual(req["secObj"], {})
		self.assertEqual(req["userCtx"]["db"], "test")
		self.assertIn("name", req["userCtx"])
		self.assertUuid(req["uuid"])

	def testList(self):
		self._db.put(LIST_DOCUMENT)

		resp = self._db.list(
			"test/args/ids",
			query={"a": "b"},
		)

		head, req = json.loads(resp.body)["args"]
		self.assertEqual(head["offset"], 0)
		self.assertEqual(head["total_rows"], 0)

		self.assertIsNone(req["id"])
		self.assertEqual(req["raw_path"], "/test/_design/test/_list/args/ids?a=b")
		self.assertEqual(req["requested_path"], ["test", "_design", "test", "_list", "args", "ids?a=b"])
		self.assertEqual(req["path"], ["test", "_design", "test", "_list", "args", "ids"])
		#and one at random, to check if the rest (shared with show) is still ok.
		self.assertEqual(req["peer"], "127.0.0.1")

	def testWrongListContentType(self):
		"""CouchDB only supports application/json here. It's a CouchDB
		restriction: this check is here in case it ever changes. - then
		PouchDB-List's simulation of it can stop.

		"""
		self._db.put(LIST_DOCUMENT)
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("test/args/ids", headers={"Content-Type": "application/x-www-form-urlencoded"}, body="value=hello")
		self.assertEqual(cm.exception["status"], 400)
		self.assertEqual(cm.exception["name"], "bad_request")
		self.assertEqual(cm.exception["message"], "invalid_json")

	def testValidation(self):
		self._db.put(ONLY_TEST_VALIDATION_DOC)

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPost({})
		self.assertEqual(cm.exception["status"], 403)
		self.assertEqual(cm.exception["name"], "forbidden")
		self.assertEqual(cm.exception["message"], "only a document named 'test' is allowed.")

		resp = self._db.validatingPut({"_id": "test"})
		self.assertTrue(resp.ok)

	def testUpdate(self):
		self._db.put(UPDATE_DOCUMENT)
		doc, req = json.loads(self._db.updatingPut("test/args/my-id").body)
		self.assertIsNone(doc)
		self.assertEqual(req["id"], "my-id")

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
			self.assertEqual(err.name, "forbidden")

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
		self.assertEqual(exc["name"], "unauthorized")
		self.assertEqual(exc["message"], "only a document named 'test' is allowed.")

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
		self.assertEqual(exc["name"], "forbidden")
		self.assertEqual(exc["message"], "only a document named 'test' is allowed.")

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
				{}
			],
		})
		self._checkException(resp[0])
		self._checkException(resp[1])

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
		self.assertEqual(e["name"], "compilation_error")
		self.assertIn("Expression does not eval to a function.", e["message"])

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

		self.assertEqual(cm.exception["name"], "ReferenceError")
		#'test' is the name of the missing variable.
		self.assertIn("test", cm.exception["message"])

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
		self.assertEqual(cm.exception["name"], "forbidden")
		#checks if the newDoc argument is filled in correctly
		self.assertIn('"_attachments":{}', cm.exception["message"])

	def testPutAttachmentSuccess(self):
		self._db.validatingPutAttachment("attachment_test2", "text", u"tést".encode("UTF-8"), "text/plain")

	def testPutAttachmentWhenForbidden(self):
		self._db.put(self.forbiddenDesignDoc)
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPutAttachment("attachment_test2", "text", u"tést".encode("UTF-8"), "text/plain")
		self.assertEqual(cm.exception["name"], "forbidden")
		#checks if the newDoc argument is filled in correctly
		self.assertIn("text/plain", cm.exception["message"])

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
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["message"])
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
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["message"])
		self.assertTrue(oldDoc["test"])
		self.assertIn("ids", oldDoc["_revisions"])
		self.assertIn("ids", newDoc["_revisions"])

	def testChangingUserCtx(self):
		theUserCtx = {
			"db": "test",
			"name": "pypouchtest",
			"roles": ["the_boss"]
		}

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validatingPost({}, userCtx=theUserCtx)
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["message"])

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
		newDoc, oldDoc, userCtx, secObj = json.loads(cm.exception["message"])

		self.assertEqual(secObj, theSecObj)

class SyncShowTests(SyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(SyncShowTests, self).setUp()

		self._db.put(SHOW_DOCUMENT)

	def testInvalidRespObj(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/invalidRespObject")
		self.assertEqual(cm.exception["status"], 500)
		self.assertEqual(cm.exception["name"], "external_response_error")
		self.assertEqual(cm.exception["message"], 'Invalid data from external server: {<<"abc">>,<<"test">>}')

	def testShowWithoutDocAndDifferentEnv(self):
		self._env.context.evalJs("window.theNavigator = window.navigator; window.navigator = undefined;")
		result = self._db.show("test/myshow")
		self.assertEqual(result["code"], 200)
		self._env.context.evalJs("window.navigator = window.theNavigator; delete window.theNavigator;")

	def testInvalidReturnTypeAndProvides(self):
		result = self._db.show("test/invalidReturnTypeAndProvides")
		self.assertEqual(result["code"], 200)
		self.assertEqual(result["body"], "")

	def testThrowingErrorInProvides(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/throwingErrorInProvides")
		self.assertEqual(cm.exception["status"], 500)

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
		resp = self._db.show("test/args", method="POST")
		doc, req = json.loads(resp.body)["args"]
		self.assertEqual(req["method"], "POST")

	def testOverwriteHeader(self):
		resp = self._db.show("test/args", headers={"Host": "example.com"})
		doc, req = json.loads(resp.body)["args"]
		#check if the header update was succesful.
		self.assertEqual(req["headers"]["Host"], "example.com")
		#check if other headers (test subject is Accept) are still set.
		self.assertEqual(req["headers"]["Accept"], "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

	def testShowArgs(self):
		doc, req = json.loads(self._db.show("test/args").body)["args"]

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
		self.assertWebKitUserAgent(req["headers"]["User-Agent"])

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
		doc, req = json.loads(self._db.show("test/args/abc").body)["args"]
		self.assertIsNone(doc)
		self.assertEqual(req["id"], "abc")
		self.assertIn("abc", req["path"])

	def testWithDesignDocAsArg(self):
		doc, req = json.loads(self._db.show("test/args/_design/test").body)["args"]
		self.assertEqual(req["id"], "_design/test")
		self.assertEqual(req["raw_path"], "/test/_design/test/_show/args/_design/test")
		self.assertIn("shows", doc)

	def testWithFakeDesignDocAsArg(self):
		doc, req = json.loads(self._db.show("test/args/_design").body)["args"]
		self.assertIsNone(doc)
		self.assertEqual(req["id"], "_design")
		self.assertEqual(req["raw_path"], "/test/_design/test/_show/args/_design")

	def testSettingQuery(self):
		resp = self._db.show("test/args", query={"a": 1})
		doc, req = json.loads(resp.body)["args"]
		self.assertIsNone(doc)
		self.assertTrue(req["raw_path"].endswith("?a=1"))
		self.assertTrue(req["requested_path"] == ["test", "_design", "test", "_show", "args?a=1"])
		self.assertTrue(req["path"] == ["test", "_design", "test", "_show", "args"])

	def testSettingForm(self):
		resp = self._db.show("test/args", form={"a": 1})
		doc, req = json.loads(resp.body)["args"]
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
		self.assertEqual(cm.exception["name"], "not_found")
		self.assertEqual(cm.exception["message"], "missing show function unexisting-show on design doc _design/test")

	def testProvidersDefault(self):
		resp = self._db.show("test/usingProviders")
		self.assertEqual(resp["code"], 200)
		self.assertEqual(resp["body"], "<h1>Hello World!</h1>")
		self.assertEqual(resp["headers"]["Content-Type"], "text/html; charset=utf-8")
		self.assertEqual(resp["headers"]["Vary"], "Accept")

	def testProvidersFormat(self):
		resp = self._db.show("test/usingProviders", query={"format": "json"})
		self.assertEqual(resp["code"], 200)
		self.assertEqual(json.loads(resp["body"]), {"message": "Hello World!"})
		self.assertEqual(resp["headers"]["Content-Type"], "application/json")
		self.assertEqual(resp["headers"]["Vary"], "Accept")

	def testProvidersAcceptHeader(self):
		resp = self._db.show("test/usingProviders", headers={"Accept": "text/css,*/*;q=0.1"})
		self.assertEqual(resp["body"], 'body {content: "Hello World!"}')
		self.assertEqual(resp["headers"]["Content-Type"], "text/css")

	def testCustomProvider(self):
		resp = self._db.show("test/usingProviders", headers={"Accept": "application/octet-stream"})
		self.assertEqual(resp["code"], 200)
		with self.assertRaises(KeyError):
			resp["body"]
		self.assertEqual(base64.b64decode(resp["base64"].encode("ascii")), b"Hello World!")
		self.assertEqual(resp["headers"]["Content-Type"], "application/octet-stream; charset=ascii")

	def testUnexistingFormat(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/usingProviders", query={"format": "text"})
		self.assertEqual(cm.exception["status"], 500)
		self.assertEqual(cm.exception["name"], "render_error")
		self.assertEqual(cm.exception["message"], "the format option is set to 'text', but there's no provider registered for that format.")

	def testNoMatchingProvider(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/usingProviders", headers={"Accept": "text/plain"})
		self.assertEqual(cm.exception["status"], 406)
		self.assertEqual(cm.exception["name"], "not_acceptable")
		self.assertTrue(cm.exception["message"].startswith("Content-Type(s) text/plain not supported, try one of: "))
		self.assertIn("application/json", cm.exception["message"])

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
		self.assertEqual(cm.exception["name"], "compilation_error")

	def testInvalidSyntax(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/invalidsyntax")
		self.assertEqual(cm.exception["status"], 500)
		self.assertEqual(cm.exception["name"], "compilation_error")

class SyncShowTestsWithEmptyDesignDoc(SyncPouchDBTestCaseWithDB):
	def test(self):
		self._db.put({"_id": "_design/test"})

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.show("test/test/test")

		self.assertEqual(cm.exception["status"], 404)

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

	def testUnexistingDDoc(self):
		def cb(err, resp):
			self.assertEqual(err["name"], "not_found")
			self.assertEqual(err["message"], "missing")

		self._db.show("abc/args", cb)
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
			head, req = json.loads(resp.body)["args"]
			self.assertEqual(head["offset"], 0)
			self.assertIsNone(req["id"])
			self.assertEqual(req["query"]["a"], "b")

		self._db.list("test/args/ids", cb, query={"a": "b"})
		self.waitUntilCalled(cb)

class SyncListTestsWithEmptyDesignDoc(SyncPouchDBTestCaseWithDB):
	def test(self):
		self._db.put({"_id": "_design/test"})

		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("test/test/test")

		self.assertEqual(cm.exception["status"], 404)

class SyncListTests(SyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(SyncListTests, self).setUp()

		self._db.put(LIST_DOCUMENT)
		self._db.put({"_id": "testdoc"})

	def testCouchEval(self):
		resp = self._db.list("test/test-coucheval/ids")
		self.assertEqual(resp["code"], 200)
		self.assertEqual(resp["body"], "6 - Hello World!")

	def testArgs(self):
		resp = self._db.list("test/args/ids", query={"a": "b"})
		head, req = json.loads(resp.body)["args"]
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

	def testUnexistingListFunc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("test/unexisting/ids")
		self.assertTrue(str(cm.exception))
		self.assertEqual(cm.exception["name"], "not_found")
		self.assertEqual(cm.exception["message"], "missing list function unexisting on design doc _design/test")

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

	def testWrongContentType(self):
		"""CouchDB only supports application/json here. It's a CouchDB
		restriction: probably best to emulate it...

		"""
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.list("test/args/ids", headers={"Content-Type": "application/x-www-form-urlencoded"})
		self.assertEqual(cm.exception["status"], 400)
		self.assertEqual(cm.exception["name"], "bad_request")
		self.assertEqual(cm.exception["message"], "invalid_json")

class SyncUpdateTests(SyncPouchDBTestCaseWithDBAndDoc):
	def setUp(self):
		super(SyncUpdateTests, self).setUp()

		self._db.put(UPDATE_DOCUMENT)

	def testArgs(self):
		doc, req = json.loads(self._db.updatingPost("test/args/mytest", query={"a": 3}).body)
		self.assertTrue(doc["test"])
		self.assertEqual(req["id"], "mytest")
		self.assertEqual(req["raw_path"], "/test/_design/test/_update/args/mytest?a=3")

	def testArgsWithoutDoc(self):
		resp = self._db.updatingPost("test/args", withValidation=True)
		doc, req = json.loads(resp.body)
		self.assertIsNone(doc)
		self.assertNotIn("withValidation", req)

	def testUnexistingFunction(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.updatingPost("test/unexisting/mytest")
		self.assertTrue(str(cm.exception))
		self.assertEqual(cm.exception["name"], "not_found")
		self.assertEqual(cm.exception["message"], "missing update function unexisting on design doc _design/test")

	def testSaving(self):
		resp = self._db.updatingPost("test/save-adding-date", body=json.dumps({
			"_id": "test",
			"name": "Today"
		}))
		self.assertEqual(resp.body, "Hello World!")

		doc = self._db.get("test")
		self.assertTrue(doc["updated"])
		self.assertEqual(doc["name"], "Today")

class AsyncUpdateTests(AsyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(AsyncUpdateTests, self).setUp()

		def cb(err, resp):
			pass
		self._db.put(UPDATE_DOCUMENT, cb)
		self.waitUntilCalled(cb)

	def testException(self):
		def cb(err, resp):
			self.assertEqual(err["status"], 500)
			self.assertEqual(err["name"], "ReferenceError")
			self.assertIn("abc", err["message"])

		self._db.updatingPut("test/exception", cb)
		self.waitUntilCalled(cb)

class AsyncUpdateWithEmptyDesignDocTests(AsyncPouchDBTestCaseWithDB):
	def setUp(self):
		super(AsyncUpdateWithEmptyDesignDocTests, self).setUp()

		def cb(err, resp):
			pass

		self._db.put({"_id": "_design/test"}, cb)
		self.waitUntilCalled(cb)

	def testBasic(self):
		def cb(err, resp):
			self.assertEqual(err["status"], 404)
			self.assertEqual(err["name"], "not_found")
			self.assertEqual(err["message"], "missing update function unexisting on design doc _design/test")

		self._db.updatingPost("test/unexisting", cb)
		self.waitUntilCalled(cb)
