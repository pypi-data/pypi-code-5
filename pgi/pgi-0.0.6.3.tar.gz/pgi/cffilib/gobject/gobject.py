# Copyright 2013 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

from ._ffi import ffi
from .. import _create_enum_class


GParamFlags = _create_enum_class(ffi, "GParamFlags", "G_PARAM_")
