import re

from marathoner.commands.base import BaseCommand


class Command(BaseCommand):
    syntax = '<seed> [vis params]'
    help = 'run single test with visualization'

    cmd_re = re.compile(r'^\s*(\d+)\s*([^\d\s].*)?\s*$')
    def is_match(self, command):
        return self.cmd_re.match(command)

    def handle(self, command):
        match = self.cmd_re.match(command)
        seed = int(match.group(1))
        vis_params = match.group(2) or ''

        self.contest.single_test_starting(seed)
        visualizer_stdout, solution_stderr = self.executor.run(seed, True, vis_params)
        best_score = self.project.scores[seed]
        current_score = self.contest.extract_score(seed, visualizer_stdout, solution_stderr)
        self.project.scores[seed] = current_score
        self.project.scores.save()
        self.contest.single_test_ending(seed, visualizer_stdout, solution_stderr, best_score, current_score)
