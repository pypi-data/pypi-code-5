'''
Copyright 2011 SRI International

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on Apr 27, 2011

@author: jklo
'''
import re
import hashlib
import gnupg
import types
import os, copy
from ..errors import UnknownKeyException, InvalidPassphrase, IncompatibleDocumentVersion
from ..bencode import bencode
from abc import ABCMeta

def _cmp_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

class SignBase(object):
    __meta_class__ = ABCMeta
    signatureMethod = "LR-PGP.1.0"
    min_doc_version = "0.21.0"


    '''
    Base class for signing LR envelopes following version 0.21.0 of the LR Specification:
        see: https://docs.google.com/document/d/191BTary350To_4JokBUFZLFRMOEfGYrl_EHE6QZxUr8/edit
    '''

    def __init__(self, privateKeyID=None, passphrase=None, gnupgHome=os.path.expanduser(os.path.join("~", ".gnupg")), gpgbin="/usr/local/bin/gpg", publicKeyLocations=[], sign_everything=True):
        '''
        Constructor
        '''
        self.privateKeyID = privateKeyID
        self.passphrase = passphrase
        self.gnupgHome = gnupgHome
        self.gpgbin = gpgbin
        self.publicKeyLocations = publicKeyLocations
        self.sign_everything = sign_everything

        self.gpg = gnupg.GPG(gnupghome=self.gnupgHome, gpgbinary=self.gpgbin)

        secretKeys = self.gpg.list_keys(secret=True)

        if self.privateKeyID != None:
            # remove spaces from key as `gpg --fingerprint` returns a key with spaces
            self.privateKeyID = self.privateKeyID.replace(' ', '')

            privateKeyAvailable = False
            for skey in secretKeys:
                if skey["keyid"] == self.privateKeyID:
                    privateKeyAvailable = True
                    self.privateKeyInfo = skey
                    break
                if skey["fingerprint"] == self.privateKeyID:
                    privateKeyAvailable = True
                    self.privateKeyInfo = skey

            if privateKeyAvailable == False:
                raise UnknownKeyException(self.privateKeyID)

    def _version_check(self, doc):
        if _cmp_version(doc["doc_version"], self.min_doc_version) < 0:
            raise IncompatibleDocumentVersion(
                "Document version of %s found, looking for %s or greater" % (doc["doc_version"], self.min_doc_version)
            )

        return True

    def _bnormal(self, obj = {}):
            if isinstance(obj, types.NoneType):
                return "null"
            # Boolean needs to be checked before numeric types as Booleans are also IntType
            elif isinstance(obj, types.BooleanType):
                return str(obj).lower()
            elif isinstance(obj, (types.FloatType, types.IntType, types.LongType, types.ComplexType)):
                print "Dropping number: {0}\n".format(obj)
                raise TypeError("Numbers not permitted")
                # return str(obj)
            elif isinstance(obj, types.StringType):
                return obj
            elif isinstance(obj, types.UnicodeType):
                return obj
            elif isinstance(obj, types.ListType):
                nobj = []
                for child in obj:
                    try:
                        nobj.append(self._bnormal(child))
                    except TypeError:
                        pass
                return nobj
            elif isinstance(obj, types.DictType):
                for key in obj.keys():
                    try:
                        obj[key] = self._bnormal(obj[key])
                    except TypeError:
                        obj[key] = self._bnormal(None)
                return obj
            else:
                return obj

    def _stripEnvelope(self, envelope={}):
        fields = ["digital_signature", "publishing_node", "update_timestamp", "node_timestamp", "create_timestamp", "doc_ID", "_id", "_rev"]
        sigObj = copy.deepcopy(envelope)
        for field in fields:
            if sigObj.has_key(field):
                del sigObj[field]
        return sigObj


    def _buildCanonicalString(self, envelope = {}):
        encoded = bencode(envelope)
        return encoded

    def _hash(self, msg):
        hashedDigest = hashlib.sha256(msg.encode("utf-8")).hexdigest()
        return hashedDigest

    def get_message(self, envelope):
        '''
        Hashes the contents of an LR envelope in the following manner:

            1. remove all fields from envelope except for the following:
                "doc_type", "doc_version", "resource_data_type", "active", "submitter_type", "submitter",
                "submitter_timestamp", "submitter_TTL",  "submission_TOS", "submission_attribution",
                "resource_locator", "keys", "resource_TTL", "payload_placement"
            2. Bencode the remaining envelope [http://en.wikipedia.org/wiki/Bencode]
            3. Hash the Bencoded string using a SHA256
            4. Convert SHA256 to hexadecimal digest.

        Returns digest as string.
        '''

        stripped = self._stripEnvelope(envelope)
        normalized = self._bnormal(stripped)
        canonical = self._buildCanonicalString(normalized)
        hashedDigest = self._hash(canonical)

        return hashedDigest

    def _get_privatekey_owner(self):
        if self.privateKeyInfo.has_key("uids") and isinstance(self.privateKeyInfo["uids"], types.ListType):
            return ", ".join(self.privateKeyInfo["uids"])

        return None


    def _get_sig_block(self, sigdata):
        signature = {
            "signature": sigdata,
            "key_location": self.publicKeyLocations,
            "signing_method": self.signatureMethod
        }

        pkowner = self._get_privatekey_owner()
        if pkowner != None:
            signature["key_owner"] = pkowner

        return signature

    def sign(self, envelope):
        '''
        Hashes and Signs a LR envelope according to the version 2.0 LR Specification
        '''

        # check version compatibility
        try:
            self._version_check(envelope)
        except IncompatibleDocumentVersion as ex:
            # raise IncompatibleDocumentVersion
            if not self.sign_everything:
                raise ex

        msg = self.get_message(envelope)

        signPrefs = {
                     "keyid": self.privateKeyID,
                     "passphrase": self.passphrase,
                     "clearsign": True
                }

        result = self.gpg.sign(msg, **signPrefs)

        if result.data == '':
            raise InvalidPassphrase('The passphrase provided is incorrect')


        envelope["digital_signature"] = self._get_sig_block(result.data)

        return envelope



# Alias classes to align with specification versions

class Sign_0_21(SignBase):
    min_doc_version = "0.21.0"

class Sign_0_23(SignBase):
    min_doc_version = "0.21.0"

class Sign_0_49(SignBase):
    min_doc_version = "0.49.0"

class Sign_0_51(SignBase):
    min_doc_version = "0.51.0"


if __name__ == "__main__":

    sign = Sign_0_21("C37C805D164B052C", passphrase="2dimples")

