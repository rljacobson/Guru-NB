#Needs to:
#   Manage the notebook/worksheet object.
#   Communicate to the javascript in the WebView object.
#   Open and save .sws files.
#   Delete the internal notebook object on disk when done.

import os

try:
    # simplejson is faster, so try to import it first
    import simplejson as json
except ImportError:
    import json

from PySide.QtCore import (QObject, SIGNAL, Slot)

from sagenb.notebook.notebook import Notebook
from sagenb.notebook.misc import encode_response
from sagenb.misc.misc import (unicode_str, walltime)

from guru.globals import GURU_PORT, GURU_USERNAME, guru_notebook

worksheet_commands = {}

class WorksheetController(QObject):
    #Class variables
    notebook = guru_notebook
    worksheet_count = 0 #Reference counting.

    def __init__(self, webViewController):
        super(WorksheetController, self).__init__()

        WorksheetController.worksheet_count += 1

        self.webview_controller = webViewController

        #Set up the Python-javascript bridge.
        self.webFrame = self.webview_controller.webView().page().mainFrame()
        self.connect(self.webFrame, SIGNAL("javaScriptWindowObjectCleared()"), self.addJavascriptBridge)
        self.request_values = None

        self.isDirty = False
        self.cleanState = 0

        #Set up the local notebook and worksheet.
        #I need a better tmp directory.
        if guru_notebook is None:
            raise RuntimeError

        self.notebook_username = GURU_USERNAME
        self._worksheet = None

        self.init_updates()

    @staticmethod
    def withNewWorksheet(webViewController):
        wsc = WorksheetController(webViewController)
        wsc.setWorksheet(guru_notebook.create_new_worksheet('Untitled', wsc.notebook_username))
        wsc._worksheet._notebook = guru_notebook
        return wsc

    @staticmethod
    def withWorksheetFile(webViewController, filename):
        wsc = WorksheetController(webViewController)
        ws = wsc.notebook.import_worksheet(filename, wsc.notebook_username)
        wsc.setWorksheet(ws)
        wsc._worksheet._notebook = guru_notebook
        return wsc

    def setWorksheet(self, worksheet):
        #Check that the worksheet we were given has the notebook setup correctly.
        if (not hasattr(worksheet, "_notebook")) or (worksheet._notebook is None):
            worksheet._notebook = guru_notebook
        self._worksheet = worksheet

        #Handle the dirty status of the worksheet.
        self.isDirty = False
        self.cleanState = worksheet.state_number()

        #Open the worksheet in the webView
        self.webFrame.setUrl(self.worksheetUrl())

    def addJavascriptBridge(self):
        #This method is called whenever new content is loaded into the webFrame.
        #Each time this happens, we need to reconnect the Python-javascript bridge.
        self.webFrame.addToJavaScriptWindowObject("Guru", self)

    @Slot(str, str)
    def asyncRequest(self, url, postvars):
        #This is the counterpart to sagenb.async_request() in sagenb.js.
        #The original sagenb.async_request() made an ajax request. We can
        #significantly improve performance by calling this python method
        #directly and bypassing the Flask server.

        if self._worksheet is None:
            return

        if False:
            #Handle the command ourselves.

            #Log the request to the Ajax console.
            console_text = "url: %s\n" % url
            if postvars != "":
                #Log
                self.request_values = json.loads(postvars)
                console_text += ("decoded postvars: %s\n"%self.request_values)

            self.webview_controller.putAjaxConsole(console_text)

            #The url encodes the command. They look like:
            #   url = "/home/admin/0/worksheet_properties"
            command = url.split("/")[-1]
            result = worksheet_commands[command](self, self._worksheet)
            self.webview_controller.putAjaxConsole("result: " + result + "\n")
            javascript = "Guru.callback('success', '%s');" %  result
            self.webFrame.evaluateJavaScript(javascript)

        else:
            #Let the Sage Notebook Server handle the request as usual.

            javascript = "sagenb.guru_async_request(Guru.url, Guru.callback, Guru.postvars);"
            self.webFrame.evaluateJavaScript(javascript)

        #Check and see if the operation has made the worksheet dirty. If so, emit a "dirty" signal.
        if self._worksheet.state_number() > self.cleanState and self.isDirty == False:
            self.isDirty = True
            self.emit(SIGNAL("dirty(bool)"), True)

    @Slot(str)
    def putAjaxConsole(self, text):
        self.webview_controller.putAjaxConsole(text + "\n")

    def cleanup(self):
        #This method is called when this WorksheetController instance is about
        #to be eligible for garbage collection.
        WorksheetController.worksheet_count -= 1
        if self._worksheet is not None:
            #Now remove the worksheet.
            self._worksheet.quit()
            self._worksheet = None

    def saveWorksheet(self, file_name):
        #Write out the worksheet to filename whether it exists or not.
        if os.path.exists(file_name):
            os.remove(file_name) #This may be unnecessary.
        self.worksheet_download(self._worksheet, file_name)

        #The worksheet is no longer dirty.
        self.isDirty = False
        self.cleanState = self._worksheet.state_number()
        self.emit(SIGNAL("dirty(bool)"), False)

    def worksheetUrl(self):
        if self._worksheet is None:
            return ''
        #There is probably a better way to do this.
        url_vars = {'port' : GURU_PORT, 'username': GURU_USERNAME, 'idnum': self._worksheet.id_number()}
        url = "http://localhost:%(port)s/home/%(username)s/%(idnum)s/" % url_vars
        return url

    ########### FILE MENU WORKSHEET COMMANDS ###########

    def evaluateAll(self):
        javascript = "sagenb.worksheetapp.worksheet.evaluate_all()"
        self.webFrame.evaluateJavaScript(javascript)

    def interrupt(self):
        javascript = "sagenb.worksheetapp.worksheet.interrupt()"
        self.webFrame.evaluateJavaScript(javascript)

    def hideAllOutput(self):
        javascript = "sagenb.worksheetapp.worksheet.hide_all_output()"
        self.webFrame.evaluateJavaScript(javascript)

    def showAllOutput(self):
        javascript = "sagenb.worksheetapp.worksheet.show_all_output()"
        self.webFrame.evaluateJavaScript(javascript)

    def deleteAllOutput(self):
        javascript = "sagenb.worksheetapp.worksheet.delete_all_output()"
        self.webFrame.evaluateJavaScript(javascript)

    def restartWorksheet(self):
        javascript = "sagenb.worksheetapp.worksheet.restart_sage()"
        self.webFrame.evaluateJavaScript(javascript)

    def typesetOutput(self, enabled):
        #set_pretty_print takes a lowercase string.
        if enabled:
            self._worksheet.set_pretty_print('true')
        else:
            self._worksheet.set_pretty_print('false')

    ########### FLASK SERVER WORKSHEET COMMANDS ###########
    def worksheet_command(target):
        #This decorator registers the command as a command that the worksheet controller
        #knows how to handle.

        def decorator(f):
            #Register the worksheet command.
            worksheet_commands[target] = f
            #We will need to take care of commands with multiple arguments.
            def wrapper(*args, **kwds):
                return f(*args, **kwds)

            return wrapper

        return decorator
    
    def get_cell_id(self):
        """
        Returns the cell ID from the request.
    
        We cast the incoming cell ID to an integer, if it's possible.
        Otherwise, we treat it as a string.
        """
        try:
            return int(self.request_values['id'])
        except ValueError:
            return self.request_values['id']

    @worksheet_command('rename')
    def worksheet_rename(self, worksheet):
        worksheet.set_name(self.request_values['name'])
        return 'done'

    @worksheet_command('alive')
    def worksheet_alive(self, worksheet):
        return str(worksheet.state_number())

    @worksheet_command('system/<system>')
    def worksheet_system(self, worksheet, system):
        worksheet.set_system(system)
        return 'success'

    @worksheet_command('pretty_print/<enable>')
    def worksheet_pretty_print(self, worksheet, enable):
        worksheet.set_pretty_print(enable)
        return 'success'

    @worksheet_command('conf')
    def worksheet_conf(self, worksheet):
        return str(worksheet.conf())


    ########################################################
    # Save a worksheet
    ########################################################
    @worksheet_command('save')
    def worksheet_save(self, worksheet):
        """
        Save the contents of a worksheet after editing it in plain-text
        edit mode.
        """
        if 'button_save' in request.form:
            E = self.request_values['textfield']
            worksheet.edit_save(E)
            worksheet.record_edit(self.notebook_username)
        return redirect(url_for_worksheet(worksheet))

    @worksheet_command('save_snapshot')
    def worksheet_save_snapshot(self, worksheet):
        """Save a snapshot of a worksheet."""
        worksheet.save_snapshot(self.notebook_username)
        return 'saved'

    @worksheet_command('save_and_quit')
    def worksheet_save_and_quit(self, worksheet):
        """Save a snapshot of a worksheet then quit it. """
        worksheet.save_snapshot(self.notebook_username)
        worksheet.quit()
        return 'saved'

    #XXX: Redundant due to the above?
    @worksheet_command('save_and_close')
    def worksheet_save_and_close(self, worksheet):
        """Save a snapshot of a worksheet then quit it. """
        worksheet.save_snapshot(self.notebook_username)
        worksheet.quit()
        return 'saved'

    @worksheet_command('discard_and_quit')
    def worksheet_discard_and_quit(self, worksheet):
        """Quit the worksheet, discarding any changes."""
        worksheet.revert_to_last_saved_state()
        worksheet.quit()
        return 'saved' #XXX: Should this really be saved?

    @worksheet_command('revert_to_last_saved_state')
    def worksheet_revert_to_last_saved_state(self, worksheet):
        worksheet.revert_to_last_saved_state()
        return 'reverted'

    ########################################################
    # Worksheet properties
    ########################################################
    @worksheet_command('worksheet_properties')
    def worksheet_properties(self, worksheet):
        """
        Send worksheet properties as a JSON object
        """

        r = worksheet.basic()

        if worksheet.has_published_version():
            hostname = request.headers.get('host', self.notebook.interface + ':' + str(self.notebook.port))

            r['published_url'] = 'http%s://%s/home/%s' % ('' if not self.notebook.secure else 's',
                                                hostname,
                                                worksheet.published_version().filename())

        return encode_response(r)

    ########################################################
    # Used in refreshing the cell list
    ########################################################
    @worksheet_command('cell_properties')
    def worksheet_cell_properties(self, worksheet):
        """
        Return the cell with the given id as a JSON object
        """
        id = self.get_cell_id()
        return encode_response(worksheet.get_cell_with_id(id).basic())

    @worksheet_command('cell_list')
    def worksheet_cell_list(self, worksheet):
        """
        Return a list of cells in JSON format.
        """
        r = {}
        r['state_number'] = worksheet.state_number()
        r['cell_list'] = [c.basic() for c in worksheet.cell_list()]
        return encode_response(r)

    ########################################################
    # Set output type of a cell
    ########################################################
    @worksheet_command('set_cell_output_type')
    def worksheet_set_cell_output_type(self, worksheet):
        """
        Set the output type of the cell.

        This enables the type of output cell, such as to allowing wrapping
        for output that is very long.
        """
        id = self.get_cell_id()
        type = self.request_values['type']
        worksheet.get_cell_with_id(id).set_cell_output_type(type)
        return ''

    ########################################################
    #Cell creation
    ########################################################
    @worksheet_command('new_cell_before')
    def worksheet_new_cell_before(self, worksheet):
        """Add a new cell before a given cell."""
        r = {}
        r['id'] =  id = self.get_cell_id()
        input = unicode_str(self.request_values.get('input', ''))
        cell = worksheet.new_cell_before(id, input=input)
        worksheet.increase_state_number()

        r['new_id'] = cell.id()
        #r['new_html'] = cell.html(div_wrap=False)

        return encode_response(r)

    @worksheet_command('new_text_cell_before')
    def worksheet_new_text_cell_before(self, worksheet):
        """Add a new text cell before a given cell."""
        r = {}
        r['id'] = id = self.get_cell_id()
        input = unicode_str(self.request_values.get('input', ''))
        cell = worksheet.new_text_cell_before(id, input=input)
        worksheet.increase_state_number()

        r['new_id'] = cell.id()
        #r['new_html'] = cell.html(editing=True)

        # XXX: Does editing correspond to TinyMCE?  If so, we should try
        # to centralize that code.
        return encode_response(r)


    @worksheet_command('new_cell_after')
    def worksheet_new_cell_after(self, worksheet):
        """Add a new cell after a given cell."""
        r = {}
        r['id'] = id = self.get_cell_id()
        input = unicode_str(self.request_values.get('input', ''))
        cell = worksheet.new_cell_after(id, input=input)
        worksheet.increase_state_number()

        r['new_id'] = cell.id()
        #r['new_html'] = cell.html(div_wrap=True)

        return encode_response(r)

    @worksheet_command('new_text_cell_after')
    def worksheet_new_text_cell_after(self, worksheet):
        """Add a new text cell after a given cell."""
        r = {}
        r['id'] = id = self.get_cell_id()
        input = unicode_str(self.request_values.get('input', ''))
        cell = worksheet.new_text_cell_after(id, input=input)
        worksheet.increase_state_number()

        r['new_id'] = cell.id()
        #r['new_html'] = cell.html(editing=True)

        # XXX: Does editing correspond to TinyMCE?  If so, we should try
        # to centralize that code.
        return encode_response(r)

    ########################################################
    # Cell deletion
    ########################################################
    @worksheet_command('delete_cell')
    def worksheet_delete_cell(self, worksheet):
        """
        Deletes a worksheet cell, unless there's only one compute cell
        left.  This allows functions which evaluate relative to existing
        cells, e.g., inserting a new cell, to continue to work.
        """
        r = {}
        r['id'] = id = self.get_cell_id()
        if len(worksheet.compute_cell_id_list()) <= 1:
            r['command'] = 'ignore'
        else:
            prev_id = worksheet.delete_cell_with_id(id)
            r['command'] = 'delete'
            r['prev_id'] = worksheet.delete_cell_with_id(id)
            r['cell_id_list'] = worksheet.cell_id_list()

        return encode_response(r)

    @worksheet_command('delete_cell_output')
    def worksheet_delete_cell_output(self, worksheet):
        """Delete's a cell's output."""
        r = {}
        r['id'] = id = self.get_cell_id()
        worksheet.get_cell_with_id(id).delete_output()
        r['command'] = 'delete_output'

        return encode_response(r)

    ########################################################
    # Evaluation and cell update
    ########################################################
    @worksheet_command('eval')
    def worksheet_eval(self, worksheet):
        """
        Evaluate a worksheet cell.

        If the request is not authorized (the requester did not enter the
        correct password for the given worksheet), then the request to
        evaluate or introspect the cell is ignored.

        If the cell contains either 1 or 2 question marks at the end (not
        on a comment line), then this is interpreted as a request for
        either introspection to the documentation of the function, or the
        documentation of the function and the source code of the function
        respectively.
        """

        r = {}

        r['id'] = id = self.get_cell_id()
        cell = worksheet.get_cell_with_id(id)
        public = worksheet.tags().get('_pub_', [False])[0] #this is set in pub_worksheet

        if public and not cell.is_interactive_cell():
            r['command'] = 'error'
            r['message'] = 'Cannot evaluate non-interactive public cell with ID %r.' % id
            return encode_response(r)

        worksheet.increase_state_number()

        if public:
            # Make public input cells read-only.
            input_text = cell.input_text()
        else:
            input_text = unicode_str(self.request_values.get('input', '')).replace('\r\n', '\n') #DOS

        # Handle an updated / recomputed interact.  TODO: JSON encode
        # the update data.
        if 'interact' in self.request_values:
            r['interact'] = 1
            input_text = INTERACT_UPDATE_PREFIX
            variable = self.request_values.get('variable', '')
            if variable!='':
                adapt_number = int(self.request_values.get('adapt_number', -1))
                value = self.request_values.get('value', '')
                input_text += "\n_interact_.update('%s', '%s', %s, _interact_.standard_b64decode('%s'), globals())" % (id, variable, adapt_number, value)

            if int(self.request_values.get('recompute', 0)):
                input_text += "\n_interact_.recompute('%s')" % id

        cell.set_input_text(input_text)

        if int(self.request_values.get('save_only', '0')):
            self.notebook_updates()
            return encode_response(r)
        elif int(self.request_values.get('text_only', '0')):
            self.notebook_updates()
            r['cell_html'] = cell.html()
            return encode_response(r)

        cell.evaluate(username=self.notebook_username)

        new_cell = int(self.request_values.get('newcell', 0)) #whether to insert a new cell or not
        if new_cell:
            new_cell = worksheet.new_cell_after(id)
            r['command'] = 'insert_cell'
            r['new_cell_id'] = new_cell.id()
            r['new_cell_html'] = new_cell.html(div_wrap=False)
        else:
            r['next_id'] = cell.next_compute_id()

        self.notebook_updates()

        return encode_response(r)

    @worksheet_command('cell_update')
    def worksheet_cell_update(self, worksheet):
        import time

        r = {}
        r['id'] = id = self.get_cell_id()

        # update the computation one "step".
        worksheet.check_comp()

        # now get latest status on our cell
        r['status'], cell = worksheet.check_cell(id)

        if r['status'] == 'd':
            r['new_input'] = cell.changed_input_text()
            r['output_html'] = cell.output_html()

            # Update the log.
            t = time.strftime('%Y-%m-%d at %H:%M',
                              time.localtime(time.time()))
            H = "Worksheet '%s' (%s)\n" % (worksheet.name(), t)
            H += cell.edit_text(ncols=self.notebook.HISTORY_NCOLS, prompts=False,
                                max_out=self.notebook.HISTORY_MAX_OUTPUT)
            self.notebook.add_to_user_history(H, self.notebook_username)
        else:
            r['new_input'] = ''
            r['output_html'] = ''

        r['interrupted'] = cell.interrupted()
        if 'Unhandled SIGSEGV' in cell.output_text(raw=True).split('\n'):
            r['interrupted'] = 'restart'
            print 'Segmentation fault detected in output!'

        r['output'] = cell.output_text(html=True)
        r['output_wrapped'] = cell.output_text(self.notebook.conf()['word_wrap_cols'])
        r['introspect_output'] = cell.introspect_output()

        # Compute 'em, if we got 'em.
        worksheet.start_next_comp()
        return encode_response(r)

    ########################################################
    # Cell introspection
    ########################################################
    @worksheet_command('introspect')
    def worksheet_introspect(self, worksheet):
        """
        Cell introspection. This is called when the user presses the tab
        key in the browser in order to introspect.
        """
        r = {}
        r['id'] = id = self.get_cell_id()

        if worksheet.tags().get('_pub_', [False])[0]: #tags set in pub_worksheet
            r['command'] = 'error'
            r['message'] = 'Cannot evaluate public cell introspection.'
            return encode_response(r)

        before_cursor = self.request_values.get('before_cursor', '')
        after_cursor = self.request_values.get('after_cursor', '')
        cell = worksheet.get_cell_with_id(id)
        cell.evaluate(introspect=[before_cursor, after_cursor])

        r['command'] = 'introspect'
        return encode_response(r)

    ########################################################
    # Edit the entire worksheet
    ########################################################
    @worksheet_command('edit')
    def worksheet_edit(self, worksheet):
        """
        Return a window that allows the user to edit the text of the
        worksheet with the given filename.
        """
        return render_template(os.path.join("html", "worksheet_edit.html"),
                               worksheet = worksheet,
                               username = self.notebook_username)

    ########################################################
    # Plain text log view of worksheet
    ########################################################
    @worksheet_command('text')
    def worksheet_text(self, worksheet):
        """
        Return a window that allows the user to edit the text of the
        worksheet with the given filename.
        """
        from cgi import escape
        plain_text = worksheet.plain_text(prompts=True, banner=False)
        plain_text = escape(plain_text).strip()

        return render_template(os.path.join("html", "worksheet_text.html"),
                               username = self.notebook_username,
                               plain_text = plain_text)

    ########################################################
    # Copy a worksheet
    ########################################################
    @worksheet_command('copy')
    def worksheet_copy(self, worksheet):
        copy = self.notebook.copy_worksheet(worksheet, self.notebook_username)
        if 'no_load' in self.request_values:
            return ''
        else:
            return redirect(url_for_worksheet(copy))

    ########################################################
    # Get a copy of a published worksheet and start editing it
    ########################################################
    @worksheet_command('edit_published_page')
    def worksheet_edit_published_page(self, worksheet):
        ## if user_type(self.username) == 'guest':
        ##     return current_app.message('You must <a href="/">login first</a> in order to edit this worksheet.')

        ws = worksheet.worksheet_that_was_published()
        if ws.owner() == self.notebook_username:
            W = ws
        else:
            W = self.notebook.copy_worksheet(worksheet, self.notebook_username)
            W.set_name(worksheet.name())

        return redirect(url_for_worksheet(W))


    ########################################################
    # Collaborate with others
    ########################################################
    @worksheet_command('invite_collab')
    def worksheet_invite_collab(self, worksheet):
        owner = worksheet.owner()
        id_number = worksheet.id_number()
        old_collaborators = set(worksheet.collaborators())
        collaborators = set([u.strip() for u in self.request_values.get('collaborators', '').split(',') if u!=owner])
        if len(collaborators-old_collaborators)>500:
            # to prevent abuse, you can't add more than 500 collaborators at a time
            return current_app.message(_("Error: can't add more than 500 collaborators at a time"), cont=url_for_worksheet(worksheet))
        worksheet.set_collaborators(collaborators)
        user_manager = self.notebook.user_manager()
        # add worksheet to new collaborators
        for u in collaborators-old_collaborators:
            try:
                user_manager.user(u).viewable_worksheets().add((owner, id_number))
            except KeyError:
                # user doesn't exist
                pass
        # remove worksheet from ex-collaborators
        for u in old_collaborators-collaborators:
            try:
                user_manager.user(u).viewable_worksheets().discard((owner, id_number))
            except KeyError:
                # user doesn't exist
                pass

        return ''

    ########################################################
    # Revisions
    ########################################################
    # TODO take out or implement
    @worksheet_command('revisions')
    def worksheet_revisions(self, worksheet):
        """
        Show a list of revisions of this worksheet.
        """
        if 'action' not in self.request_values:
            if 'rev' in self.request_values:
                return self.notebook.html_specific_revision(self.notebook_username, worksheet,
                                                           self.request_values['rev'])
            else:
                return self.notebook.html_worksheet_revision_list(self.notebook_username, worksheet)
        else:
            rev = self.request_values['rev']
            action = self.request_values['action']
            if action == 'revert':
                import bz2
                worksheet.save_snapshot(self.notebook_username)
                #XXX: Requires access to filesystem
                txt = bz2.decompress(open(worksheet.get_snapshot_text_filename(rev)).read())
                worksheet.delete_cells_directory()
                worksheet.edit_save(txt)
                return redirect(url_for_worksheet(worksheet))
            elif action == 'publish':
                import bz2
                W = self.notebook.publish_worksheet(worksheet, self.notebook_username)
                txt = bz2.decompress(open(worksheet.get_snapshot_text_filename(rev)).read())
                W.delete_cells_directory()
                W.edit_save(txt)
                return redirect(url_for_worksheet(W))
            else:
                return current_app.message(_('Error'))

    ########################################################
    # Cell directories
    ########################################################
    @worksheet_command('cells/<path:filename>')
    def worksheet_cells(self, worksheet, filename):
        #XXX: This requires that the worker filesystem be accessible from
        #the server.
        from flask.helpers import send_from_directory
        return send_from_directory(worksheet.cells_directory(), filename)


    ##############################################
    # Data
    ##############################################
    @worksheet_command('data/<path:filename>')
    def worksheed_data_folder(self, worksheet, filename):
        dir = os.path.abspath(worksheet.data_directory())
        if not os.path.exists(dir):
            return make_response(_('No data file'), 404)
        else:
            from flask.helpers import send_from_directory
            return send_from_directory(worksheet.data_directory(), filename)

    @worksheet_command('delete_datafile')
    def worksheet_delete_datafile(self, worksheet):
        dir = os.path.abspath(worksheet.data_directory())
        filename = self.request_values['name']
        path = os.path.join(dir, filename)
        os.unlink(path)
        return ''

    @worksheet_command('edit_datafile/<path:filename>')
    def worksheet_edit_datafile(self, worksheet, filename):
        ext = os.path.splitext(filename)[1].lower()
        file_is_image, file_is_text = False, False
        text_file_content = ""

        path = "/home/%s/data/%s" % (worksheet.filename(), filename)

        if ext in ['.png', '.jpg', '.gif']:
            file_is_image = True
        if ext in ['.txt', '.tex', '.sage', '.spyx', '.py', '.f', '.f90', '.c']:
            file_is_text = True
            text_file_content = open(os.path.join(worksheet.data_directory(), filename)).read()

        return render_template(os.path.join("html", "datafile_edit.html"),
                               worksheet = worksheet,
                               username = self.notebook_username,
                               filename_ = filename,
                               file_is_image = file_is_image,
                               file_is_text = file_is_text,
                               text_file_content = text_file_content,
                               path = path)

    @worksheet_command('save_datafile')
    def worksheet_save_datafile(self, worksheet):
        filename = self.request_values['filename']
        if 'button_save' in self.request_values:
            text_field = self.request_values['textfield']
            dest = os.path.join(worksheet.data_directory(), filename) #XXX: Requires access to filesystem
            if os.path.exists(dest):
                os.unlink(dest)
            open(dest, 'w').write(text_field)

        print 'saving datafile, redirect'
        return redirect(url_for_worksheet(worksheet))

    # @worksheet_command('link_datafile')
    # def worksheet_link_datafile(self, worksheet):
    #     target_worksheet_filename = self.request_values['target']
    #     data_filename = self.request_values['filename']
    #     src = os.path.abspath(os.path.join(
    #         worksheet.data_directory(), data_filename))
    #     target_ws =  self.notebook.get_worksheet_with_filename(target_worksheet_filename)
    #     target = os.path.abspath(os.path.join(
    #         target_ws.data_directory(), data_filename))
    #     if target_ws.owner() != self.notebook_username and not target_ws.is_collaborator(self.notebook_username):
    #         return current_app.message(_("illegal link attempt!"), worksheet_datafile.url_for(worksheet, name=data_filename))
    #     if os.path.exists(target):
    #         return current_app.message(_("The data filename already exists in other worksheet\nDelete the file in the other worksheet before creating a link."), worksheet_datafile.url_for(worksheet, name=data_filename))
    #     os.link(src,target)
    #     return redirect(worksheet_datafile.url_for(worksheet, name=data_filename))
    #     #return redirect(url_for_worksheet(target_ws) + '/datafile?name=%s'%data_filename) #XXX: Can we not hardcode this?

    @worksheet_command('upload_datafile')
    def worksheet_upload_datafile(self, worksheet):
        from werkzeug.utils import secure_filename

        file = request.files['file']
        name = self.request_values.get('name', '').strip() or file.filename
        name = secure_filename(name)

        #XXX: disk access
        dest = os.path.join(worksheet.data_directory(), name)
        if os.path.exists(dest):
            if not os.path.isfile(dest):
                return _('Suspicious filename encountered uploading file.')
            os.unlink(dest)

        file.save(dest)
        return ''

    @worksheet_command('datafile_from_url')
    def worksheet_datafile_from_url(self, worksheet):
        from werkzeug.utils import secure_filename

        name = self.request_values.get('name', '').strip()
        url = self.request_values.get('url', '').strip()
        if url and not name:
            name = url.split('/')[-1]
        name = secure_filename(name)

        import urllib2
        from urlparse import urlparse
        # we normalize the url by parsing it first
        parsedurl = urlparse(url)
        if not parsedurl[0] in ('http','https','ftp'):
            return _('URL must start with http, https, or ftp.')
        download = urllib2.urlopen(parsedurl.geturl())

        dest = os.path.join(worksheet.data_directory(), name)
        if os.path.exists(dest):
            if not os.path.isfile(dest):
                return _('Suspicious filename encountered uploading file.')
            os.unlink(dest)

        import re
        matches = re.match("file://(?:localhost)?(/.+)", url)
        if matches:
            f = file(dest, 'wb')
            f.write(open(matches.group(1)).read())
            f.close()
            return ''

        with open(dest, 'w') as f:
            f.write(download.read())
        return ''

    @worksheet_command('new_datafile')
    def worksheet_new_datafile(self, worksheet):
        from werkzeug.utils import secure_filename

        name = self.request_values.get('new', '').strip()
        name = secure_filename(name)

        #XXX: disk access
        dest = os.path.join(worksheet.data_directory(), name)
        if os.path.exists(dest):
            if not os.path.isfile(dest):
                return _('Suspicious filename encountered uploading file.')
            os.unlink(dest)

        open(dest, 'w').close()
        return ''

    ################################
    #Publishing
    ################################
    @worksheet_command('publish')
    def worksheet_publish(self, worksheet):
        """
        This provides a frontend to the management of worksheet
        publication. This management functionality includes
        initializational of publication, re-publication, automated
        publication when a worksheet saved, and ending of publication.
        """
        if 'publish_on' in self.request_values:
            self.notebook.publish_worksheet(worksheet, self.notebook_username)
        if 'publish_off' in self.request_values and worksheet.has_published_version():
            self.notebook.delete_worksheet(worksheet.published_version().filename())

        if 'auto_on' in self.request_values:
            worksheet.set_auto_publish(True)
        if 'auto_off' in self.request_values:
            worksheet.set_auto_publish(False)
        if 'is_auto' in self.request_values:
            return str(worksheet.is_auto_publish())

        if 'republish' in self.request_values:
            self.notebook.publish_worksheet(worksheet, self.notebook_username)

        return ''

    ############################################
    # Ratings
    ############################################
    # @worksheet_command('rating_info')
    # def worksheet_rating_info(worksheet):
    #     return worksheet.html_ratings_info()

    # @worksheet_command('rate')
    # def worksheet_rate(worksheet):
    #     ## if user_type(self.username) == "guest":
    #     ##     return HTMLResponse(stream = message(
    #     ##         'You must <a href="/">login first</a> in order to rate this worksheet.', ret))

    #     rating = int(self.request_values['rating'])
    #     if rating < 0 or rating >= 5:
    #         return current_app.messge("Gees -- You can't fool the rating system that easily!",
    #                           url_for_worksheet(worksheet))

    #     comment = self.request_values['comment']
    #     worksheet.rate(rating, comment, self.notebook_username)
    #     s = """
    #     Thank you for rating the worksheet <b><i>%s</i></b>!
    #     You can <a href="rating_info">see all ratings of this worksheet.</a>
    #     """%(worksheet.name())
    #     #XXX: Hardcoded url
    #     return current_app.message(s.strip(), '/pub/', title=u'Rating Accepted')


    ########################################################
    # Downloading, moving around, renaming, etc.
    ########################################################
    @worksheet_command('download/<path:title>')
    def worksheet_download(self, worksheet, filename):
        try:
            #XXX: Accessing the hard disk.
            self.notebook.export_worksheet(worksheet.filename(), filename)
        except KeyError:
            print 'No such worksheet.'


    @worksheet_command('restart_sage')
    def worksheet_restart_sage(self, worksheet):
        #XXX: TODO -- this must not block long (!)
        worksheet.restart_sage()
        return 'done'

    @worksheet_command('quit_sage')
    def worksheet_quit_sage(self, worksheet):
        #XXX: TODO -- this must not block long (!)
        worksheet.quit()
        return 'done'

    @worksheet_command('interrupt')
    def worksheet_interrupt(self, worksheet):
        #XXX: TODO -- this must not block long (!)
        worksheet.sage().interrupt()
        return 'failed' if worksheet.sage().is_computing() else 'success'

    @worksheet_command('hide_all')
    def worksheet_hide_all(self, worksheet):
        worksheet.hide_all()
        return 'success'

    @worksheet_command('show_all')
    def worksheet_show_all(self, worksheet):
        worksheet.show_all()
        return 'success'

    @worksheet_command('delete_all_output')
    def worksheet_delete_all_output(self, worksheet):
        try:
            worksheet.delete_all_output(self.notebook_username)
        except ValueError:
            return 'fail'
        else:
            return 'success'

    @worksheet_command('print')
    def worksheet_print(self, worksheet):
        #XXX: We might want to separate the printing template from the
        #regular html template.
        return self.notebook.html(worksheet.filename(), do_print=True)


    #######################################################
    # Jmol Popup
    #######################################################
    #@ws.route('/home/<username>/<id>/jmol_popup.html', methods=['GET'])
    #@login_required
    def jmol_popup(username, id):
        return render_template(os.path.join('html', 'jmol_popup.html'))

    ############################
    # Notebook autosave.
    ############################
    # save if make a change to notebook and at least some seconds have elapsed since last save.
    def init_updates(self):
        self.save_interval = self.notebook.conf()['save_interval']
        self.idle_interval = self.notebook.conf()['idle_check_interval']
        self.last_save_time = walltime()
        self.last_idle_time = walltime()

    def notebook_save_check(self):
        t = walltime()
        if t > self.last_save_time + self.save_interval:
            with global_lock:
                # if someone got the lock before we did, they might have saved,
                # so we check against the last_save_time again
                # we don't put the global_lock around the outer loop since we don't need
                # it unless we are actually thinking about saving.
                if t > self.last_save_time + self.save_interval:
                    self.notebook.save()
                    self.last_save_time = t

    def notebook_idle_check(self):
        t = walltime()

        if t > self.last_idle_time + self.idle_interval:
            if t > self.last_idle_time + self.idle_interval:
                self.notebook.update_worksheet_processes()
                self.notebook.quit_idle_worksheet_processes()
                self.last_idle_time = t

    def notebook_updates(self):
        self.notebook_save_check()
        self.notebook_idle_check()