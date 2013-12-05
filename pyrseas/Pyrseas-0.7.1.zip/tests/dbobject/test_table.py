# -*- coding: utf-8 -*-
"""Test tables"""

import pytest

from pyrseas.testutils import DatabaseToMapTestCase
from pyrseas.testutils import InputMapToSqlTestCase, fix_indent

CREATE_STMT = "CREATE TABLE t1 (c1 integer, c2 text)"
COMMENT_STMT = "COMMENT ON TABLE t1 IS 'Test table t1'"
CREATE_STOR_PARAMS = CREATE_STMT + \
    " WITH (fillfactor=90, autovacuum_enabled=false)"


class TableToMapTestCase(DatabaseToMapTestCase):
    """Test mapping of created tables"""

    def test_create_table(self):
        "Map a table with two columns"
        dbmap = self.to_map([CREATE_STMT])
        assert dbmap['schema public']['table t1'] == {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}]}

    def test_map_table_comment(self):
        "Map a table comment"
        dbmap = self.to_map([CREATE_STMT, COMMENT_STMT])
        assert dbmap['schema public']['table t1'] == {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'description': 'Test table t1'}

    def test_map_table_comment_quotes(self):
        "Map a table comment with quotes"
        stmts = [CREATE_STMT, "COMMENT ON TABLE t1 IS "
                 "'A \"special\" person''s table t1'"]
        dbmap = self.to_map(stmts)
        assert dbmap['schema public']['table t1'] == {
            'columns': [{'c1': {'type': 'integer'}}, {'c2': {'type': 'text'}}],
            'description': "A \"special\" person's table t1"}

    def test_map_column_comments(self):
        "Map two column comments"
        stmts = [CREATE_STMT,
                 "COMMENT ON COLUMN t1.c1 IS 'Test column c1 of t1'",
                 "COMMENT ON COLUMN t1.c2 IS 'Test column c2 of t1'"]
        dbmap = self.to_map(stmts)
        assert dbmap['schema public']['table t1'] == {
            'columns': [{'c1': {'type': 'integer',
                                'description': 'Test column c1 of t1'}},
                        {'c2': {'type': 'text',
                                'description': 'Test column c2 of t1'}}]}

    def test_map_table_options(self):
        "Map a table with options"
        dbmap = self.to_map([CREATE_STOR_PARAMS])
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}],
                  'options': ["fillfactor=90", 'autovacuum_enabled=false']}
        assert dbmap['schema public']['table t1'] == expmap

    def test_map_inherit(self):
        "Map a table that inherits from two other tables"
        stmts = [CREATE_STMT, "CREATE TABLE t2 (c3 integer)",
                 "CREATE TABLE t3 (c4 text) INHERITS (t1, t2)"]
        dbmap = self.to_map(stmts)
        expmap = {'columns': [{'c1': {'type': 'integer', 'inherited': True}},
                              {'c2': {'type': 'text', 'inherited': True}},
                              {'c3': {'type': 'integer', 'inherited': True}},
                              {'c4': {'type': 'text'}}],
                  'inherits': ['t1', 't2']}
        assert dbmap['schema public']['table t3'] == expmap

    def test_unlogged_table(self):
        "Map an unlogged table"
        if self.db.version < 90100:
            self.skipTest('Only available on PG 9.1')
        dbmap = self.to_map(["CREATE UNLOGGED TABLE t1 (c1 integer, c2 text)"])
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}],
                  'unlogged': True}
        assert dbmap['schema public']['table t1'] == expmap

    def test_map_table_within_schema(self):
        "Map a schema and a table within it"
        stmts = ["CREATE SCHEMA s1",
                 "CREATE TABLE s1.t1 (c1 INTEGER, c2 TEXT)"]
        dbmap = self.to_map(stmts)
        assert dbmap['schema s1'] == {
            'table t1': {'columns': [{'c1': {'type': 'integer'}},
                                     {'c2': {'type': 'text'}}]}}

    def test_map_select_tables(self):
        "Map two tables out of three present"
        stmts = [CREATE_STMT, "CREATE TABLE t2 (c1 integer, c2 text)",
                 "CREATE TABLE t3 (c1 integer, c2 text)"]
        dbmap = self.to_map(stmts, tables=['t2', 't1'])
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}]}
        assert dbmap['schema public']['table t1'] == expmap
        assert dbmap['schema public']['table t2'] == expmap
        assert 'table t3' not in dbmap['schema public']

    def test_map_table_sequence(self):
        "Map sequence if owned by a table"
        stmts = [CREATE_STMT, "CREATE TABLE t2 (c1 integer, c2 text)",
                 "CREATE SEQUENCE seq1", "ALTER SEQUENCE seq1 OWNED BY t2.c1",
                 "CREATE SEQUENCE seq2"]
        dbmap = self.to_map(stmts, tables=['t2'])
        self.db.execute_commit("DROP SEQUENCE seq1")
        expmap = {'columns': [{'c1': {'type': 'integer'}},
                              {'c2': {'type': 'text'}}]}
        assert 'table t1' not in dbmap['schema public']
        assert dbmap['schema public']['table t2'] == expmap
        assert 'sequence seq1' in dbmap['schema public']
        assert not 'sequence seq2' in dbmap['schema public']


