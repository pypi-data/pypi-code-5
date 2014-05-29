
"""
No Comment!

"""
import os


def recursivep(itemlist):
    for item in itemlist:
        if isinstance(item, list):
            recursivep(item)
        else:
            print(item)


morebook = ["MORE!", "MORE!!!!"]
sub_book = ["CCCC", "QQ", morebook]
book = ["aa", "bb", "haha", sub_book]
book.insert(1,"10")
print(book)


for item in book:
    if isinstance(item, list):
        for eachitem in item:
            print(eachitem)
    else:
        print(item)

recursivep(book)







