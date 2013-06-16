import sys, os
from guru.globals import GURU_ROOT

lib_path = os.path.join(GURU_ROOT, "lib")
sys.path.append(lib_path)

import sagenb.misc.misc
sagenb.misc.misc.DOT_SAGENB = "/Users/rljacobson/Downloads/.sagenb"

from sagenb.notebook.run_notebook import notebook_run

#Passing fork=True runs the server in its own process.
notebook_run(server="flask", port=8081, fork=True)