class TableToSqlTestCase(InputMapToSqlTestCase):
    """Test SQL generation of table statements from input schemas"""

    def test_create_table(self):
        "Create a two-column table"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}]}})
        sql = self.to_sql(inmap)
        assert fix_indent(sql[0]) == CREATE_STMT

    def test_create_table_quoted_idents(self):
        "Create a table needing quoted identifiers"
        inmap = self.std_map()
        inmap['schema public'].update({'table order': {
            'columns': [{'primary': {'type': 'integer'}},
                        {'two words': {'type': 'text'}}]}})
        sql = self.to_sql(inmap, quote_reserved=True)
        assert fix_indent(sql[0]) == 'CREATE TABLE "order" (' \
            '"primary" integer, "two words" text)'

    def test_bad_table_map(self):
        "Error creating a table with a bad map"
        inmap = self.std_map()
        inmap['schema public'].update({'t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}]}})
        with pytest.raises(KeyError):
            self.to_sql(inmap)

    def test_missing_columns(self):
        "Error creating a table with no columns"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {'columns': []}})
        with pytest.raises(ValueError):
            self.to_sql(inmap)

    def test_drop_table(self):
        "Drop an existing table"
        sql = self.to_sql(self.std_map(), [CREATE_STMT])
        assert sql == ["DROP TABLE t1"]

    def test_rename_table(self):
        "Rename an existing table"
        inmap = self.std_map()
        inmap['schema public'].update({'table t2': {
            'oldname': 't1',
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}]}})
        sql = self.to_sql(inmap, [CREATE_STMT])
        assert sql == ["ALTER TABLE t1 RENAME TO t2"]

    def test_create_table_options(self):
        "Create a table with options"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}],
            'options': ["fillfactor=90", "autovacuum_enabled=false"]}})
        sql = self.to_sql(inmap)
        assert fix_indent(sql[0]) == CREATE_STOR_PARAMS

    def test_change_table_options(self):
        "Change a table's storage parameters"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}],
            'options': ["fillfactor=70"]}})
        sql = self.to_sql(inmap, [CREATE_STOR_PARAMS])
        assert fix_indent(sql[0]) == "ALTER TABLE t1 SET (fillfactor=70), " \
            "RESET (autovacuum_enabled)"

    def test_create_table_within_schema(self):
        "Create a new schema and a table within it"
        inmap = self.std_map()
        inmap.update({'schema s1': {'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}]}}})
        sql = self.to_sql(inmap)
        expsql = ["CREATE SCHEMA s1",
                  "CREATE TABLE s1.t1 (c1 integer, c2 text)"]
        for i in range(len(expsql)):
            assert fix_indent(sql[i]) == expsql[i]

    def test_unlogged_table(self):
        "Create an unlogged table"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}], 'unlogged': True}})
        sql = self.to_sql(inmap)
        assert fix_indent(sql[0]) == \
            "CREATE UNLOGGED TABLE t1 (c1 integer, c2 text)"


