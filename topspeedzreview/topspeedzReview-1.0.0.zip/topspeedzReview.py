def print_list(aList):
    for each_item in aList:
        if isinstance(each_item, list):
            print_list(each_item)
        else:
            print(each_item)
