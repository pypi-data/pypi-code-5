'''
Created on Dec 3, 2013

@author: karthicm
'''

global TESTSUITE_DIRECTORY
global TESTSUITE_NAMES
global TESTCASE_NAMES
global TAGS_TO_INCLUDE
global CRITICAL_TEST_TAGS
global NON_CRITICAL_TEST_TAGS

TESTSUITE_DIRECTORY = ""
TESTSUITE_NAMES = []
TESTCASE_NAMES = []
TAGS_TO_INCLUDE = []
TAGS_TO_EXCLUDE = []
CRITICAL_TEST_TAGS = []
NON_CRITICAL_TEST_TAGS = []

#config_path = 'C:\SAF\Run'

def set_configdata(config_path):
    actual_config = config_path + '\saf_test_executor_config.txt'
    config_file = open(actual_config,'r')
    config_metadata = config_file.readlines()
    for config in config_metadata:
        #print config
        configdata = str(config).split('|')
        config_variable = str(configdata[0]).strip()
        config_value = str(configdata[1]).strip()
        if config_variable == 'TESTSUITE_DIRECTORY':
            global TESTSUITE_DIRECTORY
            if not config_value == '':
                TESTSUITE_DIRECTORY = config_value
 
        elif config_variable == 'TESTSUITE_NAMES':
            global TESTSUITE_NAMES
            if not config_value == '':
                config_values = config_value.split('#')
                for values in config_values:
                    TESTSUITE_NAMES.append(values)

        elif config_variable == 'TESTCASE_NAMES':
            global TESTCASE_NAMES
            if not config_value == '':
                config_values = config_value.split('#')
                for values in config_values:
                    TESTCASE_NAMES.append(values)

        elif config_variable == 'TAGS_TO_INCLUDE':
            global TAGS_TO_INCLUDE
            if not config_value == '':
                config_values = config_value.split('#')
                for values in config_values:
                    TAGS_TO_INCLUDE.append(values)

        elif config_variable == 'TAGS_TO_EXCLUDE':
            global TAGS_TO_EXCLUDE
            if not config_value == '':
                config_values = config_value.split('#')
                for values in config_values:
                    TAGS_TO_EXCLUDE.append(values)
                            
        elif config_variable == 'CRITICAL_TEST_TAGS':
            global CRITICAL_TEST_TAGS
            if not config_value == '':
                config_values = config_value.split('#')
                for values in config_values:
                    CRITICAL_TEST_TAGS.append(values)
        
        elif config_variable == 'NON_CRITICAL_TEST_TAGS':
            global NON_CRITICAL_TEST_TAGS
            if not config_value == '':
                config_values = config_value.split('#')
                for values in config_values:
                    NON_CRITICAL_TEST_TAGS.append(values)