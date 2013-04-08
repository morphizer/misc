#!/usr/bin/env python
from xmlrpclib import ServerProxy
import logging, sys, signal, subprocess, datetime, os, time

# Setup logging (info to file, debug to console)
logger = logging.getLogger(sys.argv[0])
logger.setLevel(logging.INFO)
#file output
logfilename = "/tmp/nfscheck.log"
filelog = logging.FileHandler(logfilename, 'a')
filelog.setLevel(logging.INFO)
# Use console for development logging:
conlog = logging.StreamHandler()
conlog.setLevel(logging.DEBUG)
# Specify log formatting:
formatter = logging.Formatter("%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s")
conlog.setFormatter(formatter)
filelog.setFormatter(formatter)
# Add console log to logger
logger.addHandler(conlog)
logger.addHandler(filelog)
# Configuration Settings
hostname = subprocess.Popen(["hostname"], stdout=subprocess.PIPE)
hostname.out = hostname.communicate()[0]
hostname.out = hostname.out.rstrip()
logger.debug("Hostname/Device: %s" % hostname.out)

# Function to send events to Zenoss
def send_zenoss_event(server, component, message, severity, eventclass):
        """
        Send a WARNING event to defined instance of Zenoss
        """
        # Setup connection:
        serv = ServerProxy('zenoss:zenoss@zenoss:8080/zport/dmd/ZenEventManager')
        # Define the event:
        evt = {'device':server,
                'component':component,
                'summary':message,
                'severity':severity,
                'eventClass':eventclass}
        logger.info("Sending %s event for %s to Zenoss..." % (component, server))
        try:
                serv.sendEvent(evt)
        except:
                logger.info("%s event for %s could not be sent." % (component, server))
                sys.exit(-1)
        logger.info("%s event for %s sent." % (component, server))

# Command timeout function
def timeout_command(command, timeout):
    """call shell-command and either return log message or if
	it times out, return a zenoss event"""
    start = datetime.datetime.now()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:
        time.sleep(0.1)
        now = datetime.datetime.now()
        if (now - start).seconds> timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return send_zenoss_event('%s' % hostname.out,'NFS','Mount point at %s is unavailable. Please investigate' % mount[1],'5','/nfs')
    return logger.info("Mount point %s is available." % mount[1])


# Now do the check!
fstab = open("/etc/fstab")
for line in fstab:
  # get the mount points
  if "nfs4" in line:
    mount = line.split()
    timeout_command(["stat", "-t", "%s" % mount[1]], 5)
fstab.close()
