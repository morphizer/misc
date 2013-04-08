#!/usr/bin/env python
#
# Function to send events in to Zenoss monitoring
# Includes logging from "logger" snippet (commented out in here)
#
# Severity levels:
# 5: Critical
# 4: Error
# 3: Warning
# 2: Info
# 1: Debug
# 0: Clear

from xmlrpclib import ServerProxy
import sys
#import logging
def send_zenoss_event(server, component, message, severity, eventclass):
        """
        Send a WARNING event to defined instance of Zenoss
        """
        # Setup connection:
        serv = ServerProxy('http://zenoss:zenoss@test-instance:8080/zport/dmd/ZenEventManager')
        # Define the event:
        evt = {'device':server,
                'component':component,
                'summary':message,
                'severity':severity,
                'eventClass':eventclass}
        #logger.info("Sending %s event for %s to Zenoss..." % (component, server))
        try:
                serv.sendEvent(evt)
        except:
                #logger.info("%s event for %s could not be sent." % (component, server))
                sys.exit(-1)
        #logger.info("%s event for %s sent." % (component, server))

send_zenoss_event('test_device','JMX','Test event in to zenoss','3','/jmx')
