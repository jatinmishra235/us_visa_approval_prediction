import logging
import os
import from_root
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.log"

logs_dir = 'logs'

logs_path = os.path.join(os.getcwd(),logs_dir,LOG_FILE)

os.makedirs(logs_dir,exist_ok=True)

logging.basicConfig(filename=logs_path,format='[ %(asctime)s ] - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
