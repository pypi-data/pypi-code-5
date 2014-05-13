# This file is part of django-swiftstorage.
# Copyright 2014 Canonical Ltd.

# django-swiftstorage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings

DEFAULT_FILE_STORAGE = "swiftstorage.storage.SwiftStorage"
OS_USERNAME = os.getenv("OS_USERNAME", "")
OS_PASSWORD = os.getenv("OS_PASSWORD", "")
OS_AUTH_URL = os.getenv("OS_AUTH_URL", "https://keystone.example.com:443/v2.0/")
OS_REGION_NAME = os.getenv("OS_REGION_NAME", "")
OS_TENANT_NAME = os.getenv("OS_TENANT_NAME", "")
SWIFT_CONTAINER_NAME = "TEST_CONTAINER"
