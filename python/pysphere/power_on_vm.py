#!/usr/bin/env python
from pysphere import VIServer, VITask
from optparse import OptionParser
from getpass import getpass

# Parameters
usage = "usage: %prop [options]"
parser = OptionParser(usage=usage)
parser.add_option("-s", "--server", dest="vcenter",
    help="set the vCenter server to connect to")
parser.add_option("-u", "--user", dest="username",
    help="set the user to connect as")
parser.add_option("-p", "--password", dest="password",
    help="password to use when connecting")
parser.add_option("-t", "--template", dest="template",
    help="Template to modify.")

(options, args) = parser.parse_args()

try:
  options.vcenter
except NameError:
  options.vcenter = raw_input("Enter the vCenter to connect to: ")

try:
  options.username
except NameError:
  options.username = raw_input("Enter the usename to use: ")

try:
  options.password
except NameError:
  options.password = getpass()

try:
  options.template
except NameError:
  options.template = raw_input("Enter the template to use: ")

server = VIServer()

server.connect(options.vcenter,options.username,options.password)

vm = server.get_vm_by_name(options.template)
task = vm.power_on(sync_run=False)
try:
  status = task.wait_for_state(['running', 'error'], timeout=10)
  if status == 'error':
    print "Error powering on:", task.get_error_message()
  else:
    print "Successfully powered on"
except:
  print "10 second timeout reached waiting for power to finish"

server.disconnect
