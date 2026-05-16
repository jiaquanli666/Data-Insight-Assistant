import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

LLM_MODEL = "deepseek-chat"
EMBEDDING_MODEL = "text-embedding-v2"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

CHROMA_PERSIST_DIR = os.path.join(PROJECT_ROOT, "data", "chroma")
CHART_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "charts")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "retail.db")

os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)
