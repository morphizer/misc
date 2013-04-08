#!/usr/bin/env python

# This script will select what cdrom device to use
# client/iso/host 
# If using ISO, you can select the ISO to mount

from pysphere import VIServer, VITask
from pysphere.vi_virtual_machine import VIVirtualMachine
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
parser.add_option("-d", "--device", dest="device",
                help="Device to select. Enter either 'client' or 'host' or 'iso'")
parser.add_option("-t", "--template", dest="template",
                help="Template to modify.")
parser.add_option("-i", "--iso", dest="isofile",
                help="ISO file path. Should appear as: [datastorename] rhel5.iso")

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
  options.device
except NameError:
  options.device = raw_input("Enter the device to use (client|host|iso): ")

try:
  options.template
except NameError:
  options.template = raw_input("Enter the template to use: ")

if options.device == "iso":
  try:
    options.isofile
  except NameError:
    options.isofile = raw_input("Enter the iso file to use (e.g. [datastorename] rhel5.iso): ")

def change_cdrom_type(dev, dev_type, value=""):
    if dev_type == "ISO":
        iso = VI.ns0.VirtualCdromIsoBackingInfo_Def("iso").pyclass()
        iso.set_element_fileName(value)
        dev.set_element_backing(iso)
    elif dev_type == "HOST DEVICE":
        host = VI.ns0.VirtualCdromAtapiBackingInfo_Def("host").pyclass()
        host.set_element_deviceName(value)
        dev.set_element_backing(host)
    elif dev_type == "CLIENT DEVICE":
        client = VI.ns0.VirtualCdromRemoteAtapiBackingInfo_Def("client").pyclass()
        client.set_element_deviceName("")
        dev.set_element_backing(client)

def get_valid_host_devices(vm):
    env_browser = vm.properties.environmentBrowser._obj
    request = VI.QueryConfigTargetRequestMsg()
    _this = request.new__this(env_browser)
    _this.set_attribute_type(env_browser.get_attribute_type())
    request.set_element__this(_this)
    ret = server._proxy.QueryConfigTarget(request)._returnval
    return [cd.Name for cd in ret.CdRom]

def apply_changes(vm, cdrom):
    request = VI.ReconfigVM_TaskRequestMsg()
    _this = request.new__this(vm._mor)
    _this.set_attribute_type(vm._mor.get_attribute_type())
    request.set_element__this(_this)
    spec = request.new_spec()

    dev_change = spec.new_deviceChange()
    dev_change.set_element_device(cdrom)
    dev_change.set_element_operation("edit")

    spec.set_element_deviceChange([dev_change])
    request.set_element_spec(spec)
    ret = server._proxy.ReconfigVM_Task(request)._returnval

    task = VITask(ret, server)
    status = task.wait_for_state([task.STATE_SUCCESS,task.STATE_ERROR])
    if status == task.STATE_SUCCESS:
        print "%s: successfully reconfigured" % vm.properties.name
    elif status == task.STATE_ERROR:
        print "%s: Error reconfiguring vm"% vm.properties.name
        print "%s" % task.get_error_message()

server = VIServer()

server.connect(options.vcenter,options.username,options.password)

vm = server.get_vm_by_name(options.template)

cdrom = None
for dev in vm.properties.config.hardware.device:
    if dev._type == "VirtualCdrom":
        cdrom = dev._obj
        break

if options.device == "iso":
  # ISO
  change_cdrom_type(cdrom, "ISO", options.isofile)
  # Set it to connected. This finds cdrom drive that is set to not start connected
  for dev in vm.properties.config.hardware.device:
    if dev._type == "VirtualCdrom" and not dev.connectable.startConnected:
      d = dev._obj
      d.Connectable.set_element_startConnected(True)
      request = VI.ReconfigVM_TaskRequestMsg()
      _this = request.new__this(vm._mor)
      _this.set_attribute_type(vm._mor.get_attribute_type())
      request.set_element__this(_this)
      spec = request.new_spec()
      dev_change = spec.new_deviceChange()
      dev_change.set_element_device(d)
      dev_change.set_element_operation("edit")
      spec.set_element_deviceChange([dev_change])
      request.set_element_spec(spec)
      ret = server._proxy.ReconfigVM_Task(request)._returnval

      task = VITask(ret, server)
      status = task.wait_for_state([task.STATE_SUCCESS,task.STATE_ERROR])
      if status == task.STATE_SUCCESS:
        print "%s: successfully reconfigured" % vm.properties.name
      elif status == task.STATE_ERROR:
        print "%s: Error reconfiguring vm" % vm.properties.name
        print "%s" % task.get_error_message()
elif options.device == "host":
  #HOST DEVICE: hardcoded to use the first valid host device
  valid_host_device = get_valid_host_devices(vm)[0]
  change_cdrom_type(cdrom, "HOST DEVICE", valid_host_device)
elif options.device == "client":
  #CLIENT DEVICE
  change_cdrom_type(cdrom, "CLIENT DEVICE")

apply_changes(vm, cdrom)

server.disconnect()
