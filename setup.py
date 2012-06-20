import sys
from distutils.core import setup
import py2exe
from distutils.core import setup
import py2exe
import matplotlib

MyData_Files = ['config.cfg','TABOB.TXT']


setup(windows=[{"script":"at.py","icon_resources":[(1,"star.ico")]}],
      options={"py2exe":{"includes" : ["matplotlib.backends.backend_tkagg"],"excludes":["_gtkagg"]}},
      data_files = MyData_Files+matplotlib.get_py2exe_datafiles()
     )
