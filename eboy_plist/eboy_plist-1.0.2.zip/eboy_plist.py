""" 只是个循环列表的接口 """
def print_list(this_List,tabNum):
    """ 只是个循环列表的接口 """
    for movie in this_List:
        if isinstance(movie,list) :
           print_list(movie,tabNum+1)
        else:
           for num in range(tabNum):
               print('\t',end='')
           print(movie)
print('_________________________')
