"""This function will be used as an example"""

titles=["title0","title1","title2","title3",["nesteditem0",["subnest0","subnest1"]]]
y=["2000","2001","2002","2003","2004","2005"]

titles.insert(1,y[0])
titles.insert(3,y[1])
titles.insert(5,y[2])
titles.insert(7,y[3])
titles.insert(9,y[4])

   
def print_lol(the_list):
  for each_item in the_list:
    if isinstance(each_item,list):
      print_lol(each_item)
      
    else:
      print (each_item)
      
     