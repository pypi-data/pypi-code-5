CUCKOO_EP = (  # pragma: no cover
    (['POST'], 'tasks_create_file', '/tasks/create/file',
     'Adds a file to the list of pending tasks to be processed and analyzed.'),
    (['POST'], 'tasks_create_url', '/tasks/create/url',
     'An URL to the list of pending tasks to be processed and analyzed.'),
    (['GET'], 'tasks_list', '/tasks/list',
     'Returns the list of tasks stored in the internal Cuckoo database. '
     'You can optionally specify a limit of entries to return.'),
    (['GET'], 'tasks_view', '/tasks/view',
     'Returns the details on the task assigned to the specified ID.'),
    (['GET'], 'tasks_delete', '/tasks/delete',
     'Removes the given task from the database and deletes the results.'),
    (['GET'], 'tasks_report', '/tasks/report',
     'Returns the report generated out of the analysis of the task associated '
     'with the specified ID. You can optionally specify which report format to'
     ' return, if none is specified the JSON report will be returned.'),
    (['GET'], 'tasks_shots', '/tasks/screenshots',
     'Returns one or all screenshots associated with the specified task ID.'),
    (['GET'], 'files_view', '/files/view',
     'Search the analyzed binaries by MD5 hash, SHA256 hash or internal ID '
     '(referenced by the tasks details).'),
    (['GET'], 'files_get', '/files/get',
     'The content of the binary with the specified SHA256 hash.'),
    (['GET'], 'pcap_get', '/pcap/get',
     'Returns the content of the PCAP associated with the given task.'),
    (['GET'], 'machines_list', '/machines/list',
     'Returns the list of analysis machines available to Cuckoo.'),
    (['GET'], 'machines_view', '/machines/view',
     'Returns details on the analysis machine associated with the specified '
     'name.'),
    (['GET'], 'cuckoo_status', '/cuckoo/status',
     'Returns the basic cuckoo status, including version and tasks overview'),
)
