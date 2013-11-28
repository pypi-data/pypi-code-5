"""
Scrapy Shell

See documentation in docs/topics/shell.rst
"""

from threading import Thread

from scrapy.command import ScrapyCommand
from scrapy.shell import Shell


class Command(ScrapyCommand):

    requires_project = False
    default_settings = {'KEEP_ALIVE': True, 'LOGSTATS_INTERVAL': 0}

    def syntax(self):
        return "[url|file]"

    def short_desc(self):
        return "Interactive scraping console"

    def long_desc(self):
        return "Interactive console for scraping the given url"

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option("-c", dest="code",
            help="evaluate the code in the shell, print the result and exit")
        parser.add_option("--spider", dest="spider",
            help="use this spider")

    def update_vars(self, vars):
        """You can use this function to update the Scrapy objects that will be
        available in the shell
        """
        pass

    def run(self, args, opts):
        crawler = self.crawler_process.create_crawler()

        url = args[0] if args else None
        spider = crawler.spiders.create(opts.spider) if opts.spider else None

        self.crawler_process.start_crawling()
        self._start_crawler_thread()

        shell = Shell(crawler, update_vars=self.update_vars, code=opts.code)
        shell.start(url=url, spider=spider)

    def _start_crawler_thread(self):
        t = Thread(target=self.crawler_process.start_reactor)
        t.daemon = True
        t.start()
