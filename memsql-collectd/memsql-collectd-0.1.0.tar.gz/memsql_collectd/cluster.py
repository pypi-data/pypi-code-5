from netifaces import interfaces, ifaddresses, AF_INET
import re
import socket
from memsql.common.connection_pool import ConnectionPool

# Status variables specified in the following array will be sent to
# collectd as COUNTERS as well as GAUGES.
# This will cause them to be stored as both an absolute value and a
# derivative.
COUNTER_STATUS_VARIABLES = [
    "Rows_affected_by_writes",
    "Rows_returned_by_reads",
    "Successful_write_queries",
    "Successful_read_queries"
]

def find_node(connection_pool):
    addresses = _network_addresses()
    addresses_sql = ','.join(["'%s'" % address for address in addresses])
    with connection_pool.connect() as conn:
        node_row = conn.get('''
            SELECT id, host, port
            FROM nodes
            WHERE nodes.host IN (%s)
            ORDER BY host, port LIMIT 1
        ''' % addresses_sql)

    if node_row is None:
        # we may be the master node, and the dashboard may be pointing at 127.0.0.1
        with connection_pool.connect_master() as conn:
            master_host = socket.gethostbyname(conn.connection_info()[0])
            if master_host in addresses:
                # ok we are the master
                node_row = conn.get('''
                    SELECT id, port, %s AS host
                    FROM nodes WHERE master=1
                ''', master_host)

    if node_row is not None:
        return Node(node_row)

def _network_addresses():
    ret = []
    for interface in interfaces():
        details = ifaddresses(interface)
        if AF_INET in details:
            for link in details[AF_INET]:
                if link['addr'] != '127.0.0.1':
                    ret.append(link['addr'])
    return ret

class Node(object):
    def __init__(self, node_row):
        self.update_from_node(node_row)
        self.alias = None
        self._pool = ConnectionPool()

    def update_from_node(self, node):
        self.id = node.id
        self.host = node.host
        self.port = node.port

    def update_alias(self, connection_pool, alias):
        self.alias = alias

        try:
            conn = connection_pool.connect_master()

            if conn:
                conn.execute('''
                    INSERT INTO node_alias (node_id, alias)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE alias=VALUES(alias)
                ''', self.id, alias)
        finally:
            if conn:
                conn.close()

    def connect(self):
        return self._pool.connect(
            host=self.host,
            port=self.port,
            user="dashboard",
            password="",
            database="information_schema")

    def status(self):
        with self.connect() as conn:
            rows = conn.query('SHOW STATUS EXTENDED')

        for row in rows:
            name = row.Variable_name
            try:
                value = self._parse_value(row.Value)
            except ValueError:
                continue
            yield (name, value)

    STATUS_CONSTS = re.compile(r"ms|MB|KB", re.I)

    def _parse_value(self, value):
        if self.STATUS_CONSTS.search(value):
            return float(value.split(" ")[0])
        return float(value)

    def variables(self):
        with self.connect() as conn:
            rows = conn.query('SHOW VARIABLES')
        for row in rows:
            yield (row.Variable_name, row.Value)
