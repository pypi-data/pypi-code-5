#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand

class GetDrawer(GetCommand):
    __domain__ = "drawer"
    __operation__ = "get"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def run(self):
        db = self._ctx.db_session()
        if (len(self.object_ids) == 0):
            # Get all drawers
            query = db.query(Note).filter(and_(Folder.status != 'archived',
                                                Folder.company_id == self._ctx.account_id,
                                                Folder.folder_id == None,
                                                Folder.project_id == None))
        else:
            query = db.query(Note).filter(and_(Folder.object_id.in_(self.object_ids),
                                                Folder.status != 'archived',
                                                Folder.company_id == self._ctx.account_id,
                                                Folder.folder_id == None,
                                                Folder.project_id == None))
        self.set_return_value(self.add_comments(query.all()))