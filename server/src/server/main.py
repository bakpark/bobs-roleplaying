import os, logging
from dotenv import load_dotenv
from langsmith import traceable

# 로그 설정
logging.basicConfig(
    filename='logs/app.log',  # 로그를 저장할 파일 이름
    level=logging.INFO,   # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