class TableCommentToSqlTestCase(InputMapToSqlTestCase):
    """Test SQL generation of table and column COMMENT statements"""

    def _tblmap(self):
        "Return a table input map with a comment"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'description': 'Test table t1',
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}]}})
        return inmap

    def test_table_with_comment(self):
        "Create a table with a comment"
        sql = self.to_sql(self._tblmap())
        assert fix_indent(sql[0]) == CREATE_STMT
        assert sql[1] == COMMENT_STMT

    def test_comment_on_table(self):
        "Create a comment for an existing table"
        sql = self.to_sql(self._tblmap(), [CREATE_STMT])
        assert sql == [COMMENT_STMT]

    def test_table_comment_quotes(self):
        "Create a table comment with quotes"
        inmap = self._tblmap()
        inmap['schema public']['table t1']['description'] = \
            "A \"special\" person's table t1"
        sql = self.to_sql(inmap, [CREATE_STMT])
        assert sql == ["COMMENT ON TABLE t1 IS "
                       "'A \"special\" person''s table t1'"]

    def test_drop_table_comment(self):
        "Drop a comment on an existing table"
        inmap = self._tblmap()
        del inmap['schema public']['table t1']['description']
        sql = self.to_sql(inmap, [CREATE_STMT, COMMENT_STMT])
        assert sql == ["COMMENT ON TABLE t1 IS NULL"]

    def test_change_table_comment(self):
        "Change existing comment on a table"
        inmap = self._tblmap()
        inmap['schema public']['table t1'].update(
            {'description': 'Changed table t1'})
        sql = self.to_sql(inmap, [CREATE_STMT, COMMENT_STMT])
        assert sql == ["COMMENT ON TABLE t1 IS 'Changed table t1'"]

    def test_create_column_comments(self):
        "Create a table with column comments"
        inmap = self._tblmap()
        inmap['schema public']['table t1']['columns'][0]['c1'].update(
            description='Test column c1')
        inmap['schema public']['table t1']['columns'][1]['c2'].update(
            description='Test column c2')
        sql = self.to_sql(inmap)
        assert fix_indent(sql[0]) == CREATE_STMT
        assert sql[1] == COMMENT_STMT
        assert sql[2] == "COMMENT ON COLUMN t1.c1 IS 'Test column c1'"
        assert sql[3] == "COMMENT ON COLUMN t1.c2 IS 'Test column c2'"

    def test_add_column_comment(self):
        "Add a column comment to an existing table"
        inmap = self._tblmap()
        inmap['schema public']['table t1']['columns'][0]['c1'].update(
            description='Test column c1')
        sql = self.to_sql(inmap, [CREATE_STMT, COMMENT_STMT])
        assert sql[0] == "COMMENT ON COLUMN t1.c1 IS 'Test column c1'"

    def test_add_column_with_comment(self):
        "Add a commented column to an existing table"
        inmap = self._tblmap()
        inmap['schema public']['table t1']['columns'].append({'c3': {
            'description': 'Test column c3', 'type': 'integer'}})
        sql = self.to_sql(inmap, [CREATE_STMT, COMMENT_STMT])
        assert fix_indent(sql[0]) == "ALTER TABLE t1 ADD COLUMN c3 integer"
        assert sql[1] == "COMMENT ON COLUMN t1.c3 IS 'Test column c3'"

    def test_drop_column_comment(self):
        "Drop a column comment on an existing table"
        stmts = [CREATE_STMT, COMMENT_STMT,
                 "COMMENT ON COLUMN t1.c1 IS 'Test column c1'"]
        sql = self.to_sql(self._tblmap(), stmts)
        assert sql[0] == "COMMENT ON COLUMN t1.c1 IS NULL"

    def test_change_column_comment(self):
        "Add a column comment to an existing table"
        inmap = self._tblmap()
        inmap['schema public']['table t1']['columns'][0]['c1'].update(
            description='Changed column c1')
        sql = self.to_sql(inmap, [CREATE_STMT, COMMENT_STMT])
        assert sql[0] == "COMMENT ON COLUMN t1.c1 IS 'Changed column c1'"


class TableInheritToSqlTestCase(InputMapToSqlTestCase):
    """Test SQL generation of table inheritance statements"""

    def test_table_inheritance(self):
        "Create a table that inherits from another"
        inmap = self.std_map()
        inmap['schema public'].update({'table t1': {
            'columns': [{'c1': {'type': 'integer'}},
                        {'c2': {'type': 'text'}}]}})
        inmap['schema public'].update({'table t2': {
            'columns': [{'c1': {'type': 'integer', 'inherited': True}},
                        {'c2': {'type': 'text', 'inherited': True}},
                        {'c3': {'type': 'numeric'}}], 'inherits': ['t1']}})
        sql = self.to_sql(inmap)
        assert fix_indent(sql[0]) == CREATE_STMT
        assert fix_indent(sql[1]) == "CREATE TABLE t2 (c3 numeric) " \
            "INHERITS (t1)"

    def test_drop_inherited(self):
        "Drop tables that inherit from others"
        stmts = [CREATE_STMT, "CREATE TABLE t2 (c3 numeric) INHERITS (t1)",
                 "CREATE TABLE t3 (c4 date) INHERITS (t2)"]
        sql = self.to_sql(self.std_map(), stmts)
        assert sql == ["DROP TABLE t3", "DROP TABLE t2", "DROP TABLE t1"]
