import os, sys

tmp = os.path.dirname(sys.argv[0])

#print "os.path.dirname: %s" % tmp
print "os.path.abspath: %s" % os.path.abspath(tmp)

from pkg_resources import resource_filename

print os.path.split(resource_filename(__name__, ''))[0]

from sagenb.misc.misc import (SAGENB_ROOT, DOT_SAGENB, SAGENB_VERSION, SAGE_VERSION)

foo = ("SAGENB_ROOT", "DOT_SAGENB", "SAGENB_VERSION", "SAGE_VERSION")
bar = (SAGENB_ROOT, DOT_SAGENB, SAGENB_VERSION, SAGE_VERSION)
foobar = zip(foo, bar)
for thing in foobar:
    print "%s: %s" % (thing[0], thing[1])