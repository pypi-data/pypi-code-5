from fanstatic import Library, Resource

library = Library('moment.js', 'resources')

moment = Resource(library, 'moment.min.js')

moment_with_langs = Resource(
    library,
    'moment-with-langs.js',
    minified='moment-with-langs.min.js')
