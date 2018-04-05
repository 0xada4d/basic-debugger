from distutils.core import setup
import py2exe

# For python2, we need `pip install py2exe_py2`
# Run: python setup.py py2exe

setup(
    options = {'py2exe': {'bundle_files': 1}},
    service = ['vulnservice'],
    zipfile = None,
)

# Another usage example
# Just make sure all of your created python files are in the same folder as setup.py
# For instance, the below .exe needs my_debugger_defines.py, backdoor.py to be in same directory
# Run: python setup.py py2exe
#
# # Backdoor builder
# from distutils.core import setup
# import py2exe
#
# setup(console=['backdoor.py'],
#       options = {'py2exe':{'bundle_files':1}},
#       zipfile = None,
#       )