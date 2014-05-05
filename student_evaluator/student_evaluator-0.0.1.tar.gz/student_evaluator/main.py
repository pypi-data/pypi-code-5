"""
    Student Evaluator
    Copyright 2014, Jeroen Doggen, jeroendoggen@gmail.com
"""

import sys

from evaluator import StudentEvaluator


def run():
    """Run the main program"""
    evaluator = StudentEvaluator()
    #assignment_analyser.init()
    evaluator.run()
    return(evaluator.exit_value())


if __name__ == "__main__":
    sys.exit(run())
