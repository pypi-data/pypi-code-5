from robot import run
import lib_Operations_Common
import saf_test_constants
import os

path = os.path.dirname(saf_test_constants.__file__)
parent_runpath = os.path.abspath(os.path.join(path,os.pardir))
#print path
#runpath = "C:\SAF\Run"
runpath = parent_runpath + '\Run'
UserVariableFile = runpath + "\TestExecutionVariables.py"

saf_test_constants.set_configdata(runpath)

outputdirectory = lib_Operations_Common.get_current_result_directory()
run(saf_test_constants.TESTSUITE_DIRECTORY, suite =saf_test_constants.TESTSUITE_NAMES,test =saf_test_constants.TESTCASE_NAMES, outputdir= outputdirectory, include = saf_test_constants.TAGS_TO_INCLUDE,exclude= saf_test_constants.TAGS_TO_EXCLUDE,critical = saf_test_constants.CRITICAL_TEST_TAGS,noncritical =saf_test_constants.NON_CRITICAL_TEST_TAGS, variablefile =UserVariableFile )