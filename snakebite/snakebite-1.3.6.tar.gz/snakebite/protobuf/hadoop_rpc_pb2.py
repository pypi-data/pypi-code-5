# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='hadoop_rpc.proto',
  package='',
  serialized_pb='\n\x10hadoop_rpc.proto\"\x7f\n\x15HadoopRpcRequestProto\x12\x12\n\nmethodName\x18\x01 \x02(\t\x12\x0f\n\x07request\x18\x02 \x01(\x0c\x12\"\n\x1a\x64\x65\x63laringClassProtocolName\x18\x03 \x02(\t\x12\x1d\n\x15\x63lientProtocolVersion\x18\x04 \x02(\x04\x42\x34\n\x1eorg.apache.hadoop.ipc.protobufB\x0fHadoopRpcProtos\xa0\x01\x01')




_HADOOPRPCREQUESTPROTO = descriptor.Descriptor(
  name='HadoopRpcRequestProto',
  full_name='HadoopRpcRequestProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='methodName', full_name='HadoopRpcRequestProto.methodName', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='request', full_name='HadoopRpcRequestProto.request', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='declaringClassProtocolName', full_name='HadoopRpcRequestProto.declaringClassProtocolName', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='clientProtocolVersion', full_name='HadoopRpcRequestProto.clientProtocolVersion', index=3,
      number=4, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=20,
  serialized_end=147,
)

DESCRIPTOR.message_types_by_name['HadoopRpcRequestProto'] = _HADOOPRPCREQUESTPROTO

class HadoopRpcRequestProto(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _HADOOPRPCREQUESTPROTO
  
  # @@protoc_insertion_point(class_scope:HadoopRpcRequestProto)

# @@protoc_insertion_point(module_scope)
