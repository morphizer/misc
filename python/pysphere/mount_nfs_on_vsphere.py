#!/usr/bin/env python

# This will add an NFS datastore to vsphere
# Doesn't work well in automation, as after its created the jenkins user doesn't
# get the permissions on that new datastore to remove it. I leave it here because 
# it's still pretty cool

from pysphere import VIProperty, VIServer, VITask
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
                help="ESX host to mount the share to")

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
  options.esxhost = raw_input("Enter the ESX host to mount share to: ")


server = VIServer()
server.connect(options.vcenter, options.username, options.password)

def create_nas_store(host, access_mode, local_path, remote_host, remote_path,
                     username=None, password=None, volume_type='NFS'):

    #access_mode: 'readOnly' or 'readWrite'
    #volume_type: 'CIFS' or 'NFS' (if not set defaults to NFS)
    
    host_properties = VIProperty(server, host)
    
    hds = host_properties.configManager.datastoreSystem._obj

    request = VI.CreateNasDatastoreRequestMsg()
    _this = request.new__this(hds)
    _this.set_attribute_type(hds.get_attribute_type())
    request.set_element__this(_this)
    
    spec = request.new_spec()
    spec.set_element_accessMode(access_mode)
    spec.set_element_localPath(local_path)
    spec.set_element_remoteHost(remote_host)
    spec.set_element_remotePath(remote_path)
    if username:
        spec.set_element_userName(username)
    if password:
        spec.set_element_password(password)
    if volume_type:
        spec.set_element_type(volume_type)
    
    request.set_element_spec(spec)

    ret = server._proxy.CreateNasDatastore(request)._returnval

    task = VITask(ret, server)
    status = task.wait_for_state([task.STATE_SUCCESS,task.STATE_ERROR])
    if status == task.STATE_SUCCESS:
      print "Successfully mounted NFS share"
    elif status == task.STATE_ERROR:
      print "Error mounting NFS share: %s" % task.get_error_message()
    
hosts = server.get_hosts()

#PICK THE HOST WHERE THE NEW DATASTORE WILL BE CREATED
host = [k for k,v in hosts.items() if v == options.esxhost][0]

new_datastore_mor = create_nas_store(
                 host, 'readOnly', 'datastorename', 'nfshost.local', '/data/sharedir')

server.disconnect()
