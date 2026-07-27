import os
import sys

import yaml
from dotenv import load_dotenv
from backend.constants import CONFIG_YAML_PATH

# Load environment variables from .env file
load_dotenv()

# # Set default values for Redis connection
# os.environ.setdefault("REDIS_HOST", "localhost")
# os.environ.setdefault("REDIS_PORT", "6379")
# os.environ.setdefault("REDIS_DB", "0")

print("Loading config from:", CONFIG_YAML_PATH.resolve())
try:
    with open(CONFIG_YAML_PATH) as file:
        config = yaml.safe_load(os.path.expandvars(file.read()))
except Exception as e:
    print(f"Error loading configuration: {str(e)}")
    sys.exit(1)
sys.dont_write_bytecode = True
# This line is necessary to prevent the creation of .pyc files
# when running the application in development mode.
