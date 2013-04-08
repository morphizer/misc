#!/usr/bin/env python
from pysphere import VIProperty, VIServer
from pysphere.resources import VimService_services as VI
from optparse import OptionParser
from getpass import getpass
import time

# Parameters
usage = "usage: %prop [options]"
parser = OptionParser(usage=usage)
parser.add_option("-s", "--server", dest="vcenter",
                help="set the vCenter server to connect to")
parser.add_option("-u", "--user", dest="username",
                help="set the user to connect as")
parser.add_option("-p", "--password", dest="password",
                help="password to use when connecting")
parser.add_option("-e", "--esxhost", dest="esxhost",
                help="ESX host to remove the share from")

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
  options.esxhost
except NameError:
  options.esxhost = raw_input("Enter the ESX host to remove the share from: ")


datastore_name = "datastorename"

server = VIServer()
server.connect(options.vcenter,options.username,options.password)

host_mor = [k for k,v in server.get_hosts().items() if v==options.esxhost][0]
ds_mor = [k for k,v in server.get_datastores().items() if v==datastore_name][0]

host = VIProperty(server, host_mor)

ds_system = host.configManager.datastoreSystem._obj

request = VI.RemoveDatastoreRequestMsg()
_this = request.new__this(ds_system)
_this.set_attribute_type(ds_system.get_attribute_type())
request.set_element__this(_this)
request.Datastore = ds_mor

server._proxy.RemoveDatastore(request)
server.disconnect()
