#!/usr/bin/env python

# This script will mark a template as being a virtual machine.
# The cluster, resource pool and esx host (required parameters) are set in
# the code below, not as an argument.

from pysphere import VIServer
from pysphere.resources import VimService_services as VI
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
parser.add_option("-t", "--template", dest="vm_path",
                help="Template/Virtual Machine we're changing")

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
  options.vm_path
except NameError:
  options.vm_path = raw_input("Enter the Template/VM to convert: ")

# Make the vcenter connection
server = VIServer()
server.connect(options.vcenter, options.username, options.password)

# Set the host, cluster and resource pool to "deploy" it into
# We get teh "mor" which is a number to identify with vCenter
hosts = server.get_hosts()
host = [k for k,v in hosts.items() if v=="esxhost.local"][0]
vm = server.get_vm_by_name(options.vm_path)
cluster_name = "DevTest_Cluster"
resource_pool = "/Resources"
cluster = [k for k,v in server.get_clusters().items() if v==cluster_name][0]
rpmor = [k for k,v in server.get_resource_pools(from_mor=cluster).items() if v==resource_pool][0]

# This is the request message we send off to make the change, setting the 
# vm, host, and resource pool.
request = VI.MarkAsVirtualMachineRequestMsg()
_this = request.new__this(vm._mor)
_this.set_attribute_type(vm._mor.get_attribute_type())
request.set_element__this(_this)
request.set_element_pool(rpmor)
request.set_element_host(host)
server._proxy.MarkAsVirtualMachine(request)

server.disconnect()
