import sys

sys.path.append("/Users/rljacobson/Documents/development/Guru/lib")

import time #For sleeping.


#from sagenb.notebook.worksheet import Worksheet

from sagenb.notebook.notebook import Notebook
nb = Notebook('/Users/rljacobson/Downloads/'+'.sagenb')

import sagenb.notebook.misc
#sagenb.notebook.misc.notebook = nb
nb.user_manager().add_user('robert','robert','rljacobson@gmail.com',force=True)
W = nb.create_new_worksheet('Test Notebook Title', 'robert')
W._notebook = nb
#C = W.new_cell_after(-1, '3+9') #why doesn't this work?
C = sagenb.notebook.cell.Cell(0, '3+8', '', W)
print "Sage initialized?: %s" % W.sage().is_started()
#print "Sage init output:\n %s" % W.sage().output_status().output
C.evaluate()

#Wait until the sage process finishes computing the thingy.
while W.check_comp()[0]=='w':
    print "Computing..."
    time.sleep(1)

print C
#print "Cell evaluated? %s" % C.evaluated()
#print C.input_text()
#print C.output_text()

W.quit()
nb.delete()



