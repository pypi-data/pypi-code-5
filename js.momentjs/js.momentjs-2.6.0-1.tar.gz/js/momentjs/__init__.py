from fanstatic import Library, Resource

library = Library('moment.js', 'resources')

moment = Resource(library, 'moment.min.js')

moment_with_langs = Resource(
    library,
    'moment-with-langs.js',
    minified='moment-with-langs.min.js')

moment_timezone = Resource(
    library,
    'moment-timezone.js',
    depends=[moment_with_langs],
    minified='moment-timezone.min.js')

moment_timezone_with_data = Resource(
    library,
    'moment-timezone-data.js',
    depends=[moment_timezone],
    minified='moment-timezone-data.min.js')
