from distutils.core import setup 
setup(name='pythonpinyin',
      version='0.11',
      description='a python project for getting pinyin for Chinese words or sentence',
      author='Small Qiao',
      author_email='dlutwy@qq.com',
      url='http://www.smallqiao.com',
      package_dir={'pythonpinyin':'pypinyin'},
      package_data={'pythonpinyin':['*.*']}
) 
