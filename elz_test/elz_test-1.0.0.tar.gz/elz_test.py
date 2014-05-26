""" This elz_test module, support one print_lol function to print list.
    It's test codes for elz studying the Python.
    If you want to use it, thank you very much!"""


def print_lol(the_list,indent=False,level=0):
    """This function has three vars:
            the_list: the Python list, can be any list, even includes nested list.
            indent: print tab or not,
            level: the printed tab number."""
            
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                #for tab_stop in range(level):
                #    print('\t', end='')
                print("\t"*level, end='')
            print(each_item)
