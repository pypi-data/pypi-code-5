movies = ["aa","bb","cc",["dd","ee",["ff"]]]
def c(alist):
    for each_item in alist:
        if isinstance(each_item,list):
            c(each_item)
        else:
            print(each_item)

