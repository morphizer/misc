#!/usr/bin/env python

# This script will configure the network on a selected virtual machine
# You can give the -n flag to set it to null, otherwise it sets to vlan 7

from pysphere import VIServer, VITask
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
parser.add_option("-n", "--null", action="store_true", dest="null",
                help="Use this flag to make the network vNull")

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
  options.vm_path = raw_input("Enter the VM to change: ")

# Make the vcenter connection
server = VIServer()
server.connect(options.vcenter, options.username, options.password)

# The VM object we will be changing
vm = server.get_vm_by_name(options.vm_path)

if not vm:
  raise Exception("VM %s not found" % vm)

# Find the virtual nic device, and then set it to the label we specified from parameters

def change_dvs_net(server, vm_obj, pg_map):
    """Takes a VIServer and VIVirtualMachine object and reconfigures
    dVS portgroups according to the mappings in the pg_map dict. The
    pg_map dict must contain the source portgroup as key and the
    destination portgroup as value"""
    # Find virtual NIC devices
    if vm_obj:
        net_device = []
        for dev in vm_obj.properties.config.hardware.device:
            if dev._type in ["VirtualE1000", "VirtualE1000e",
                            "VirtualPCNet32", "VirtualVmxnet",
                            "VirtualNmxnet2", "VirtualVmxnet3"]:
                net_device.append(dev)

    # Throw an exception if there is no NIC found
    if len(net_device) == 0:
        raise Exception("The vm seems to lack a Virtual Nic")

    # Use pg_map to set the new Portgroups
    for dev in net_device:
        old_portgroup = dev.backing.port.portgroupKey
        if pg_map.has_key(old_portgroup):
            dev.backing.port._obj.set_element_portgroupKey(
                pg_map[old_portgroup])
            dev.backing.port._obj.set_element_portKey('')

    # Invoke ReconfigVM_Task
    request = VI.ReconfigVM_TaskRequestMsg()
    _this = request.new__this(vm_obj._mor)
    _this.set_attribute_type(vm_obj._mor.get_attribute_type())
    request.set_element__this(_this)

    # Build a list of device change spec objects
    devs_changed = []
    for dev in net_device:
        spec = request.new_spec()
        dev_change = spec.new_deviceChange()
        dev_change.set_element_device(dev._obj)
        dev_change.set_element_operation("edit")
        devs_changed.append(dev_change)

    # Submit the device change list
    spec.set_element_deviceChange(devs_changed)
    request.set_element_spec(spec)
    ret = server._proxy.ReconfigVM_Task(request)._returnval

    # Wait for the task to finish
    task = VITask(ret, server)

    status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
    if status == task.STATE_SUCCESS:
        print "VM %s successfully reconfigured" % vm_obj
    elif status == task.STATE_ERROR:
        print "Error reconfiguring vm: %s" % vm_obj, task.get_error_message()
    else:
        print "VM %s not found" % vm_obj

if options.null:
  # If the null flag is set, this will change the network to vNull
  pg_map = {'dvportgroup-54116' : 'dvportgroup-54531'}
else:
  # Otherwise we set it to VLAN_7
  pg_map = {'dvportgroup-54531' : 'dvportgroup-54116'}

change_dvs_net(server, vm, pg_map)

server.disconnect()
