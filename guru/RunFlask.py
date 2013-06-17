#We don't use sagenb.notebook.run_notebook because we want the server in the same python environment as our app so we have access to the Notebook and Worksheet objects.


#########
# Flask #
#########
import os, random

from guru.globals import GURU_PORT

from sagenb.misc.misc import (DOT_SAGENB, find_next_available_port)
import flask_server.base as flask_base

def startServer():
    opts={}
    opts['startup_token'] = '{0:x}'.format(random.randint(0, 2**128))
    startup_token = opts['startup_token']

    notebook_directory = os.path.join(DOT_SAGENB, "sage_notebook.sagenb")

    flask_app = flask_base.create_app(notebook_directory, interface="localhost", port=8081,secure=False, **opts)


    def save_notebook(notebook):
        print "Quitting all running worksheets..."
        notebook.quit()
        print "Saving notebook..."
        notebook.save()
        print "Notebook cleanly saved."

    sagenb_pid = os.path.join(notebook_directory, "sagenb.pid")

    with open(sagenb_pid, 'w') as pidfile:
        pidfile.write(str(os.getpid()))


    import logging
    logger=logging.getLogger('werkzeug')
    logger.setLevel(logging.WARNING)
    #logger.setLevel(logging.INFO) # to see page requests
    #logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    port = find_next_available_port('localhost', GURU_PORT)

    from sagenb.misc.misc import open_page; open_page('localhost', 8081, False, '/?startup_token=%s' % startup_token)
    try:
        flask_app.run(host='localhost', port=port, threaded=True,
                      ssl_context=None, debug=False)
    finally:
        save_notebook(flask_base.notebook)
        os.unlink(sagenb_pid)
