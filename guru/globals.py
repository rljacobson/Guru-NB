import sys, os
from pkg_resources import resource_filename

#This magic gets the Guru directory.
GURU_ROOT = os.path.split(resource_filename(__name__, ''))[0]
