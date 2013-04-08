#!/usr/bin/env python
# Allows for easy logging/debugging

import logging, sys

# Set the logger name (name of file)
logger = logging.getLogger(sys.argv[0])
# Set the logging level (Debug/Info)
logger.setLevel(logging.DEBUG)
# Log file output
logfilename = "/tmp/my-logfile.log"
filelog = logging.FileHandler(logfilename, 'a')
filelog.setLevel(logging.INFO)
# Use console for development logging
conlog = logging.StreamHandler()
conlog.setLevel(logging.DEBUG)
# Specify log formatting:
formatter = logging.Formatter("%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s")
conlog.setFormatter(formatter)
filelog.setFormatter(formatter)
# Add the handlers
logger.addHandler(conlog)
logger.addHandler(filelog)

# Example info message
logger.info("Testing info logging level")
# Example debug message
logger.debug("Testing debug logging level")
