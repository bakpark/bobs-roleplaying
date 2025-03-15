import logging
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

log_dir = os.getenv(
    "LOG_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
)
os.makedirs(log_dir, exist_ok=True)

# 현재 시각으로 로그 파일명 설정
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = os.path.join(log_dir, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_filepath)],
)

logger = logging.getLogger(__name__)
