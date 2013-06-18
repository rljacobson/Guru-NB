#We don't use sagenb.notebook.run_notebook because we want the server in the same python environment as our app so we have access to the Notebook and Worksheet objects.


#########
# Flask #
#########
import os, random

from guru.globals import GURU_PORT, GURU_NOTEBOOK_DIR

import sagenb.notebook.notebook as notebook
from sagenb.misc.misc import find_next_available_port
import flask_server.base as flask_base

def startServer(notebook_to_use=None, open_browser=False, debug_mode=False):
    #notebook_directory = os.path.join(DOT_SAGENB, "sage_notebook.sagenb")

    #Setup the notebook.
    if notebook_to_use is None:
        #We assume the notebook is empty.
        notebook_to_use = notebook.load_notebook(notebook_directory)
        notebook_to_use.user_manager().add_user('admin', 'admin','rljacobson@gmail.com',force=True)
        notebook_to_use.save() #Write out changes to disk.

    notebook_directory = notebook_to_use._dir

    #Setup the flask app.
    opts={}
    opts['startup_token'] = '{0:x}'.format(random.randint(0, 2**128))
    startup_token = opts['startup_token']

    flask_base.notebook = notebook_to_use
    #create_app will now use notebook_to_use instead of the provided location.
    flask_app = flask_base.create_app(interface="localhost", port=8081,secure=False, **opts)

    sagenb_pid = os.path.join(notebook_directory, "sagenb.pid")
    with open(sagenb_pid, 'w') as pidfile:
        pidfile.write(str(os.getpid()))


    #What does this block even do?
    import logging
    logger=logging.getLogger('werkzeug')
    logger.setLevel(logging.WARNING)
    #logger.setLevel(logging.INFO) # to see page requests
    #logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    port = find_next_available_port('localhost', GURU_PORT)
    notebook_to_use.port = port

    #MAKE THIS HAPPEN IN flask_base: g.username = session['username'] = 'admin'


    if open_browser:
        from sagenb.misc.misc import open_page
        open_page('localhost', port, False, '/?startup_token=%s' % startup_token)

    try:
        if debug_mode:
            flask_app.run(host='localhost', port=port, threaded=True,
                      ssl_context=None, debug=True, use_reloader=False)
        else:
            flask_app.run(host='localhost', port=port, threaded=True,
                          ssl_context=None, debug=False)

    finally:
        #save_notebook(flask_base.notebook)
        os.unlink(sagenb_pid)

