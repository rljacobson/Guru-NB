import os, sys #, tempfile
from pkg_resources import resource_filename


############### Global Constants ###############
#This magic gets the Guru directory.
GURU_ROOT = os.path.split(resource_filename(__name__, ''))[0]
GURU_PORT = 8081
#This will eventually be set to a temporary directory.
GURU_NOTEBOOK_DIR = '/Users/rljacobson/Downloads/'+'.sagenb'
GURU_USERNAME = 'admin'
GURU_EMAIL = 'rljacobson@gmail.com'
GURU_ONLINE_DOCUMENTATION = 'http://www.sagemath.org/doc/index.html'

############### Paths and sagenb Constants ###############
lib_path = os.path.join(GURU_ROOT, "lib")
sys.path.append(lib_path)

import sagenb.misc.misc
sagenb.misc.misc.DOT_SAGENB = GURU_NOTEBOOK_DIR

############### Local Notebook ###############
from sagenb.notebook.notebook import Notebook

guru_notebook = Notebook(GURU_NOTEBOOK_DIR)
guru_notebook.user_manager().add_user(GURU_USERNAME, GURU_USERNAME, GURU_EMAIL,force=True)
guru_notebook.save() #Write out changes to disk. Unnecessary?

############### Cleanup, Utility Functions, etc. ###############

def cleanup():
    if guru_notebook is not None:
        guru_notebook.delete()


guru_server_thread = None
def startServerThread():
    global guru_server_thread
    global guru_notebook
    from threading import Thread
    from guru.RunFlask import startServer

    options = {'notebook_to_use':guru_notebook, 'open_browser': False, 'debug_mode': True}

    guru_server_thread = Thread(target=startServer, kwargs=options)
    #Setting guru_server_thread.daemon to False would keep Python from terminating as long
    #as the thread is executing.
    guru_server_thread.daemon = True
    guru_server_thread.start() #Why the eff is this blocking?!
