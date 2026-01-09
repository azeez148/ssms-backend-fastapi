import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
LOG_DIR = "/var/log/ssms"
log_dir = LOG_DIR
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a logger
logger = logging.getLogger("ssms.api")
logger.setLevel(logging.DEBUG)

# Create a rotating file handler
log_file = os.path.join(log_dir, "api.log")
# Max 5 files of 1MB each
handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)
