from coverage.report import Reporter
from coverage.misc import NotPython


class CoverallsReporter(Reporter):
    def report(self, base_dir, ignore_errors=False):
        ret = []
        for cu in self.code_units:
            try:
                with open(cu.filename) as fp:
                    source = fp.readlines()
            except IOError:
                if ignore_errors:
                    continue
                else:
                    raise
            try:
                analysis = self.coverage._analyze(cu)
            except NotPython:
                if ignore_errors:
                    continue
                else:
                    raise
            coverage_list = [None for _ in source]
            for lineno, line in enumerate(source):
                if lineno + 1 in analysis.statements:
                    coverage_list[lineno] = int(lineno + 1 not in analysis.missing)
            ret.append({
                'name': cu.filename.replace(base_dir, '').lstrip('/'),
                'source': ''.join(source).rstrip(),
                'coverage': coverage_list,
            })
        return ret
