#
# Autogenerated by Thrift Compiler (0.9.1)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class BaeRet:
  OK = 0
  RETRY = 1
  OLD_VERSION = 2
  AUTH_PARM_ERROR = 3
  AUTH_FAIL = 4
  AUTH_ASK_NOT_EXIST = 5
  AUTH_ASK_NOT_MATCH = 6
  AUTH_QUOTA_NOT_INIT = 7
  AUTH_QUOTA_EXCEED = 8
  AUTH_QUOTA_UPDATE_ERROR = 9
  AUTH_CONN_FAIL = 10
  INTERNAL_ERROR = 11

  _VALUES_TO_NAMES = {
    0: "OK",
    1: "RETRY",
    2: "OLD_VERSION",
    3: "AUTH_PARM_ERROR",
    4: "AUTH_FAIL",
    5: "AUTH_ASK_NOT_EXIST",
    6: "AUTH_ASK_NOT_MATCH",
    7: "AUTH_QUOTA_NOT_INIT",
    8: "AUTH_QUOTA_EXCEED",
    9: "AUTH_QUOTA_UPDATE_ERROR",
    10: "AUTH_CONN_FAIL",
    11: "INTERNAL_ERROR",
  }

  _NAMES_TO_VALUES = {
    "OK": 0,
    "RETRY": 1,
    "OLD_VERSION": 2,
    "AUTH_PARM_ERROR": 3,
    "AUTH_FAIL": 4,
    "AUTH_ASK_NOT_EXIST": 5,
    "AUTH_ASK_NOT_MATCH": 6,
    "AUTH_QUOTA_NOT_INIT": 7,
    "AUTH_QUOTA_EXCEED": 8,
    "AUTH_QUOTA_UPDATE_ERROR": 9,
    "AUTH_CONN_FAIL": 10,
    "INTERNAL_ERROR": 11,
  }

class BaeLogLevel:
  FATAL = 1
  WARNING = 2
  NOTICE = 4
  TRACE = 8
  DEBUG = 16

  _VALUES_TO_NAMES = {
    1: "FATAL",
    2: "WARNING",
    4: "NOTICE",
    8: "TRACE",
    16: "DEBUG",
  }

  _NAMES_TO_VALUES = {
    "FATAL": 1,
    "WARNING": 2,
    "NOTICE": 4,
    "TRACE": 8,
    "DEBUG": 16,
  }


class UserLogEntry:
  """
  Attributes:
   - appid
   - level
   - timestamp
   - msg
   - logid
   - tag
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'appid', None, None, ), # 1
    (2, TType.I32, 'level', None, None, ), # 2
    (3, TType.I64, 'timestamp', None, None, ), # 3
    (4, TType.STRING, 'msg', None, None, ), # 4
    None, # 5
    None, # 6
    None, # 7
    (8, TType.STRING, 'logid', None, None, ), # 8
    (9, TType.STRING, 'tag', None, None, ), # 9
  )

  def __init__(self, appid=None, level=None, timestamp=None, msg=None, logid=None, tag=None,):
    self.appid = appid
    self.level = level
    self.timestamp = timestamp
    self.msg = msg
    self.logid = logid
    self.tag = tag

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.appid = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I32:
          self.level = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.timestamp = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRING:
          self.msg = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.STRING:
          self.logid = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.STRING:
          self.tag = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('UserLogEntry')
    if self.appid is not None:
      oprot.writeFieldBegin('appid', TType.STRING, 1)
      oprot.writeString(self.appid)
      oprot.writeFieldEnd()
    if self.level is not None:
      oprot.writeFieldBegin('level', TType.I32, 2)
      oprot.writeI32(self.level)
      oprot.writeFieldEnd()
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I64, 3)
      oprot.writeI64(self.timestamp)
      oprot.writeFieldEnd()
    if self.msg is not None:
      oprot.writeFieldBegin('msg', TType.STRING, 4)
      oprot.writeString(self.msg)
      oprot.writeFieldEnd()
    if self.logid is not None:
      oprot.writeFieldBegin('logid', TType.STRING, 8)
      oprot.writeString(self.logid)
      oprot.writeFieldEnd()
    if self.tag is not None:
      oprot.writeFieldBegin('tag', TType.STRING, 9)
      oprot.writeString(self.tag)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.appid is None:
      raise TProtocol.TProtocolException(message='Required field appid is unset!')
    if self.level is None:
      raise TProtocol.TProtocolException(message='Required field level is unset!')
    if self.timestamp is None:
      raise TProtocol.TProtocolException(message='Required field timestamp is unset!')
    if self.msg is None:
      raise TProtocol.TProtocolException(message='Required field msg is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SecretEntry:
  """
  Attributes:
   - user
   - passwd
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'user', None, None, ), # 1
    (2, TType.STRING, 'passwd', None, None, ), # 2
  )

  def __init__(self, user=None, passwd=None,):
    self.user = user
    self.passwd = passwd

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.user = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.passwd = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('SecretEntry')
    if self.user is not None:
      oprot.writeFieldBegin('user', TType.STRING, 1)
      oprot.writeString(self.user)
      oprot.writeFieldEnd()
    if self.passwd is not None:
      oprot.writeFieldBegin('passwd', TType.STRING, 2)
      oprot.writeString(self.passwd)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.user is None:
      raise TProtocol.TProtocolException(message='Required field user is unset!')
    if self.passwd is None:
      raise TProtocol.TProtocolException(message='Required field passwd is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class BaeLogEntry:
  """
  Attributes:
   - category
   - content
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'category', None, None, ), # 1
    (2, TType.STRING, 'content', None, None, ), # 2
  )

  def __init__(self, category=None, content=None,):
    self.category = category
    self.content = content

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.category = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.content = iprot.readString();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('BaeLogEntry')
    if self.category is not None:
      oprot.writeFieldBegin('category', TType.STRING, 1)
      oprot.writeString(self.category)
      oprot.writeFieldEnd()
    if self.content is not None:
      oprot.writeFieldBegin('content', TType.STRING, 2)
      oprot.writeString(self.content)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.category is None:
      raise TProtocol.TProtocolException(message='Required field category is unset!')
    if self.content is None:
      raise TProtocol.TProtocolException(message='Required field content is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class BaeLog:
  """
  Attributes:
   - messages
   - secret
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'messages', (TType.STRUCT,(BaeLogEntry, BaeLogEntry.thrift_spec)), None, ), # 1
    (2, TType.STRUCT, 'secret', (SecretEntry, SecretEntry.thrift_spec), None, ), # 2
  )

  def __init__(self, messages=None, secret=None,):
    self.messages = messages
    self.secret = secret

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.LIST:
          self.messages = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = BaeLogEntry()
            _elem5.read(iprot)
            self.messages.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.secret = SecretEntry()
          self.secret.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('BaeLog')
    if self.messages is not None:
      oprot.writeFieldBegin('messages', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.messages))
      for iter6 in self.messages:
        iter6.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    if self.secret is not None:
      oprot.writeFieldBegin('secret', TType.STRUCT, 2)
      self.secret.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.messages is None:
      raise TProtocol.TProtocolException(message='Required field messages is unset!')
    return


  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
